<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid, CodeBranchSolid, FolderOpenSolid, DownloadSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Popover, Radio,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { tq } from '../../util/translate.js';
    import { isSet } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import RepositoryForm from './forms/Repository.svelte';
    import { repoKindMap, REPO_EXEC_STATI_ACTIVE } from './Config.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classPopoverColumn1, classListHeader, classListContent,
        classPopover, classPopoverColumn2Div, classPopoverColumn2Text, classPopoverTitle,
    } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let addGitModal = $state(false);
    let addStaticModal = $state(false);
    let addGitModalId = $state(Date.now());
    let addStaticModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let entryActions = $state({});
    let updateLoop: number = $state(0);

    interface repoType {
        id: number,
        name: string,
        rtype: number,
        rtype_name: string,
        static_path: string|null,
        git_origin: string|null,
        git_credentials: string|null,
        git_branch: string|null,
        git_isolate: boolean,
        git_lfs: boolean,
        git_limit_depth: number|null,
        git_hook_pre: string|null,
        git_hook_post: string|null,
        git_hook_cleanup: string|null,
        git_override_initialize: string|null,
        git_override_update: string|null,
        git_playbook_base: string|null,
        git_timeout: number|null,
        time_update: string,
        status: number,
        status_name: string,
        log_stdout: string|null,
        log_stdout_url: string|null,
        log_stderr: string|null,
        log_stderr_url: string|null,
    }

    let entryList: repoType[] = $state([]);

    function t(code: string) {
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
        entryList = j;
        apiDataHash = h;
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

    function isDownloadActive(repo: repoType) {
        return REPO_EXEC_STATI_ACTIVE.includes(repo.status);
    }

    function buildUpdateRepoList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`repository?hash=${apiDataHash}`, loadRepoList);
    }

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
            <AccordionItem>
                <span slot="header">{t(`repos.${repoKind}`)}</span>
        
                <div>
                    <Table striped={true}>
                    <TableHead theadClass={classListHeader}>
                        <TableHeadCell>{t('common.name')}</TableHeadCell>
                        <TableHeadCell class="max-lg:hidden">{t(`repos.${repoKind}.src`)}</TableHeadCell>
                        {#if repoKind == 'git'}
                            <TableHeadCell>{t('common.status')}</TableHeadCell>
                        {/if}
                        <TableHeadCell>{t('common.actions')}</TableHeadCell>
                    </TableHead>
                    <TableBody tableBodyClass="divide-y">
                        {#each entryList as repo (repo.id)}
                            {#if repoKindMap[repoKind] == repo.rtype}
                                <TableBodyRow>
                                    <TableBodyCell tdClass={classListContent}>
                                        {repo.name}
                                        <button id="repo-name-{repo.id}" class="ml-1">
                                            <InfoCircleSolid size="sm"/>
                                            <span class="sr-only">{t('repos.info')}</span>
                                        </button>
                                    </TableBodyCell>
                                    <TableBodyCell tdClass="{classListContent} max-lg:hidden">
                                        {#if repo.rtype == repoKindMap['git']}
                                            {repo.git_origin}:{repo.git_branch}
                                        {:else}
                                            {repo.static_path}
                                        {/if}
                                    </TableBodyCell>
                                    {#if repoKind == 'git'}
                                        <TableBodyCell class={classListContent}>
                                            <div>
                                                <b>Updated:</b> {repo.time_update ? repo.time_update : '-'}
                                            </div>
                                            <div>
                                                <!-- todo: status color green/red/blue -->
                                                <b>Status:</b> <span>{repo.status_name}</span>
                                            </div>
                                            {#if repo.log_stderr_url || repo.log_stderr_url}
                                                <div>
                                                    <b>Logs:</b> 
                                                    {#if repo.log_stderr_url}
                                                        <a href={repo.log_stdout_url}>Output</a>
                                                    {/if}
                                                    {#if repo.log_stderr_url}
                                                        <a href={repo.log_stderr_url}>Error</a>
                                                    {/if}
                                                </div>
                                            {/if}
                                        </TableBodyCell>
                                    {/if}
                                    <TableBodyCell tdClass={classListContent}>
                                        {#if repoKind == 'git'}
                                            <div class="mb-2">
                                                <Button size="xs" on:click={() => (downloadGitRepo(repo.id))}
                                                    disabled={isDownloadActive(repo)}>
                                                    <DownloadSolid/>
                                                </Button>
                                                <Tooltip>{t('btn.download')}</Tooltip>
                                            </div>
                                        {/if}
                                        <div>
                                            <RepositoryForm bind:open={entryActions[repo.id].edit} action='edit' rtypeName={repoKind}
                                                existingID={repo.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                            <Button size="xs" on:click={() => {entryActions[repo.id].edit = true}}><EditSolid/></Button>
                                            <Tooltip>{t('btn.edit')}</Tooltip>
                        
                                            <RepositoryForm bind:open={entryActions[repo.id].clone} action='clone' rtypeName={repoKind}
                                                existingID={repo.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                            <Button size="xs" on:click={() => {entryActions[repo.id].clone = true}}><FileCloneSolid/></Button>
                                            <Tooltip>{t('btn.clone')}</Tooltip>
                        
                                            <Button size="xs" on:click={() => {deleteRepository(repo.id)}}><TrashBinSolid/></Button>
                                            <Tooltip>{t('btn.delete')}</Tooltip>
                                        </div>
                                    </TableBodyCell>
                                </TableBodyRow>
                            {/if}
                        {/each}
                    </TableBody>
                    </Table>
                    {#if !entryList.length}
                        <div class={classSpinnerDiv}><Spinner/></div>
                    {/if}
                </div>
                <div>
                    {#each entryList as repo (repo.id)}
                        {#if repoKindMap[repoKind] == repo.rtype}
                        <div id="repo-infos-{repo.id}">
                            <Popover triggeredBy="#repo-name-{repo.id}" class={classPopover} placement="bottom-start">
                                <div class="p-3 space-y-2">
                                    <h3 class={classPopoverTitle}>{t('repos.info')}</h3>
                                </div>
                                <table>
                                    <tbody>
                                        <!-- todo: extend -->
                                        {#if repoKind == 'static'}
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.static_path')}:
                                                </td>
                                                <td class={classPopoverColumn2Text}>
                                                    {repo.static_path}
                                                </td>
                                            </tr>
                                        {:else}
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_origin')}:
                                                </td>
                                                <td class={classPopoverColumn2Text}>
                                                    {repo.git_origin}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_branch')}:
                                                </td>
                                                <td class={classPopoverColumn2Text}>
                                                    {repo.git_branch}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_credentials')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_credentials)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_limit_depth')}:
                                                </td>
                                                <td class={classPopoverColumn2Text}>
                                                    {repo.git_limit_depth ? repo.git_limit_depth : '-'}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_playbook_base')}:
                                                </td>
                                                <td class={classPopoverColumn2Text}>
                                                    {repo.git_playbook_base ? repo.git_playbook_base : '-'}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_lfs')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={repo.git_lfs}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_isolate')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={repo.git_isolate}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_hook_pre')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_hook_pre)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_hook_post')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_hook_post)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_hook_cleanup')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_hook_cleanup)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_override_initialize')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_override_initialize)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class={classPopoverColumn1}>
                                                    {t('repos.form.git_override_update')}:
                                                </td>
                                                <td class={classPopoverColumn2Div}>
                                                    <button class="cursor-default">
                                                        <Radio class="inline-block" checked={isSet(repo.git_override_update)}></Radio>
                                                    </button>
                                                </td>
                                            </tr>
                                        {/if}
                                    </tbody>
                                </table>
                            </Popover>
                        </div>
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
        <Button>{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem on:click={() => {addStaticModalId = Date.now(); addStaticModal = true}}>
                <FolderOpenSolid class="inline-block"/> {t('repos.static')}
            </DropdownItem>
            <DropdownItem on:click={() => {addGitModalId = Date.now(); addGitModal = true}}>
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
