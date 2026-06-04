<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, 
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import JobForm from './forms/Job.svelte';
    import JobExecutionForm from './forms/JobExecution.svelte';
    import JobInfoPopovers from './popovers/JobList.svelte';
    import { tq } from '../../util/translate.js';
    import { redirectLogs } from './util/JobUtils';
    import { apiEdit, apiGet, cacheKey } from '../../util/api.js';
    import type { jobType } from './Types.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { JOB_EXEC_STATI_ACTIVE } from '../Config.js';
    import type { formChoiceType, formInfoType, entryActionStateExec } from '../Types.js';
    import { getURLHashParams, setURLHashParams } from '../../util/main.js';
    import {
        classSpinnerDiv, classListContent, classListHeader, classFooterSpacing,
    } from '../Style.js';

    const URL_HASH = 'jobs';
    const HASH_PARAM_EXEC = 'exec';
    const HASH_PARAM_EDIT = 'edit';

    let { open = $bindable(false) } = $props();

    interface entryActionsType {
        [id: number]: entryActionStateExec;
    }

    let apiResponseHandler: APIResponseHandler = $state();
    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let executionPromptID = $state(Date.now());
    let entryList: jobType[] = $state([]);
    let entryActions: entryActionsType = $state({});
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiError = $state(false);
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let searchedAt = $state(0);
    // todo: init search from url-param
    //let tableSearchTerm = $state('');
    let loaded = $state(false);

    interface credentialType {
        id: number,
        name: string,
    }
    interface credentialsType {
        shared: credentialType[],
        user: credentialType[],
    }

    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let usableCredentials: credentialsType = $state({shared: [], user: []});
    let usableCredentialChoices = $derived(buildCredentialChoices(usableCredentials));

    function t(code: string) : string {
        return tq($share, code);
    }

    function setFormInfos(j: any) {
        formInfos = j;
    }

    function isJobActive(job: jobType) : boolean {
        if (!job.executions.length) {
            return false;
        }
        return JOB_EXEC_STATI_ACTIVE.includes(job.executions[0].status);
    }

    function stopJob(jobId: number, executionId: number) {
        if (!jobId || !executionId) {
            return;
        }
        apiSuccessMsg = 'jobs.action.stop';
        apiEdit('delete', `job/${jobId}/${executionId}`, null, apiResponseHandler.handleRes);
    }

    function deleteJob(jobId: number) {
        if (!jobId) {
            return;
        }
        apiSuccessMsg = 'jobs.action.delete';
        apiEdit('delete', `job/${jobId}`, null, apiResponseHandler.handleRes);
    }

    function editJob(jobId: number) {
        setURLHashParams(URL_HASH, {edit: jobId});
        entryActions[jobId].edit = true;
    }

    function openExecutionPrompt(job: jobType) {
        executionPromptID = Date.now();
        setURLHashParams(URL_HASH, {exec: job.id});
        entryActions[job.id].exec = true;
    }

    function searchFilter(item: jobType, searchTerm: string) : boolean {
        searchedAt = Date.now();
        if (searchTerm.includes('id:')) {
            let sid = searchTerm.split(':')[1];
            return String(item.id) == sid;
        }

        let s = searchTerm.toLowerCase();
        let c = item.comment ? item.comment : '';
        let i = item.inventory_file ? item.inventory_file : '';
        return (
            item.name.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s) ||
            item.playbook_file.toLowerCase().includes(s) ||
            i.toLowerCase().includes(s)
        )
    }

    /*
    function setSearchByURL() {
        let paramSearch = urlParams.get(PARAM_SEARCH);
        if (!paramSearch) {
            return;
        }
        tableSearchTerm = paramSearch;
    }
    */

    // todo: update search url-param on input

    function loadCredentialInfos(j: any) {
        j.shared.sort((a: credentialType, b: credentialType) => a.name.localeCompare(b.name));
        j.user.sort((a: credentialType, b: credentialType) => a.name.localeCompare(b.name));
        usableCredentials = j;
    }

    function buildCredentialChoices(cr: credentialsType) : formChoiceType[] {
        let choices: formChoiceType[] = [];
        for (let c of cr.user) {
            choices.push({value: `user-${c.id}`, name: `${t('creds.user')} - ${c.name}`});
        }
        for (let c of cr.shared) {
            choices.push({value: `shared-${c.id}`, name: `${t('creds.shared')} - ${c.name}`});
        }
        return choices;
    }

    function loadJobList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        for (let job of j) {
            if (!entryActions[job.id]) {
                entryActions[job.id] = {edit: false, clone: false, exec: false};
            }
        }
        entryList = j;
        apiDataHash = h;
        updatedAt = Date.now();
        if (!loaded) {
            loaded = true;
            openModalByURL();
        }
        /*
        if (!loaded) {
            setSearchByURL();
            loaded = true;
        }
        */
    }

    function buildUpdateJobList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (addModal || isUserEditingOrExecuting()) {
            // user currently adding/editing entry
            return;
        }
        apiGet(`job?executions=true&execution_count=1&hash=${apiDataHash}`, loadJobList);
    }

    function openModalByURL() {
        let params = getURLHashParams();
        let action: 'clone'|'edit'|'exec'|null = null;
        let value = null;

        // only one possible
        for (let k of [HASH_PARAM_EDIT, HASH_PARAM_EXEC]) {
            if (params[String(k)]) {
                value = params[String(k)];
                action = k;
            }
        }
        if (action == null) {
            return;
        }

        for (let job of entryList) {
            if (String(job.id) == String(value)) {
                if (action == HASH_PARAM_EXEC) {
                    openExecutionPrompt(job);
                } else {
                    entryActions[job.id][action] = true;
                }
                break;
            }
        }
    }

    function isUserEditingOrExecuting(): boolean {
        if (updatedAt == 0) {
            return false;
        }
        let any_open = Object.values(entryActions).some(job => job.exec || job.edit);
        return any_open;
    }

    function updateURLHash(_: any) {
        // remove hash-params from URL if modals were closed
        if (!loaded) {
            return;
        }
        if (!isUserEditingOrExecuting()) {
            setURLHashParams(URL_HASH, null);
        } 
    }

    $effect(() => {
      updateURLHash(entryActions);
    });

    onMount(() => {
        buildUpdateJobList();
        apiGet('credentials', loadCredentialInfos);
        apiGet(`frontend/form/job?${cacheKey($share)}`, setFormInfos);

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateJobList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:showError={apiError}
    bind:successMsg={apiSuccessMsg} bind:showSuccess={apiSuccess} />

<div>
  <Table striped={true} bind:items={entryList} hoverable={true} shadow
        placeholder={t('common.search')} filter={(item, searchTerm) => {return searchFilter(item, searchTerm)}}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
            {t('jobs.job')}
        </TableHeadCell>
        <TableHeadCell class="max-lg:hidden" sort={(a, b) => a.inventory_file.localeCompare(b.inventory_file)}>
            {t('jobs.form.inventory_file')}
        </TableHeadCell>
        <TableHeadCell class="max-lg:hidden" sort={(a, b) => a.playbook_file.localeCompare(b.playbook_file)}>
            {t('jobs.form.playbook_file')}
        </TableHeadCell>
        <TableHeadCell class="max-sm:hidden" sort={(a, b) => {
            let aNextRun = a.next_run ? a.next_run : 'z';
            let bNextRun = b.next_run ? b.next_run : 'z';
            return aNextRun.localeCompare(bNextRun);
        }}>
            {t('jobs.form.schedule')}
        </TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    {#key updatedAt}
    <TableBody tableBodyClass="divide-y">
        <TableBodyRow slot="row" let:item>
            <TableBodyCell tdClass={classListContent}>
                {item.name}
                {#key item.id}
                    <button id="job-name-{item.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">{t('jobs.info')}</span>
                    </button>
                {/key}
            </TableBodyCell>
            <TableBodyCell class="{classListContent} max-lg:hidden">{item.inventory_file ? item.inventory_file : '-'}</TableBodyCell>
            <TableBodyCell class="{classListContent} max-lg:hidden">{item.playbook_file}</TableBodyCell>    
            <TableBodyCell class="{classListContent} max-sm:hidden">
                {item.next_run ? item.next_run : '-'}
                {#key item.id}
                    <button id="job-schedule-{item.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">{t('jobs.info.execution')}</span>
                    </button>
                {/key}
            </TableBodyCell>
            <TableBodyCell tdClass="{classListContent} action-btns">
                <div>
                    <Button size="xs" on:click={() => {openExecutionPrompt(item)}} disabled={isJobActive(item)} id="jobs-btn-exec-{item.id}">
                        <PlaySolid/>
                    </Button>
                    <Tooltip>{t('btn.execute')}</Tooltip>

                    <Button size="xs" on:click={() => {stopJob(item.id, item.executions[0].id)}}
                        disabled={!isJobActive(item)} id="jobs-btn-stop-{item.id}">
                        <StopSolid/>
                    </Button>
                    <Tooltip>{t('btn.stop')}</Tooltip>

                    <Button size="xs" on:click={() => (redirectLogs(item.id))} id="jobs-btn-logs-{item.id}">
                        <BookOpenSolid/>
                    </Button>
                    <Tooltip>{t('btn.logs')}</Tooltip>
                </div>
                <div class="mt-1">
                    <Button size="xs" on:click={() => (editJob(item.id))} id="jobs-btn-edit-{item.id}">
                        <EditSolid/>
                    </Button>
                    <Tooltip>{t('btn.edit')}</Tooltip>

                    <Button size="xs" on:click={() => {entryActions[item.id].clone = true}} id="jobs-btn-clone-{item.id}">
                        <FileCloneSolid/>
                    </Button>
                    <Tooltip>{t('btn.clone')}</Tooltip>

                    <Button size="xs" on:click={() => {deleteJob(item.id)}} id="jobs-btn-delete-{item.id}">
                        <TrashBinSolid/>
                    </Button>
                    <Tooltip>{t('btn.delete')}</Tooltip>

                    <div class="w-0 h-0 inline">
                        {#key item.id}
                            <JobForm bind:open={entryActions[item.id].edit} action='edit' existingID={item.id}
                                bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                            <JobForm bind:open={entryActions[item.id].clone} action='clone' existingID={item.id}
                                bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                        {/key}
                    </div>
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

<div>
    {#if loaded && apiResponseHandler}
    {#each entryList as job, jobIdx (job.id)}
        {#key searchedAt}
        <div id="job-infos-{job.id}">
            <JobInfoPopovers bind:job={entryList[jobIdx]} />
            {#key executionPromptID}
            <JobExecutionForm bind:open={entryActions[job.id].exec}
                bind:job={entryList[jobIdx]}
                bind:formChoices={formInfos.choices} usableCredentialChoices={usableCredentialChoices}
                bind:apiResponseHandler={apiResponseHandler}
                bind:apiSuccessMsg={apiSuccessMsg} bind:apiSuccess={apiSuccess} 
                bind:apiErrorMsg={apiErrorMsg} bind:apiError={apiError} />
            {/key}
        </div>
        {/key}
    {/each}
    {/if}
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button on:click={() => {addModalId = Date.now(); addModal = true}} id="jobs-btn-add">{t('btn.add')}</Button>
    </div>    
</div>

{#key addModalId}
    <JobForm bind:open={addModal} action='add' bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}


<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
