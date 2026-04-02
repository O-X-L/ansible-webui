<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { TrashBinSolid, EditSolid, FileCloneSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet, formJSON } from '../../util/api.js';
    import PermissionForm from './forms/Permission.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing,
    } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let entryActions = $state({});
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);

    interface permissionType {
        id: number
        name: string
        permission: number
        permission_name: string
        jobs: number[]|null
        jobs_name: string[]|null
        jobs_all: boolean
        credentials: number[]|null
        credentials_name: string[]|null
        credentials_all: boolean
        repositories: number[]|null
        repositories_name: string[]|null
        repositories_all: boolean
        users: number[]|null
        users_name: string[]|null
        groups: number[]|null
        groups_name: string[]|null
    }

    let entryList: permissionType[] = $state([]);

    function t(code: string) : string {
      return tq($share, code);
    }

    function searchFilter(item: permissionType, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let j = item.jobs_name ? item.jobs_name.join('|') : '';
        let c = item.credentials_name ? item.credentials_name.join('|') : '';
        let r = item.repositories_name ? item.repositories_name.join('|') : '';
        let u = item.users_name ? item.users_name.join('|') : '';
        let g = item.groups_name ? item.groups_name.join('|') : '';
        return (
            item.name.toLowerCase().includes(s) ||
            j.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s) ||
            r.toLowerCase().includes(s) ||
            u.toLowerCase().includes(s) ||
            g.toLowerCase().includes(s)
        )
    }

    function getMembersSummary(perm: permissionType) {
        let m = [];
        if (perm.users.length > 0) {
            m.push(t('permission.users'));
        }
        if (perm.groups.length > 0) {
            m.push(t('permission.groups'));
        }
        if (m.length == 0) {
            m.push('-');
        }
        return m;
    }

    function getPermittedSummary(perm: permissionType) {
        let m = [];
        if (perm.jobs.length > 0 || perm.jobs_all) {
            m.push(t('home.jobs'));
        }
        if (perm.credentials.length > 0 || perm.credentials_all) {
            m.push(t('home.creds'));
        }
        if (perm.repositories.length > 0 || perm.repositories_all) {
            m.push(t('home.repos'));
        }
        if (m.length == 0) {
            m.push('-');
        }
        return m;
    }

    function deletePermission(permID: number) {
        if (!permID) {
            return;
        }
        apiSuccessMsg = 'permission.action.delete';
        apiEdit('delete', `permission/${permID}`, null, apiResponseHandler.handleRes);
    }

    function loadPermList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        for (let p of j) {
            if (!entryActions[p.id]) {
                entryActions[p.id] = {edit: false, clone: false};
            }
        }
        entryList = j;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function buildUpdatePermList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`permission?hash=${apiDataHash}`, loadPermList);
    }

    onMount(() => {
        buildUpdatePermList();
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdatePermList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg}
    bind:successMsg={apiSuccessMsg} bind:showSuccess={apiSuccess} />

<div>
    <Table striped={true} bind:items={entryList} hoverable={true} shadow placeholder={t('common.search')}
        filter={(item, searchTerm) => (searchFilter(item, searchTerm))}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
            {t('common.name')}
        </TableHeadCell>
        <TableHeadCell sort={(a, b) => a.permission_name.localeCompare(b.permission_name)}>
            {t('permission.level')}
        </TableHeadCell>
        <TableHeadCell class="max-sm:hidden">
            {t('permission.members')}
        </TableHeadCell>
        <TableHeadCell class="max-sm:hidden">
            {t('permission.permitted')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass={classListContent}>{item.name}</TableBodyCell>
            <TableBodyCell tdClass={classListContent}>{item.permission_name}</TableBodyCell>
            <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                {getMembersSummary(item).join(' & ')}
            </TableBodyCell>
            <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                {getPermittedSummary(item).join(' & ')}
            </TableBodyCell>
            <TableBodyCell tdClass="{classListContent} action-btns">
                <Button size="xs" on:click={() => {entryActions[item.id].edit = true}}><EditSolid/></Button>
                <Tooltip>{t('btn.edit')}</Tooltip>

                <Button size="xs" on:click={() => {entryActions[item.id].clone = true}}><FileCloneSolid/></Button>
                <Tooltip>{t('btn.clone')}</Tooltip>

                <Button size="xs" on:click={() => {deletePermission(item.id)}}><TrashBinSolid/></Button>
                <Tooltip>{t('btn.delete')}</Tooltip>

                <div class="w-0 h-0 inline">
                    {#key item.id}
                        <PermissionForm bind:open={entryActions[item.id].edit} action='edit'
                            existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                        <PermissionForm bind:open={entryActions[item.id].clone} action='clone'
                            existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                    {/key}
                </div>
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
        <Button on:click={() => {addModalId = Date.now(); addModal = true}} id="perms-btn-add">{t('btn.add')}</Button>
    </div>    
</div>

{#key addModalId}
    <PermissionForm bind:open={addModal} action='add'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
