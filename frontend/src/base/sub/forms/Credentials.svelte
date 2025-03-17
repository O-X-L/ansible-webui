<script lang="ts">
    import { fade } from 'svelte/transition';

    import {
        FolderSolid, FileSolid, CloseCircleSolid, TrashBinSolid, FloppyDiskSolid, CirclePlusSolid,
    } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Modal, Input, Label, Helper, Toggle, Select, Spinner, Alert, Tooltip,
        AccordionItem, Accordion,
    } from 'flowbite-svelte';

    import { share } from '../../State.js';
    import { apiGet } from '../../../util/api.js';
    import { tq } from '../../../util/translate.js';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalForm, classModalInputDiv, classModalInput,
    } from '../../Style.js';

    // todo: reset to default if 'add' form gets closed
    let { open = $bindable(false), action = 'add', existingID = null, global = false } = $props();

    const formErrorAlert = 'form-job-alert';
    const urlExisting = `credentials/${existingID}?global=${global}`;

    let formInfos = $state({});
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? `credentials?global=${global}` : urlExisting);
    let title = $derived(actionNew ? t('creds.new') : t('creds.edit'));
    let formError = $state('');

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        connect_user: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        become_user: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        vault_file: {value: '', color: inputBaseColor, required: false, regex: /^.{0,300}/},
        vault_id: {value: '', color: inputBaseColor, required: false, regex: /^.{0,50}/},
        vault_pass: {value: '', color: inputBaseColor, required: false, regex: /^.{0,300}/},
        become_pass: {value: '', color: inputBaseColor, required: false, regex: /^.{0,300}/},
        connect_pass: {value: '', color: inputBaseColor, required: false, regex: /^.{0,300}/},
        ssh_key: {value: '', color: inputBaseColor, required: false, regex: /^.{0,3000}/},
        category: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
    });

    function t(code: string) {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            open = false;
        } else {
            formError = `${j.error} (${s})`;
            let a = document.getElementById(formErrorAlert);
            if (a) {
                a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            }
        }
    }

    function submitForm() {
        submitFormBase(form, method, url, handleSubmitResponse);
    }

    function setFormInfos(j: any) {
        formInfos = j;
        if (action == 'add') {
            for (let [k, v] of Object.entries(formInfos.defaults)) {
                if (form[k]) {
                    form[k].value = v;
                }
            }
            loaded = true;
        }
    }

    function loadExisting(j: any) {
        existing = j;
        if (action == 'clone') {
            existing.name = `${existing.name} - Copy`;
        }
        for (let [k, v] of Object.entries(existing)) {
            if (form[k]) {
                form[k].value = v;
            }
        }
        loaded = true;
    }

    $effect(() => {
        if (!open || loaded) {
            return;
        }
        apiGet('frontend/form/credentials', setFormInfos);

        if (action != 'add' && existingID) {
            apiGet(urlExisting, loadExisting);
        }
    })
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{title}</Heading>
    {#if !loaded}
        <Spinner/>
    {:else}
        <div id={formErrorAlert} class="h-0"></div>
        {#if formError}
            <div transition:fade>
                <Alert border color="red" class="text-wrap">
                    <CloseCircleSolid slot="icon" class="w-5 h-5" /> {formError}
                </Alert>
            </div>
        {/if}
        <Accordion class={classModalForm}>
            <AccordionItem>
                <span slot="header">Main</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_name" class={classModalLabel}>{t('jobs.form.name')}</Label>
                        <Input id="job_name" bind:value={form.name.value} bind:color={form.name.color}
                        on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                    </div>
                </div>
            </AccordionItem>
        </Accordion>

        <div class={classModalBtns}>
            <Button type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
    {/if}
</Modal>
