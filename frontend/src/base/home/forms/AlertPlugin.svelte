<script lang="ts">
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Spinner, Tooltip, Helper,
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { apiGet } from '../../../util/api.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalInputDiv,
        classModalInput, classModalHelp, classSpinnerDiv,
    } from '../../Style.js';

    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
    } = $props();

    const urlBase = 'alert/plugin';
    const urlExisting = `${urlBase}/${existingID}`;

    let apiResponseHandler: APIResponseHandler = $state();
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? urlBase : urlExisting);
    let title = $derived(actionNew ? t('alerts.plugin.new') : t('alerts.plugin.edit'));
    let formWarningMsgs: string[] = $state([]);

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        executable: {value: '', color: inputBaseColor, required: true, regex: /^.{1,300}/},
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'alerts.plugin.action.create' : 'alerts.plugin.action.update';
            success = true;
            open = false;
        } else {
            apiResponseHandler.handleRes(s, j);
        }
    }

    function submitForm() {
        let [valid, errors] = submitFormBase(
            form, method, url, handleSubmitResponse, t, 'alerts.form.plugin.',
        );
        if (!valid) {
            formWarningMsgs = errors;
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

    function fetchBuild() {
        if (action != 'add' && existingID) {
            apiGet(urlExisting, loadExisting);
        } else {
            loaded = true;
        }
    }

    $effect(() => {
        if (!open || loaded) {
            return;
        }
        fetchBuild();
    })
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{title}</Heading>
    {#if !loaded}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <APIResponseHandler bind:this={apiResponseHandler} bind:warningMsgs={formWarningMsgs} />
        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="plugin_name" class={classModalLabel}>{t('common.name')}</Label>
                <Input id="plugin_name" bind:value={form.name.value} bind:color={form.name.color}
                    on:input={valideInput} on:blur={valideInput} required={form.name.required} />
            </div>
            <div class={classModalInput}>
                <Label for="plugin_exe" class={classModalLabel}>{t('alerts.form.plugin.executable')}</Label>
                <Input id="plugin_exe" bind:value={form.executable.value} bind:color={form.executable.color}
                    on:input={valideInput} on:blur={valideInput} required={form.executable.required} />
                <Helper class={classModalHelp}>{@html t('alerts.form.help.plugin.executable')}</Helper>
            </div>
        </div>

        <div class={classModalBtns}>
            <Button id="plugin-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button id="plugin-btn-discard" on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
    {/if}
</Modal>
