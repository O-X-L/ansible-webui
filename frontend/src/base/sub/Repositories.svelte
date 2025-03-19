<script lang="ts">
    import { onMount } from 'svelte';

    import {
        InfoCircleSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid, CodeBranchSolid, FolderOpenSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Popover, Radio,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import RepositoryForm from './forms/Repository.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classPopoverColumn1, classListHeader, classListContent,
        classPopover, classPopoverColumn2Div, classPopoverColumn2Text, classPopoverTitle,
    } from '../Style.js';
 
    const repoKindMap = {'static': 1, 'git': 2};

    let apiResponseHandler: APIResponseHandler = $state();
    let addGitModal = $state(false);
    let addStaticModal = $state(false);
    let addGitModalId = $state(Date.now());
    let addStaticModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let entryActions = $state({});

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
        git_limit_depth: string|null,
        git_hook_pre: string|null,
        git_hook_post: string|null,
        git_hook_cleanup: string|null,
        git_override_initialize: string|null,
        git_override_update: string|null,
        git_playbook_base: string|null,
        git_timeout: string|null,
        time_update: string,
        status: string,
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
        if (!j || h == apiDataHash) {
            return;
        }
        for (let c of j[kind]) {
            if (!entryActions[kind][c.id]) {
                entryActions[kind][c.id] = {edit: false, clone: false};
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

    function buildUpdateJobList() {
        if (typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`repository?hash=${apiDataHash}`, loadRepoList);
    }

    // todo: refresh data over websockets
    setInterval(() => {
        buildUpdateJobList();
    }, $share.updateInterval)

    onMount(() => {
        buildUpdateJobList();
    })
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:successMsg={apiSuccessMsg} />

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
                                        <button id="repos-name-{repo.id}" class="ml-1">
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
                                            <div>
                                                <b>Logs:</b> 
                                                {#if repo.log_stderr_url}
                                                    <a href={repo.log_stdout_url}>Output</a>
                                                {/if}
                                                {#if repo.log_stderr_url}
                                                    <a href={repo.log_stderr_url}>Error</a>
                                                {/if}
                                            </div>
                                        </TableBodyCell>
                                    {/if}
                                    <TableBodyCell tdClass={classListContent}>
                                        <RepositoryForm bind:open={entryActions[repo.id].edit} action='edit'
                                        existingID={repo.id} />
                                        <Button size="xs" on:click={() => {entryActions[repo.id].edit = true}}><EditSolid/></Button>
                                        <Tooltip>{t('btn.edit')}</Tooltip>
                    
                                        <RepositoryForm bind:open={entryActions[repo.id].clone} action='clone'
                                        existingID={repo.id} />
                                        <Button size="xs" on:click={() => {entryActions[repo.id].clone = true}}><FileCloneSolid/></Button>
                                        <Tooltip>{t('btn.clone')}</Tooltip>
                    
                                        <Button size="xs" on:click={() => {deleteRepository(repo.id)}}><TrashBinSolid/></Button>
                                        <Tooltip>{t('btn.delete')}</Tooltip>
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
                        <div id="creds-infos-{repo.id}">
                            <Popover triggeredBy="#creds-name-{repo.id}" class={classPopover} placement="bottom-start">
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
                                        {/if}
                                        {#if repoKind == 'git'}
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
    <RepositoryForm bind:open={addGitModal} action='add' />
{/key}
{#key addStaticModalId}
    <RepositoryForm bind:open={addStaticModal} action='add' />
{/key}
