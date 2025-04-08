<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { TrashBinSolid, CloseCircleSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Heading, Label, Input,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { clickToCopy } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing, classModalBackdrop,
        classModalLabel, classModalForm, classModalInput, classModalBtns,
     } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let newModal = $state(false);
    let newLoad = $state(false);

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
        apiGet(`key?hash=${apiDataHash}`, loadApiKeyList);
    }

    $effect(() => {
        if (!newModal) {
            newKeyPair = EMPTY_KEYPAIR;
        }
    });

    onMount(() => {
        buildUpdateAPIKeyList();
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateAPIKeyList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg} />

<div>
    <Table striped={true} bind:items={entryList} hoverable={true} shadow placeholder={t('common.search')}
        filter={(item, searchTerm) => (searchFilter(item, searchTerm))}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell sort={(a, b) => a.token.localeCompare(b.token)} defaultSort>
            {t('api_keys.token')}
        </TableHeadCell>
        <TableHeadCell sort={(a, b) => a.comment.localeCompare(b.comment)}>
            {t('common.comment')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass={classListContent}>{item.token}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>{item.comment ? item.comment : '-'}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>
                <Button size="xs" on:click={() => {deleteAPIKey(item.token)}}><TrashBinSolid/></Button>
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

<Modal bind:open={newModal} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('api_keys.new')}</Heading>

        {#if newLoad}
            <div class={classSpinnerDiv}><Spinner/></div>
        {:else if !newKeyPair.token}
            <div class={classModalInput}>
                <Label for="api_key_cmt" class={classModalLabel}>{t('common.comment')}</Label>
                <Input id="api_key_cmt" bind:value={newKeyPair.comment} />
            </div>
            <div class="flex justify-between">
                <div></div>
                <div class="mr-5 mt-10">
                    <Button id="apikeys-btn-add-submit" on:click={() => {addAPIKey()}}>{t('btn.add')}</Button>
                </div>
            </div>
        {:else}
            <Label class={classModalLabel}>{t('api_keys.token')}</Label>
            <button onclick={clickToCopy}>{newKeyPair.token}</button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>

            <Label class={classModalLabel}>{t('api_keys.key')}</Label>
            <button onclick={clickToCopy}>{newKeyPair.key}</button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>
        {/if}

        <div class={classModalBtns}>
            <Button id="apikeys-btn-add-close" on:click={() => (newModal = false)} class="inline-block ml-2">
                <CloseCircleSolid/>
            </Button>
            <Tooltip>{t('btn.close')}</Tooltip>
        </div>
    </div>
</Modal>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
