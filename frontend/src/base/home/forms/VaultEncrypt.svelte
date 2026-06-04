<script lang="ts">
    import {
        CloseCircleSolid, PlaySolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip,
        Heading, Label, Input, Helper,
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { clickToCopy } from '../../../util/main.js';
    import { apiEdit } from '../../../util/api.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv,
        classModalBackdrop, classModalBody, classModalForm, classModalInput,
        classModalHelp, classModalBtns, classModalLabel, classModalDialog,
    } from '../../Style.js';
 
    let {
        open = $bindable(false),
        credsKind = $bindable(''),
        credsID = $bindable(0),
        apiResponseHandler = $bindable(null),
        apiSuccessMsg = $bindable(''),
        apiSuccess = $bindable(false),
    } : {
        open: boolean,
        credsKind: string,
        credsID: number,
        apiResponseHandler: APIResponseHandler,
        apiSuccessMsg: string,
        apiSuccess: boolean,
    } = $props();

    let newVaultPlaintext = $state('');
    let newVaultCiphertext = $state('');
    let newVaultLoad = $state(false);

    function t(code: string) : string {
        return tq($share, code);
    }

    function vaultEncryptPlaintext() {
        newVaultLoad = true;
        apiEdit(
            'post',
            `credentials/${credsKind}/${credsID}/vault_encrypt`,
            {plaintext: newVaultPlaintext},
            handleVaultEncryptSubmitResponse,
        );
    }

    function resetState() {
        newVaultCiphertext = '';
        newVaultPlaintext = '';
        newVaultLoad = false;
    }

    function close() {
        resetState();
        open = false;
    }

    function handleVaultEncryptSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            newVaultCiphertext = j.ciphertext;
            apiSuccessMsg = 'creds.action.vault_encrypt';
            apiSuccess = true;
            newVaultLoad = false;
        }
        apiResponseHandler.handleRes(s, j);
    }

    $effect(() => {
        if (open) {
            resetState();
        }
    });
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('creds.vault_encrypt')}</Heading>

        {#if newVaultLoad}
            <div class={classSpinnerDiv}><Spinner/></div>
        {:else if !newVaultCiphertext}
            <div class={classModalInput}>
                <Label for="creds_vaultencrypt_plaintext" class={classModalLabel}>{t('creds.form.vault_encrypt')}</Label>
                <Input id="creds_vaultencrypt_plaintext" bind:value={newVaultPlaintext} />
                <Helper class={classModalHelp}>{@html t('creds.form.help.vault_encrypt')}</Helper>
            </div>
            <div class={classModalBtns}>
                <Button id="creds-btn-vaultencrypt-submit" on:click={() => {vaultEncryptPlaintext()}}><PlaySolid/></Button>
                <Tooltip>{t('btn.encrypt')}</Tooltip>

                <Button id="creds-btn-vaultencrypt-close" on:click={close} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {:else}
            <Label class={classModalLabel}>{t('api_keys.token')}</Label>
            <button onclick={clickToCopy} class="mr-10">
<pre class="whitespace-pre-wrap break-normal text-xs">
{newVaultCiphertext}
</pre>
            </button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>

            <div class={classModalBtns}>
                <Button id="creds-btn-vaultencrypt-close" on:click={close} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {/if}
    </div>
</Modal>