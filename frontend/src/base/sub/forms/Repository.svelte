<script lang="ts">
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Modal, Input, Label, Spinner, Tooltip,
        AccordionItem, Accordion,
    } from 'flowbite-svelte';

    import { share } from '../../State.js';
    import { apiGet } from '../../../util/api.js';
    import { tq } from '../../../util/translate.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalForm, classModalInputDiv, classModalInput,
    } from '../../Style.js';

    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
    } = $props();

    const urlExisting = `repository/${existingID}`;

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos = $state({});
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? 'repository' : urlExisting);
    let title = $derived(actionNew ? t('repos.new') : t('repos.edit'));

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
        user: {value: $share.backend.user_id},
    });

    function t(code: string) {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'repos.action.create' : 'repos.action.update';
            success = true;
            open = false;
        } else {
            apiResponseHandler.handleRes(s, j);
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
        apiGet('frontend/form/repository', setFormInfos);

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
        <APIResponseHandler bind:this={apiResponseHandler} />

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="repo_name" class={classModalLabel}>{t('common.name')}</Label>
                <Input id="repo_name" bind:value={form.name.value} bind:color={form.name.color}
                on:input={valideInput} on:blur={valideInput} required={form.name.required} />
            </div>
        </div>

        <Accordion class={classModalForm}>
            <AccordionItem>
                <span slot="header">{t('repos.form.xxx')}</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="repos_xxx" class={classModalLabel}>{t('repos.form.xxx')}</Label>
                        <Input id="repos_xxx" bind:value={form.connect_user.value} bind:color={form.connect_user.color}
                        on:input={valideInput} on:blur={valideInput} />
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
