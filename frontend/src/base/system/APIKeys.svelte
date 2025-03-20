<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { TrashBinSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Modal, Heading, Label,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { clickToCopy } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing, classModalBackdrop,
        classModalLabel, classModalForm,
     } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let newModal = $state(false);

    interface apiToken {
        token: string
        comment: string|null  // todo: allow to 
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

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            newModal = true;
            newKeyPair = j;
        }
        apiResponseHandler.handleRes(s, j);
    }

    function addAPIKey() {
        apiSuccessMsg = 'api_keys.action.create';
        apiEdit('post', 'key', null, handleSubmitResponse);
    }

    function deleteAPIKey(toke: string) {
        if (!toke) {
            return;
        }
        apiSuccessMsg = 'api_keys.action.delete';
        apiEdit('delete', `key/${toke}`, null, apiResponseHandler.handleRes);
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
    <Table striped={true} bind:items={entryList} hoverable={true} placeholder={t('common.search')}
        filter={(item, searchTerm) => (item.token.toLowerCase().includes(searchTerm.toLowerCase()))}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell sort={(a, b) => a.token.localeCompare(b.token)} defaultSort>
            {t('api_keys.token')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass={classListContent}>{item.token}</TableBodyCell>
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
        <Button on:click={() => {addAPIKey()}}>{t('btn.add')}</Button>
    </div>    
</div>

<Modal bind:open={newModal} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('api_keys.new')}</Heading>

        <Label class={classModalLabel}>{t('api_keys.token')}</Label>
        <button onclick={clickToCopy}>{newKeyPair.token}</button>
        <Tooltip>{t('common.click_to_copy')}</Tooltip>

        <Label class={classModalLabel}>{t('api_keys.key')}</Label>
        <button onclick={clickToCopy}>{newKeyPair.key}</button>
        <Tooltip>{t('common.click_to_copy')}</Tooltip>
    </div>
</Modal>

<div class={classFooterSpacing}></div>
