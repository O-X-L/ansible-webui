<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { BookOpenSolid, StopSolid, TrashBinSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Accordion, AccordionItem, Table, TableBody, TableBodyCell, TableBodyRow,
        TableHead, TableHeadCell, Input, Button, Tooltip, Label,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import LogsView from './forms/Logs.svelte';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import { type jobType, type executionType } from './Types.js';
    import { JOB_EXEC_STATI_ACTIVE, PARAM_JOB } from '../Config.js';
    import { redirectTo, getURLHashParams } from '../../util/main.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListContent, classListHeader, classFooterSpacing, classSpoilerItem, classSpoilerPad,
    } from '../Style.js';

    let { open = $bindable(false) } = $props();

    const ALL_JOBS_ID = 0;

    let apiResponseHandler: APIResponseHandler = $state();
    let jobList: jobType[] = $state([]);
    let executionList: executionType[] = $state([]);
    let entryJobActions = $state({ALL_JOBS_ID: false});
    let entryExecActions = $state({});
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiDataHashJobs = $state('');
    let apiDataHashExecs = $state('');
    let updateLoop: number = $state(0);
    let openJob: number|null = $state(null);
    let executionCount: number = $state(20);
    let loaded = $state(false);

    function t(code: string) : string {
        return tq($share, code);
    }

    function isJobExecutionActive(exec: executionType) : boolean {
        if (!exec) {
            return false;
        }
        return JOB_EXEC_STATI_ACTIVE.includes(exec.status);
    }

    function stopJob(jobId: number, executionId: number) {
        if (!jobId || !executionId) {
            return;
        }
        apiSuccessMsg = 'jobs.action.stop';
        apiEdit('delete', `job/${jobId}/${executionId}`, null, apiResponseHandler.handleRes);
    }

    function cleanupJobExecution(jobId: number, executionId: number) {
        if (!jobId || !executionId) {
            return;
        }
        apiSuccessMsg = 'jobs.action.exec_delete';
        apiEdit('delete', `job/${jobId}/${executionId}/cleanup`, null, apiResponseHandler.handleRes);
    }

    /*
    function redirectJob(jobId: number) {
        if (!jobId) {
            return;
        }
        redirectTo(`/ui#jobs-search=id:${jobId}`);
    }
    */

    function loadJobList(j: any, h: string) {
        if (j === null || h == apiDataHashJobs) {
            return;
        }
        for (let job of j) {
            if (!entryJobActions[job.id]) {
                entryJobActions[job.id] = false;
            }
        }
        j.sort((a: jobType, b: jobType) => a.name.localeCompare(b.name));
        jobList = j;
        apiDataHashJobs = h;
        if (!loaded) {
            loaded = true;
            openLogsByURL();
        }
    }

    function loadExecutionList(j: any, h: string) {
        if (j === null || h == apiDataHashExecs) {
            return;
        }
        for (let exec of j) {
            if (!entryExecActions[exec.id]) {
                entryExecActions[exec.id] = false;
            }
        }
        executionList = j;
        apiDataHashExecs = h;
    }

    function buildUpdateJobList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`job?hash=${apiDataHashJobs}`, loadJobList);
    }

    function buildUpdateExecutionList() {
        if (!openJob) {
            return;
        }

        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (openJob == ALL_JOBS_ID) {
            return buildUpdateExecutionListAllJobs();
        }
        apiGet(`job_exec/${openJob}?execution_count=${executionCount}&hash=${apiDataHashExecs}`, loadExecutionList);
    }

    function buildUpdateExecutionListAllJobs() {
        apiGet(`job_exec?execution_count=${executionCount}&hash=${apiDataHashExecs}`, loadExecutionList);
    }

    function tableScrollAnchor(job_id: number): string {
        return `table-scroll-${job_id}`;
    }

    function scrollToTable(job_id: number) {
        let e = document.getElementById(tableScrollAnchor(job_id));
        if (e) {
            e.scrollIntoView({behavior: "smooth", block: "start"});
        } else {
            console.log("WARNING: Logs not loaded yet - unable to scroll into view!");
        }
    }

    function isExecActive(exec: executionType) : boolean {
        return JOB_EXEC_STATI_ACTIVE.includes(exec.status);
    }

    function openLatestActiveExecution() {
        for (let exec of executionList) {
            if (isExecActive(exec)) {
                entryExecActions[exec.id] = true
                break;
            }
        }
    }

    function openLogsByURL() {
        let params = getURLHashParams();
        if (!params[PARAM_JOB]) {
            return;
        }
        for (let job of jobList) {
            if (String(job.id) == String(params[PARAM_JOB])) {
                entryJobActions[job.id] = true;
                // wait for load
                setTimeout(() => {scrollToTable(job.id)}, 2000);
                setTimeout(() => {openLatestActiveExecution()}, 2500);
                break;
            }
        }
    }

    function updateOpenJob(actions: any = ''){
        for (let [j, v] of Object.entries(actions)) {
            if (v) {
                if (j != openJob) {
                    executionList = [];
                }
                openJob = j;
                return;
            }
        }
        openJob = null;
        executionList = [];
        apiDataHashExecs = '';
    }

    $effect(() => {
        updateOpenJob(entryJobActions);
    });

    onMount(() => {
        buildUpdateJobList();

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateJobList();
            buildUpdateExecutionList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:successMsg={apiSuccessMsg} />

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mb-10">
        <Label>{t('logs.exec_count')}</Label>
        <Input type="number" bind:value={executionCount}
            on:input={() => {executionCount = Math.max(Math.min(executionCount, 1000), 1)}} />
    </div>
</div>

<Accordion>
    <AccordionItem bind:open={entryJobActions[ALL_JOBS_ID]} defaultClass="{classSpoilerItem} logs-job-{ALL_JOBS_ID}"
        paddingDefault={classSpoilerPad}>
            <span slot="header">{t('logs.all_jobs')}</span>
            {#if !executionList.length}
                <div class={classSpinnerDiv}><Spinner/></div>
            {:else}
            <Table striped={true} id="logs-{ALL_JOBS_ID}" shadow>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell class="max-sm:hidden">#</TableHeadCell>
                    <TableHeadCell>{t('common.name')}</TableHeadCell>
                    <TableHeadCell class="max-sm:hidden">{t('logs.time')}</TableHeadCell>
                    <TableHeadCell>{t('common.status')}</TableHeadCell>
                    <TableHeadCell class="max-lg:hidden">{t('btn.download')}</TableHeadCell>
                    <TableHeadCell>{t('common.actions')}</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    {#each executionList as exec, execIdx (exec.id)}
                    <TableBodyRow>
                        <TableBodyCell tdClass="{classListContent} text-center max-sm:hidden">
                            {exec.id}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} text-center">
                            {exec.job_name}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                            <div>{t('logs.time_start_short')}: {exec.time_start}</div>
                            <div>{t('logs.time_fin_short')}: {exec.time_fin}</div>
                            <div>{t('jobs.info.duration')}: {exec.time_duration}</div>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>
                            <div>{t('common.status')}:
                                {#if isJobExecutionActive(exec)}
                                    <span class="text-blue-600">{t('jobs.info.running')}</span>
                                {:else if exec.failed}
                                    <span class="text-red-600">{t('jobs.info.failed')}</span>
                                {:else}
                                    <span class="text-green-600">{t('jobs.info.succeeded')}</span>
                                {/if}
                            </div>
                            <div>{t('logs.executed_by')}: {exec.user_name}</div>
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} max-lg:hidden">
                            {#if exec.log_stdout_url}
                                <div><a href="{exec.log_stdout_url}">{t('logs.exec_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stderr_url}
                                <div><a href="{exec.log_stderr_url}">{t('logs.exec_error_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stdout_repo_url}
                                <div><a href="{exec.log_stdout_repo_url}">{t('logs.repo_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stderr_repo_url}
                                <div><a href="{exec.log_stderr_repo_url}">{t('logs.repo_error_log_file')}</a></div>
                            {/if}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} action-btns">
                            <div class="mt-2">
                                <Button size="xs" on:click={() => {entryExecActions[exec.id] = true}} id="logs-job-{exec.job}-{exec.id}-show">
                                    <BookOpenSolid/>
                                </Button>
                                <Tooltip>{t('btn.logs')}</Tooltip>
    
                                <Button size="xs" on:click={() => {stopJob(exec.job, exec.id)}}
                                    disabled={!isJobExecutionActive(exec)} id="logs-job-{exec.job}-{exec.id}-stop">
                                    <StopSolid/>
                                </Button>
                                <Tooltip>{t('btn.stop')}</Tooltip>

                                <Button size="xs" on:click={() => {cleanupJobExecution(exec.job, exec.id)}}
                                    disabled={isJobExecutionActive(exec)} id="logs-job-{exec.job}-{exec.id}-cleanup">
                                    <TrashBinSolid/>
                                </Button>
                                <Tooltip>{t('btn.delete')}</Tooltip>

                                <!--
                                <Button size="xs" on:click={() => {redirectJob(job.id)}}><CogSolid/></Button>
                                <Tooltip>{t('jobs.job')}</Tooltip>
                                -->
    
                                <LogsView bind:open={entryExecActions[exec.id]}
                                    jobID={exec.job} jobName={exec.job_name} bind:exec={executionList[execIdx]} />
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                    {/each}
                </TableBody>
            </Table>
            {/if}
    </AccordionItem>

    {#each jobList as job (job.id)}
        <AccordionItem bind:open={entryJobActions[job.id]} defaultClass="{classSpoilerItem} logs-job-{job.id}"
            paddingDefault={classSpoilerPad}>
            <span slot="header">{job.name}</span>
            {#if !executionList.length}
                <div class={classSpinnerDiv}><Spinner/></div>
            {:else}
            <div id={tableScrollAnchor(job.id)} class="w-0 h-0"></div>

            <Table striped={true} id="logs-{job.id}" shadow>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell class="max-sm:hidden">#</TableHeadCell>
                    <TableHeadCell class="max-sm:hidden">{t('logs.time')}</TableHeadCell>
                    <TableHeadCell>{t('common.status')}</TableHeadCell>
                    <TableHeadCell class="max-lg:hidden">{t('btn.download')}</TableHeadCell>
                    <TableHeadCell>{t('common.actions')}</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    {#each executionList as exec, execIdx (exec.id)}
                    <TableBodyRow>
                        <TableBodyCell tdClass="{classListContent} text-center max-sm:hidden">
                            {exec.id}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                            <div>{t('logs.time_start_short')}: {exec.time_start}</div>
                            <div>{t('logs.time_fin_short')}: {exec.time_fin}</div>
                            <div>{t('jobs.info.duration')}: {exec.time_duration}</div>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>
                            <div>{t('common.status')}:
                                {#if isJobExecutionActive(exec)}
                                    <span class="text-blue-600">{t('jobs.info.running')}</span>
                                {:else if exec.failed}
                                    <span class="text-red-600">{t('jobs.info.failed')}</span>
                                {:else}
                                    <span class="text-green-600">{t('jobs.info.succeeded')}</span>
                                {/if}
                            </div>
                            <div>{t('logs.executed_by')}: {exec.user_name}</div>
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} max-lg:hidden">
                            {#if exec.log_stdout_url}
                                <div><a href="{exec.log_stdout_url}">{t('logs.exec_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stderr_url}
                                <div><a href="{exec.log_stderr_url}">{t('logs.exec_error_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stdout_repo_url}
                                <div><a href="{exec.log_stdout_repo_url}">{t('logs.repo_log_file')}</a></div>
                            {/if}
                            {#if exec.log_stderr_repo_url}
                                <div><a href="{exec.log_stderr_repo_url}">{t('logs.repo_error_log_file')}</a></div>
                            {/if}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} action-btns">
                            <div class="mt-2">
                                <Button size="xs" on:click={() => {entryExecActions[exec.id] = true}} id="logs-job-{job.id}-{exec.id}-show">
                                    <BookOpenSolid/>
                                </Button>
                                <Tooltip>{t('btn.logs')}</Tooltip>
    
                                <Button size="xs" on:click={() => {stopJob(job.id, exec.id)}}
                                    disabled={!isJobExecutionActive(exec)} id="logs-job-{job.id}-{exec.id}-stop">
                                    <StopSolid/>
                                </Button>
                                <Tooltip>{t('btn.stop')}</Tooltip>

                                <Button size="xs" on:click={() => {cleanupJobExecution(job.id, exec.id)}}
                                    disabled={isJobExecutionActive(exec)} id="logs-job-{job.id}-{exec.id}-cleanup">
                                    <TrashBinSolid/>
                                </Button>
                                <Tooltip>{t('btn.delete')}</Tooltip>

                                <!--
                                <Button size="xs" on:click={() => {redirectJob(job.id)}}><CogSolid/></Button>
                                <Tooltip>{t('jobs.job')}</Tooltip>
                                -->
    
                                <LogsView bind:open={entryExecActions[exec.id]}
                                    jobID={job.id} jobName={job.name} bind:exec={executionList[execIdx]} />
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                    {/each}
                </TableBody>
            </Table>
            {/if}
        </AccordionItem>
    {/each}
</Accordion>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
