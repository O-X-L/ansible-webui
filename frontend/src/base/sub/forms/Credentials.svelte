<script lang="ts">
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Modal, Input, Label, Spinner, Tooltip, Helper,
        AccordionItem, Accordion,
    } from 'flowbite-svelte';

    import { share } from '../../State.js';
    import { apiGet } from '../../../util/api.js';
    import { tq } from '../../../util/translate.js';
    import { type formInfoType } from '../../Types.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalForm, classModalInputDiv,
        classModalInput, classModalHelp, classSpinnerDiv,
    } from '../../Style.js';

    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
        shared = false,
    } = $props();

    const urlExisting = `credentials/${existingID}?shared=${shared}`;

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? `credentials?shared=${shared}` : urlExisting);
    let title = $derived(actionNew ? t('creds.new') : t('creds.edit'));

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

    function t(code: string) : string {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'creds.action.create' : 'creds.action.update';
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
        apiGet('frontend/form/credentials', setFormInfos);

        if (action != 'add' && existingID) {
            apiGet(urlExisting, loadExisting);
        }
    })
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{title}</Heading>
    {#if !loaded}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <APIResponseHandler bind:this={apiResponseHandler} />

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="creds_name" class={classModalLabel}>{t('common.name')}</Label>
                <Input id="creds_name" bind:value={form.name.value} bind:color={form.name.color}
                    on:input={valideInput} on:blur={valideInput} required={form.name.required} />
            </div>
            {#if !shared}
                <div class={classModalInput}>
                    <Label for="creds_cat" class={classModalLabel}>{t('creds.form.category')}</Label>
                    <Input id="creds_cat" bind:value={form.category.value} bind:color={form.category.color}
                        on:input={valideInput} on:blur={valideInput} />
                    <Helper class={classModalHelp}>{t('creds.form.help.category')}</Helper>
                </div>
            {/if}
        </div>

        <Accordion class={classModalForm}>
            <AccordionItem>
                <span slot="header">{t('creds.form.accounts')}</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="creds_conn_user" class={classModalLabel}>{t('creds.form.connect_user')}</Label>
                        <Input id="creds_conn_user" bind:value={form.connect_user.value} bind:color={form.connect_user.color}
                            on:input={valideInput} on:blur={valideInput} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="creds_conn_pwd" class={classModalLabel}>{t('creds.form.connect_pwd')}</Label>
                        <Input id="creds_conn_pwd" bind:value={form.connect_pass.value} bind:color={form.connect_pass.color}
                            on:input={valideInput} on:blur={valideInput} type="password" />
                    </div>
                    <div class={classModalInput}>
                        <Label for="creds_ssh_key" class={classModalLabel}>{t('creds.form.ssh_key')}</Label>
                        <Input id="creds_ssh_key" bind:value={form.ssh_key.value} bind:color={form.ssh_key.color}
                            on:input={valideInput} on:blur={valideInput} type="password" />
                        <Helper class={classModalHelp}>{t('creds.form.help.ssh_key')}</Helper>
                    </div>

                    <div class={classModalInput}>
                        <Label for="creds_bec_user" class={classModalLabel}>{t('creds.form.become_user')}</Label>
                        <Input id="creds_bec_user" bind:value={form.become_user.value} bind:color={form.become_user.color}
                            on:input={valideInput} on:blur={valideInput} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="creds_bec_pwd" class={classModalLabel}>{t('creds.form.become_pwd')}</Label>
                        <Input id="creds_bec_pwd" bind:value={form.become_pass.value} bind:color={form.become_pass.color}
                            on:input={valideInput} on:blur={valideInput} type="password" />
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">{t('creds.form.vault')}</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="creds_vault_pass" class={classModalLabel}>{t('creds.form.vault_pwd')}</Label>
                        <Input id="creds_vault_pass" bind:value={form.vault_pass.value} bind:color={form.vault_pass.color}
                            on:input={valideInput} on:blur={valideInput} type="password" />
                    </div>
                    <div class={classModalInput}>
                        <Label for="creds_vault_file" class={classModalLabel}>{t('creds.form.vault_file')}</Label>
                        <Input id="creds_vault_file" bind:value={form.vault_file.value} bind:color={form.vault_file.color}
                            on:input={valideInput} on:blur={valideInput} />
                        <Helper class={classModalHelp}>{t('creds.form.help.vault_file')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="creds_vault_id" class={classModalLabel}>{t('creds.form.vault_id')}</Label>
                        <Input id="creds_vault_id" bind:value={form.vault_id.value} bind:color={form.vault_id.color}
                            on:input={valideInput} on:blur={valideInput} />
                        <Helper class={classModalHelp}>{@html t('creds.form.help.vault_id')}</Helper>
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
