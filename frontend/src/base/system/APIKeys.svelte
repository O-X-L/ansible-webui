<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { TrashBinSolid, CloseCircleSolid, CirclePlusSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Heading, Label, Input,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { clickToCopy } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import ConfirmActionPrompt from '../home/forms/ConfirmAction.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing, classModalBackdrop,
        classModalLabel, classModalForm, classModalInput, classModalBtns, classModalBody, classModalDialog,
    } from '../Style.js';
 
    let componentRoot;
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let newModal = $state(false);
    let newLoad = $state(false);
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

    interface apiToken {
        token: string
        comment: string|null
    }
    interface apiKeyPair extends apiToken {
        key: string
    }

    const EMPTY_KEYPAIR = {token: '', key: '', comment: ''};
    let entryList: apiToken[] = $state([]);
    let newKeyPair: apiKeyPair = $state(EMPTY_KEYPAIR);

    function t(code: string) : string {
        return tq($share, code);
    }

    function searchFilter(item: apiToken, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let c = item.comment ? item.comment : '';
        return (
            item.token.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s)
        )
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            newKeyPair = j;
            newLoad = false;
        }
        apiResponseHandler.handleRes(s, j);
    }

    function addAPIKey() {
        newLoad = true;
        apiSuccessMsg = 'api_keys.action.create';
        apiEdit('post', 'key', {comment: newKeyPair.comment}, handleSubmitResponse);
    }

    function deleteAPIKey(token: string) {
        if (!token) {
            return;
        }
        apiSuccessMsg = 'api_keys.action.delete';
        apiEdit('delete', `key/${token}`, null, apiResponseHandler.handleRes);
    }

    function loadApiKeyList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        entryList = j;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function buildUpdateAPIKeyList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (newModal) {
            // user currently adding entry
            return;
        }
        apiGet(`key?hash=${apiDataHash}`, loadApiKeyList);
    }

    $effect(() => {
        if (!newModal) {
            newKeyPair = EMPTY_KEYPAIR;
        }
    });

   // ALT+S quick-save
   function handleKeyUp(e: KeyboardEvent) {
        switch (e.key) {
        case 'Alt':
            pressedKeyAlt = false;
            break;
        case 's':
        case 'S':
            pressedKeyS = false;
            break;
        default:
            return;
        }
    }
    
    function handleKeyDown(e: KeyboardEvent) {
        switch (e.key) {
        case 'Alt':
            pressedKeyAlt = true;
            break;
        case 's':
        case 'S':
            pressedKeyS = true;
            break;
        default:
            return;
        }
    }

    $effect(() => {
        if (open && componentRoot) {
            componentRoot.focus();
        }
    });

    $effect(() => {
        if (pressedKeyAlt && pressedKeyS) {
            addAPIKey();
        }
    });

    // action confirmation-prompt
    let confirmAction: string = $state('btn.delete');
    let confirmActionOpen: boolean = $state(false);
    let confirmActionProceed: boolean = $state(false);
    let confirmActionText: string = $state('');
    let confirmActionHoldEntryID: string = $state('');

    function confirmDeleteAPIKey(token: string) {
        confirmActionProceed = false;
        confirmActionHoldEntryID = token;
        confirmAction = 'btn.delete';
        confirmActionText = `${t('api_keys.token')} "${token}"`;
        confirmActionOpen = true;
    }

    function checkActionConfirmed() {
        if (!confirmActionProceed || confirmActionHoldEntryID == '') {
            return;
        }
        if (confirmAction == 'btn.delete') {
            deleteAPIKey(confirmActionHoldEntryID);
        }
    }

    $effect(() => {
        if (!confirmActionOpen) {
            checkActionConfirmed();
        }
    });

    onMount(() => {
        buildUpdateAPIKeyList();

        if (componentRoot) {
            componentRoot.addEventListener('keyup', handleKeyUp);
            componentRoot.addEventListener('keydown', handleKeyDown);
        }
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateAPIKeyList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
        if (componentRoot) {
            componentRoot.removeEventListener('keyup', handleKeyUp);
            componentRoot.removeEventListener('keydown', handleKeyDown);
        }
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg} />

<div>
    <Table striped={true} bind:items={entryList} hoverable={true} shadow placeholder={t('common.search')}
        filter={(item, searchTerm) => (searchFilter(item, searchTerm))}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell class="max-sm:hidden" sort={(a, b) => a.token.localeCompare(b.token)}>
            {t('api_keys.token')}
        </TableHeadCell>
        <TableHeadCell sort={(a, b) => a.comment.localeCompare(b.comment)} defaultSort>
            {t('common.comment')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass="{classListContent} max-sm:hidden">{item.token}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>{item.comment ? item.comment : '-'}</TableBodyCell>
            <TableBodyCell tdClass="{classListContent} action-btns">
                <Button size="xs" on:click={() => {confirmDeleteAPIKey(item.token)}}><TrashBinSolid/></Button>
                <Tooltip>{t('btn.delete')}</Tooltip>
            </TableBodyCell>
        </TableBodyRow>
    </TableBody>
    {/key}
  </Table>
  {#if !entryList.length}
      <div class={classSpinnerDiv}><Spinner/></div>
  {/if}
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button id="apikeys-btn-add" on:click={() => {newModal = true}}>{t('btn.add')}</Button>
    </div>
</div>

<div bind:this={componentRoot} tabindex="-1" class="inline-block">
<Modal bind:open={newModal} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('api_keys.new')}</Heading>

        {#if newLoad}
            <div class={classSpinnerDiv}><Spinner/></div>
        {:else if !newKeyPair.token}
            <div class={classModalInput}>
                <Label for="api_key_cmt" class={classModalLabel}>{t('common.comment')}</Label>
                <Input id="api_key_cmt" bind:value={newKeyPair.comment} />
            </div>
            <div class={classModalBtns}>
                <Button id="apikeys-btn-add-submit" on:click={() => {addAPIKey()}}><CirclePlusSolid/></Button>
                <Tooltip>{t('btn.add')}</Tooltip>

                <Button id="apikeys-btn-add-close" on:click={() => (newModal = false)} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {:else}
            <Label class={classModalLabel}>{t('api_keys.token')}</Label>
            <button onclick={clickToCopy}>{newKeyPair.token}</button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>

            <Label class={classModalLabel}>{t('api_keys.key')}</Label>
            <button onclick={clickToCopy}>{newKeyPair.key}</button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>

            <div class={classModalBtns}>
                <Button id="apikeys-btn-add-close" on:click={() => (newModal = false)} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {/if}
    </div>
</Modal>
</div>

{#key confirmActionHoldEntryID}
    <ConfirmActionPrompt bind:open={confirmActionOpen} bind:action={confirmAction}
        bind:confirmed={confirmActionProceed} bind:confirmText={confirmActionText}
    />
{/key}

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
