<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { TrashBinSolid, CloseCircleSolid, RefreshOutline, PlaySolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Heading, Label, Input, Helper,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classListHeader, classListContent, classFooterSpacing, classModalBackdrop, classModalHelp, classSpinnerDiv,
        classModalLabel, classModalForm, classModalInput, classModalBtns, classModalBody, classModalDialog,
    } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let scanModal = $state(false);
    let scanLoading = $state(false);

    interface sshHostkeyScan {
        target: string
        port: number
        file: string
        comment: string
    }
    interface sshHostKey {
        host: string
        comment: string
        hostkeys: string[]
        file: string
    }

    const EMPTY_SCAN_ARGS = {target: '', port: 22, file: 'default', comment: ''};
    let entryList: sshHostKey[] = $state([]);
    let scanArgs: sshHostkeyScan = $state(EMPTY_SCAN_ARGS);

    function t(code: string) : string {
      return tq($share, code);
    }

    function searchFilter(item: sshHostKey, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let c = item.comment ? item.comment : '';
        return (
            item.host.toLowerCase().includes(s) ||
            item.file.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s)
        )
    }

    function handleSubmitResponse(s: number, j: any) {
        scanLoading = false;
        if (s == 200 && j.error === undefined) {
            scanModal = false;
        }
        apiResponseHandler.handleRes(s, j);
    }

    function scanHost() {
        scanLoading = true;
        apiSuccessMsg = 'ssh_hostkey.action.scan';
        apiEdit('post', 'ssh-hostkey', {
            target: scanArgs.target,
            port: scanArgs.port,
            file: scanArgs.file,
            comment: scanArgs.comment,
        }, handleSubmitResponse);
    }

    function deleteHost(host: string) {
        if (!host) {
            return;
        }
        apiSuccessMsg = 'ssh_hostkey.action.delete';
        apiEdit('delete', `ssh-hostkey/${host}`, null, apiResponseHandler.handleRes);
    }

    function updateHost(entry: sshHostKey) {
        scanArgs.target = entry.host;
        scanArgs.comment = entry.comment;
        scanArgs.file = entry.file;
        scanModal = true;
    }

    function loadHostkeyList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        entryList = j;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function buildUpdateHostkeyList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`ssh-hostkey?hash=${apiDataHash}`, loadHostkeyList);
    }

    $effect(() => {
        if (!scanModal) {
            scanArgs = EMPTY_SCAN_ARGS;
        }
    });

    onMount(() => {
        buildUpdateHostkeyList();
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateHostkeyList();
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
        <TableHeadCell sort={(a, b) => a.host.localeCompare(b.host)} defaultSort>
            {t('config.form.hostnames')}
        </TableHeadCell>
        <TableHeadCell sort={(a, b) => a.comment.localeCompare(b.comment)}>
            {t('common.comment')}
        </TableHeadCell>
        <TableHeadCell sort={(a, b) => a.file.localeCompare(b.file)}>
            {t('config.form.path_ssh_known_hosts')}
        </TableHeadCell>
        <TableHeadCell class="max-sm:hidden">
            {t('system.ssh_hostkey')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass={classListContent}>{item.host}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>{item.comment ? item.comment : '-'}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>{item.file}</TableBodyCell>
            <TableBodyCell tdClass="{classListContent} max-sm:hidden space-y-2">
                {#each item.hostkeys as hostkey}
                    <div class="text-xs break-all max-w-[50vw]">{hostkey}</div>
                {/each}
            </TableBodyCell>
            <TableBodyCell tdClass="{classListContent} action-btns">
                <Button size="xs" on:click={() => {deleteHost(item.host)}}><TrashBinSolid/></Button>
                <Tooltip>{t('btn.delete')}</Tooltip>

                <Button size="xs" on:click={() => {updateHost(item)}}><RefreshOutline/></Button>
                <Tooltip>{t('btn.update')}</Tooltip>
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
        <Button id="ssh-hostkey-btn-scan" on:click={() => {scanModal = true}}>{t('btn.add')}</Button>
    </div>
</div>

<Modal bind:open={scanModal} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('ssh_hostkey.scan')}</Heading>

        <div class={classModalInput}>
            <Label for="ssh_hostkey_target" class={classModalLabel}>{t('ssh_hostkey.target')}</Label>
            <Input id="ssh_hostkey_target" bind:value={scanArgs.target} />
            <Helper class={classModalHelp}>{t('ssh_hostkey.form.help.target')}</Helper>
        </div>
        <div class={classModalInput}>
            <Label for="ssh_hostkey_port" class={classModalLabel}>{t('config.form.port')}</Label>
            <Input id="ssh_hostkey_port" type="number" bind:value={scanArgs.port} />
        </div>
        <div class={classModalInput}>
            <Label for="ssh_hostkey_file" class={classModalLabel}>{t('config.form.path_ssh_known_hosts')}</Label>
            <Input id="ssh_hostkey_file" bind:value={scanArgs.file} />
            <Helper class={classModalHelp}>{t('ssh_hostkey.form.help.file')}</Helper>
        </div>
        <div class={classModalInput}>
            <Label for="ssh_hostkey_cmt" class={classModalLabel}>{t('common.comment')}</Label>
            <Input id="ssh_hostkey_cmt" bind:value={scanArgs.comment} />
        </div>
        <div class={classModalBtns}>
            <Button id="ssh-hostkey-btn-scan-submit" on:click={() => {scanHost()}}><PlaySolid/></Button>
            <Tooltip>{t('btn.execute')}</Tooltip>

            <Button id="ssh-hostkey-btn-scan-close" on:click={() => (scanModal = false)} class="inline-block ml-2">
                <CloseCircleSolid/>
            </Button>
            <Tooltip>{t('btn.close')}</Tooltip>
        </div>
        {#if scanLoading}
            <div class={classSpinnerDiv}><Spinner/></div>
        {/if}
    </div>
</Modal>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
