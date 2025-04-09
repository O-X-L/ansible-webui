<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { BookOpenSolid, StopSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Accordion, AccordionItem, Table, TableBody, TableBodyCell, TableBodyRow,
        TableHead, TableHeadCell, Radio, Button, Tooltip,
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
        classSpinnerDiv, classListContent, classListHeader, classFooterSpacing, classSpoilerItem,
    } from '../Style.js';

    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let jobList: jobType[] = $state([]);
    let executionList: executionType[] = $state([]);
    let entryJobActions = $state({});
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

    function redirectJob(jobId: number) {
        if (!jobId) {
            return;
        }
        redirectTo(`/ui#jobs-search=id:${jobId}`);
    }

    function loadJobList(j: any, h: string) {
        if (j === null || h == apiDataHashJobs) {
            return;
        }
        for (let job of j) {
            if (!entryJobActions[job.id]) {
                entryJobActions[job.id] = false;
            }
        }
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
        apiGet(`job_exec/${openJob}?execution_count=${executionCount}&hash=${apiDataHashExecs}`, loadExecutionList);
    }

    function openLogsByURL() {
        let params = getURLHashParams();
        if (!params[PARAM_JOB]) {
            return;
        }
        for (let job of jobList) {
            if (String(job.id) == String(params[PARAM_JOB])) {
                entryJobActions[job.id] = true;
                let e = document.getElementById(`logs-${job.id}`);
                if (e) {
                    e.scrollIntoView({behavior: "smooth", block: "start", inline: "start"});
                }
                break;
            }
        }
    }

    function updateOpenJob(actions: any = ''){
        for (let [j, v] of Object.entries(actions)) {
            if (v) {
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

<Accordion>
    {#each jobList as job (job.id)}
        <AccordionItem bind:open={entryJobActions[job.id]} defaultClass="{classSpoilerItem} logs-job-{job.id}">
            <span slot="header">{job.name}</span>
            {#if !executionList.length}
                <div class={classSpinnerDiv}><Spinner/></div>
            {:else}
            <Table striped={true} id="logs-{job.id}" shadow>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell>{t('logs.time')}</TableHeadCell>
                    <TableHeadCell>{t('common.status')}</TableHeadCell>
                    <TableHeadCell class="max-lg:hidden">{t('btn.download')}</TableHeadCell>
                    <TableHeadCell>{t('common.actions')}</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    {#each executionList as exec, execIdx (exec.id)}
                    <TableBodyRow>
                        <TableBodyCell tdClass={classListContent}>
                            <div>{t('logs.time_start_short')}: {exec.time_start}</div>
                            <div>{t('logs.time_fin_short')}: {exec.time_fin}</div>
                            <div>{t('jobs.info.duration')}: {exec.time_duration}</div>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>
                            <div>{t('common.status')}: {exec.status_name}</div>
                            <div>{t('logs.executed_by')}: {exec.user_name}</div>
                            <div>{t('jobs.info.failed')}: 
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={exec.failed}></Radio>
                                </button>
                            </div>
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
                        <TableBodyCell tdClass={classListContent}>
                            <LogsView bind:open={entryExecActions[exec.id]}
                                jobID={job.id} jobName={job.name} bind:exec={executionList[execIdx]} />
                            <Button size="xs" on:click={() => {entryExecActions[exec.id] = true}}
                                id="logs-job-{job.id}-show">
                                <BookOpenSolid/>
                            </Button>
                            <Tooltip>{t('btn.logs')}</Tooltip>

                            <Button size="xs" on:click={() => {stopJob(job.id, exec.id)}}
                                disabled={!isJobExecutionActive(exec)} id="logs-job-{job.id}-stop">
                                <StopSolid/>
                            </Button>
                            <Tooltip>{t('btn.stop')}</Tooltip>
                            
                            <!--
                            <Button size="xs" on:click={() => {redirectJob(job.id)}}><CogSolid/></Button>
                            <Tooltip>{t('jobs.job')}</Tooltip>
                            -->
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
