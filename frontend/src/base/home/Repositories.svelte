<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid, CodeBranchSolid, FolderOpenSolid, DownloadSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import type { repoType} from './Types.js';
    import type { entryActionStateExec } from '../Types.js';
    import RepositoryForm from './forms/Repository.svelte';
    import ConfirmActionPrompt from './forms/ConfirmAction.svelte';
    import RepositoryInfoPopover from './popovers/RepositoryList.svelte';
    import { REPO_EXEC_STATI_ACTIVE, repoKindMap, EXEC_STATUS_FAILED, EXEC_STATUS_SUCCESS } from '../Config.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing,
        classSpoilerItem, classSpoilerPad,
    } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    interface entryActionsType {
        [id: number]: entryActionStateExec;
    }

    let apiResponseHandler: APIResponseHandler = $state();
    let addGitModal = $state(false);
    let addStaticModal = $state(false);
    let addGitModalId = $state(Date.now());
    let addStaticModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let entryActions: entryActionsType = $state({});
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let searchedAt = $state(0);

    interface repoLists {
        static: repoType[]
        git: repoType[]
    }

    let entryLists: repoLists = $state({'static': [], 'git': []});

    function t(code: string) : string {
        return tq($share, code);
    }

    function loadRepoList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        for (let r of j) {
            if (!entryActions[r.id]) {
                entryActions[r.id] = {edit: false, clone: false};
            }
        }
        let newStatic = [];
        let newGit = [];
        for (let r of j) {
            if (r.rtype == repoKindMap['static']) {
                newStatic.push(r);
            } else {
                newGit.push(r);
            }
        }
        entryLists['static'] = newStatic;
        entryLists['git'] = newGit;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function deleteRepository(repoID: number) {
        if (!repoID) {
            return;
        }
        apiSuccessMsg = 'repos.action.delete';
        apiEdit('delete', `repository/${repoID}`, null, apiResponseHandler.handleRes);
    }

    function downloadGitRepo(repoID: number) {
        if (!repoID) {
            return;
        }
        apiSuccessMsg = 'repos.action.download';
        apiEdit('post', `repository/${repoID}`, null, apiResponseHandler.handleRes);
    }

    function isDownloadActive(repo: repoType) : boolean {
        return REPO_EXEC_STATI_ACTIVE.includes(repo.status);
    }

    function searchFilter(item: repoType, searchTerm: string) : boolean {
        searchedAt = Date.now();
        let s = searchTerm.toLowerCase();
        if (item.rtype_name.toLowerCase() == 'static') {
            let p = item.static_path ? item.static_path : '';
            return (
                item.name.toLowerCase().includes(s) ||
                p.toLowerCase().includes(s)
            )
        }
        
        let o = item.git_origin ? item.git_origin : '';
        let b = item.git_branch ? item.git_branch : '';
        return (
            item.name.toLowerCase().includes(s) ||
            o.toLowerCase().includes(s) ||
            b.toLowerCase().includes(s)
        )
    }

    function buildUpdateRepoList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (addGitModal || addStaticModal || isUserEditing()) {
            // user currently adding/editing entry
            return;
        }
        apiGet(`repository?hash=${apiDataHash}`, loadRepoList);
    }

    function isUserEditing(): boolean {
        if (updatedAt == 0) {
            return false;
        }
        let any_open = Object.values(entryActions).some(state => state.edit);;
        return any_open;
    }

    // action confirmation-prompt
    let confirmAction: string = $state('btn.delete');
    let confirmActionOpen: boolean = $state(false);
    let confirmActionProceed: boolean = $state(false);
    let confirmActionText: string = $state('');
    let confirmActionHoldEntryID: number = $state(0);

    function confirmDeleteAlert(repoKind: string, repoID: number, repoName: string) {
        confirmActionProceed = false;
        confirmActionHoldEntryID = repoID;
        confirmAction = 'btn.delete';
        const languageCodeKind = t(`repos.${repoKind}`);
        confirmActionText = `${languageCodeKind} "${repoName}"`;
        confirmActionOpen = true;
    }

    function checkActionConfirmed() {
        if (!confirmActionProceed || confirmActionHoldEntryID == 0) {
            return;
        }
        if (confirmAction == 'btn.delete') {
            deleteRepository(confirmActionHoldEntryID);
        }
    }

    $effect(() => {
        if (!confirmActionOpen) {
            checkActionConfirmed();
        }
    });

    onMount(() => {
        buildUpdateRepoList();
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateRepoList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg}
    bind:successMsg={apiSuccessMsg} bind:showSuccess={apiSuccess} />

<div>
    <Accordion>
        {#each Object.keys(repoKindMap) as repoKind (repoKind) }
            <AccordionItem defaultClass="{classSpoilerItem} repos-kind-{repoKind}" paddingDefault={classSpoilerPad}>
                <span slot="header">
                    {#if repoKind == 'static'}
                        <FolderOpenSolid class="inline-block"/>
                    {:else}
                        <CodeBranchSolid class="inline-block"/>
                    {/if}
                    {t(`repos.${repoKind}`)}
                </span>
                <div>
                  <Table striped={true} bind:items={entryLists[repoKind]} hoverable={true} shadow
                      placeholder={t('common.search')} filter={(item, searchTerm) => {return searchFilter(item, searchTerm)}}>
                    <TableHead theadClass={classListHeader}>
                        <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                            {t('common.name')}
                        </TableHeadCell>
                        <TableHeadCell class="max-lg:hidden" sort={(a, b) => a.name.localeCompare(b.name)}>
                            {t(`repos.${repoKind}.src`)}
                        </TableHeadCell>
                        {#if repoKind == 'git'}
                            <TableHeadCell class="max-sm:hidden" sort={(a, b) => {
                                let aUpdatedAt = a.time_update ? a.time_update : 'z';
                                let bUpdatedAt = b.time_update ? b.time_update : 'z';
                                return aUpdatedAt.name.localeCompare(bUpdatedAt);
                            }}>
                                {t('common.status')}
                            </TableHeadCell>
                        {/if}
                        <TableHeadCell>{t('common.actions')}</TableHeadCell>
                    </TableHead>
                    {#key updatedAt}
                    <TableBody tableBodyClass="divide-y">
                        <TableBodyRow slot="row" let:item>
                            <TableBodyCell tdClass={classListContent}>
                                {item.name}
                                {#key item.id}
                                    <button id="repos-name-{item.id}" class="ml-1">
                                        <InfoCircleSolid size="sm"/>
                                        <span class="sr-only">{t('repos.info')}</span>
                                    </button>
                                {/key}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} max-lg:hidden">
                                {#if item.rtype == repoKindMap['git']}
                                    {item.git_origin}:{item.git_branch}
                                {:else}
                                    {item.static_path}
                                {/if}
                            </TableBodyCell>
                            {#if repoKind == 'git'}
                                <TableBodyCell class="{classListContent} max-sm:hidden">
                                    <div>
                                        <b>{t('common.updated_at')}:</b> {item.time_update ? item.time_update : '-'}
                                    </div>
                                    <div>
                                        <b>{t('common.status')}:</b>
                                        <span class={item.status == EXEC_STATUS_FAILED ? 'text-red-600' : 'text-green-600'}>
                                            {#if item.status == EXEC_STATUS_FAILED}
                                                {t('jobs.info.failed')}
                                            {:else if item.status == EXEC_STATUS_SUCCESS}
                                                {t('jobs.info.succeeded')}
                                            {:else}
                                                {t('jobs.info.running')}
                                            {/if}
                                        </span>
                                    </div>
                                    {#if item.log_stdout_url || item.log_stderr_url}
                                        <div>
                                            <b>{t('home.logs')}:</b> 
                                            {#if item.log_stdout_url}
                                                <a href={item.log_stdout_url}>{t('logs.repo_log_file')}</a>
                                            {/if}
                                            {#if item.log_stdout_url && item.log_stderr_url}
                                            |
                                            {/if}
                                            {#if item.log_stderr_url}
                                                <a href={item.log_stderr_url}>{t('logs.repo_error_log_file')}</a>
                                            {/if}
                                        </div>
                                    {/if}
                                </TableBodyCell>
                            {/if}
                            <TableBodyCell tdClass="{classListContent} action-btns">
                                {#if repoKind == 'git'}
                                    <div class="mb-1">
                                        <Button size="xs" on:click={() => (downloadGitRepo(item.id))} disabled={isDownloadActive(item)}
                                            id="repos-btn-dl-{item.id}">
                                            <DownloadSolid/>
                                        </Button>
                                        <Tooltip>{t('btn.download')}</Tooltip>
                                    </div>
                                {:else}
                                    <div></div>
                                {/if}
                                <div>
                                    <Button size="xs" on:click={() => {entryActions[item.id].edit = true}} id="repos-btn-edit-{item.id}">
                                        <EditSolid/>
                                    </Button>
                                    <Tooltip>{t('btn.edit')}</Tooltip>
                
                                    <Button size="xs" on:click={() => {entryActions[item.id].clone = true}} id="repos-btn-clone-{item.id}">
                                        <FileCloneSolid/>
                                    </Button>
                                    <Tooltip>{t('btn.clone')}</Tooltip>
                
                                    <Button size="xs" on:click={() => {confirmDeleteAlert(repoKind, item.id, item.name)}} id="repos-btn-delete-{item.id}">
                                        <TrashBinSolid/>
                                    </Button>
                                    <Tooltip>{t('btn.delete')}</Tooltip>

                                    <div class="w-0 h-0 inline">
                                        {#key item.id}
                                            <RepositoryForm bind:open={entryActions[item.id].edit} action='edit' rtypeName={repoKind}
                                                existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                                            <RepositoryForm bind:open={entryActions[item.id].clone} action='clone' rtypeName={repoKind}
                                                existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                        {/key}
                                    </div>
                                </div>
                            </TableBodyCell>
                        </TableBodyRow>
                    </TableBody>
                    {/key}
                  </Table>
                  {#if !entryLists[repoKind].length}
                      <div class={classSpinnerDiv}><Spinner/></div>
                  {/if}
                </div>
                <div>
                    {#each entryLists[repoKind] as repo, repoIdx (repo.id)}
                        {#if repoKind == repo.rtype_name.toLowerCase()}
                            {#key searchedAt}
                            <div id="repos-infos-{repo.id}">
                                <RepositoryInfoPopover bind:repo={entryLists[repoKind][repoIdx]} repoKind={repoKind} />
                            </div>
                            {/key}
                        {/if}
                    {/each}
                </div>
            </AccordionItem>
        {/each}
    </Accordion>    
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button id="repos-btn-add-dd">{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem id="repos-btn-add-static" on:click={() => {addStaticModalId = Date.now(); addStaticModal = true}}>
                <FolderOpenSolid class="inline-block"/> {t('repos.static')}
            </DropdownItem>
            <DropdownItem id="repos-btn-add-git" on:click={() => {addGitModalId = Date.now(); addGitModal = true}}>
                <CodeBranchSolid class="inline-block"/> {t('repos.git')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>

{#key addGitModalId}
    <RepositoryForm bind:open={addGitModal} action='add' rtypeName='git'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key addStaticModalId}
    <RepositoryForm bind:open={addStaticModal} action='add' rtypeName='static'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key confirmActionHoldEntryID}
    <ConfirmActionPrompt bind:open={confirmActionOpen} bind:action={confirmAction}
        bind:confirmed={confirmActionProceed} bind:confirmText={confirmActionText}
    />
{/key}

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
