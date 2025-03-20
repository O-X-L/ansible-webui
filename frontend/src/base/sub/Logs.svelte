<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { BookOpenSolid, StopSolid, CogSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Accordion, AccordionItem, Table, TableBody, TableBodyCell, TableBodyRow,
        TableHead, TableHeadCell, Radio, Button, Tooltip,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import LogsView from './forms/Logs.svelte';
    import { tq } from '../../util/translate.js';
    import { redirectTo } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { classSpinnerDiv, classListContent, classListHeader } from '../Style.js';
    import { JOB_EXEC_STATI_ACTIVE, type jobType, type executionType } from './Config.js';

    let { open = $bindable(false) } = $props();

    const urlParams = new URLSearchParams(window.location.search);
    const JOB_PARAM = 'job';

    let apiResponseHandler: APIResponseHandler = $state();
    let jobList: jobType[] = $state([]);
    let executionList = $state({});
    let entryActions = $state({});
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
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
        // todo: redirect to http://127.0.0.1:8000/ui#jobs?search=id:<job>
        redirectTo(`/ui?job=${jobId}#jobs`, `?job=${jobId}`);
    }

    function loadJobList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        for (let job of j) {
            if (!entryActions[job.id]) {
                entryActions[job.id] = {open: false};
            }
        }
        jobList = j;
        apiDataHash = h;
        if (!loaded) {
            loaded = true;
            openLogsByURL();
        }
    }

    function loadExecutionList(j: any) {
        if (j === null) {
            return;
        }
        for (let exec of j) {
            if (!entryActions[openJob][exec.id]) {
                entryActions[openJob][exec.id] = false;
            }
        }
        executionList[openJob] = j;
    }

    function buildUpdateJobList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`job?hash=${apiDataHash}`, loadJobList);
    }

    function buildUpdateExecutionList(actions: any) {
        let anyOpen = false;
        let openJobID = 0;
        for (let [j, v] of Object.entries(actions)) {
            if (v.open) {
                anyOpen = true;
                openJobID = j;
                break;
            }
        }
        if (!anyOpen || openJobID == openJob) {
            return;
        }
        openJob = openJobID;
        executionList[openJob] = [];

        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`job_exec/${openJob}?execution_count=${executionCount}`, loadExecutionList);
    }

    function openLogsByURL() {
        let paramJob = urlParams.get(JOB_PARAM);
        if (!paramJob) {
            return;
        }
        for (let job of jobList) {
            if (String(job.id) == String(paramJob)) {
                entryActions[job.id]['open'] = true;
                let e = document.getElementById(`logs-${job.id}`);
                if (e) {
                    e.scrollIntoView({behavior: "smooth", block: "start", inline: "start"});
                }
                break;
            }
        }
    }

    $effect(() => {
        buildUpdateExecutionList(entryActions);
    });

    onMount(() => {
        buildUpdateJobList();

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

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:successMsg={apiSuccessMsg} />

<Accordion>
    {#each jobList as job (job.id)}
        <AccordionItem bind:open={entryActions[job.id]['open']}>
            <span slot="header">{job.name}</span>
            {#if !executionList[job.id] || !executionList[job.id].length}
                <div class={classSpinnerDiv}><Spinner/></div>
            {:else}
            <Table striped={true} id="logs-{job.id}">
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell>{t('logs.time')}</TableHeadCell>
                    <TableHeadCell>{t('common.status')}</TableHeadCell>
                    <TableHeadCell class="max-lg:hidden">{t('btn.download')}</TableHeadCell>
                    <TableHeadCell>{t('common.actions')}</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    {#each executionList[job.id] as exec, execIdx (exec.id)}
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
                        <TableBodyCell tdClass={classListContent}>
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
                            <LogsView bind:open={entryActions[job.id][exec.id]}
                                jobID={job.id} jobName={job.name} bind:exec={executionList[job.id][execIdx]} />
                            <Button size="xs" on:click={() => {entryActions[job.id][exec.id] = true}}><BookOpenSolid/></Button>
                            <Tooltip>{t('btn.logs')}</Tooltip>

                            <Button size="xs" on:click={() => {stopJob(job.id, exec.id)}}
                                disabled={!isJobExecutionActive(exec)}>
                                <StopSolid/>
                            </Button>
                            <Tooltip>{t('btn.stop')}</Tooltip>

                            <Button size="xs" on:click={() => {redirectJob(job.id)}}><CogSolid/></Button>
                            <Tooltip>{t('jobs.job')}</Tooltip>
                        </TableBodyCell>
                    </TableBodyRow>
                    {/each}
                </TableBody>
            </Table>
            {/if}
        </AccordionItem>
    {/each}
</Accordion>
