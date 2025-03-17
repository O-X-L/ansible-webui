<script lang="ts">
    import { onMount } from 'svelte';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
        CloseCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip, Modal, Heading,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import JobForm from './forms/Job.svelte';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import {
        classModalBackdrop, classModalBtns, classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div,
    } from '../Style.js';

    interface executionInfos {
        id: number,
        job: number,
        user: number,
        user_name: string,
        result: number,
        status: number,
        status_name: string,
        log_stdout: string|null,
        log_stdout_url: string|null,
        log_stderr: string|null,
        log_stderr_url: string|null,
        comment: string|null,
        credential_global: number|null,
        credential_user: number|null,
        command: string|null,
        log_stdout_repo: string|null,
        log_stderr_repo: string|null,
        log_stdout_repo_url: string|null,
        log_stderr_repo_url: string|null,
        job_name: string,
        job_comment: string,
        time_start: string,
        time_fin: string,
        failed: boolean,
        error_s: string|null,
        error_m: string|null,
        time_duration: string,
    }

    interface jobInfos {
        id: number,
        name: string,
        playbook_file: string,
        inventory_file: string,
        repository: number|null,
        schedule: string|null,
        enabled: boolean,
        limit: string,
        verbosity: number,
        mode_diff: boolean,
        mode_check: boolean,
        tags: string,
        tags_skip: string,
        comment: string,
        environment_vars: string,
        cmd_args: string,
        credentials_default: number|null,
        credentials_needed: boolean,
        credentials_category: string|null,
        execution_prompts: string|null,
        next_run: string|null,
        executions: executionInfos[],
    }

    const apiErrorAlert = 'api-job-alert';
    const JOB_EXEC_STATI_ACTIVE = [0, 1, 2, 7];

    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let jobList: jobInfos[] = $state([]);
    let jobActions = $state({});
    let apiError = $state('');

    function t(code: string) {
      return tq($share, code);
    }

    function loadJobList(j: any) {
        for (let job of j) {
            jobActions[job.id] = {edit: false, clone: false, exec: false, logs: false};
        }
        jobList = j;
    }

    function isJobActive(job: jobInfos) {
        if (!job.executions.length) {
            return false;
        }
        return JOB_EXEC_STATI_ACTIVE.includes(job.executions[0].status);
    }

    function showAPIErrors(s: number, j: any) {
        if (s != 200 || j.error !== undefined) {
            apiError = `${j.error} (${s})`;  // todo: pull language-code from api-error and show user the translation
            let a = document.getElementById(apiErrorAlert);
            if (a) {
                a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            }
        }
    }

    function stopJob(jobId: number, executionId: number) {
        if (!jobId || !executionId) {
            return;
        }
        apiEdit('delete', `job/${jobId}/${executionId}`, null, showAPIErrors);
    }

    function deleteJob(jobId: number) {
        if (!jobId) {
            return;
        }
        apiEdit('delete', `job/${jobId}`, null, showAPIErrors);
    }

    function startJob(jobId: number) {
        if (!jobId) {
            return;
        }
        apiEdit('post', `job/${jobId}`, undefined, showAPIErrors);
    }

    // todo: refresh data on changes

    onMount(() => {
        apiGet('job?executions=true&execution_count=1', loadJobList);
    })
</script>

<div id={apiErrorAlert} class="h-0"></div>
{#if apiError}
    <Alert border color="red">
        <CloseCircleSolid slot="icon" class="w-5 h-5" /> {apiError}
    </Alert>
{/if}
<div>
  <Table striped={true}>
    <TableHead theadClass="text-base font-bold uppercase">
        <TableHeadCell>Job</TableHeadCell>
        <TableHeadCell class="max-lg:hidden">{t('jobs.form.inventory_file')}</TableHeadCell>
        <TableHeadCell class="max-lg:hidden">{t('jobs.form.playbook_file')}</TableHeadCell>
        <TableHeadCell class="max-sm:hidden">{t('jobs.form.schedule')}</TableHeadCell>
        <TableHeadCell>Actions</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#if !jobList.length}
            <div class="text-center mt-20"><Spinner/></div>
        {/if}
        {#each jobList as job (job.id)}
            <TableBodyRow>
                <TableBodyCell>
                    {job.name}
                    <button id="job-name-{job.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">Show Job Information</span>
                    </button>
                </TableBodyCell>
                <TableBodyCell class="max-lg:hidden">{job.inventory_file ? job.inventory_file : '-'}</TableBodyCell>
                <TableBodyCell class="max-lg:hidden">{job.playbook_file}</TableBodyCell>    
                <TableBodyCell class="max-sm:hidden">
                    {job.next_run ? job.next_run : '-'}
                    <button id="job-schedule-{job.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">Show Execution Information</span>
                    </button>
                </TableBodyCell>
                <TableBodyCell>
                    <div>
                        <Button size="xs" on:click={() => {jobActions[job.id].exec = true}} disabled={isJobActive(job)}>
                            <PlaySolid/>
                        </Button>
                        <Tooltip>{t('btn.execute')}</Tooltip>

                        <Button size="xs" on:click={() => {stopJob(job.id, job.executions[0].id)}}
                            disabled={!isJobActive(job)} >
                            <StopSolid/>
                        </Button>
                        <Tooltip>{t('btn.stop')}</Tooltip>

                        <Button size="xs" on:click={() => {jobActions[job.id].logs = true}}><BookOpenSolid/></Button>
                        <Tooltip>{t('btn.logs')}</Tooltip>
                    </div>
                    <div class="mt-2">
                        <JobForm bind:open={jobActions[job.id].edit} action='edit' jobId={job.id} />
                        <Button size="xs" on:click={() => {jobActions[job.id].edit = true}}><EditSolid/></Button>
                        <Tooltip>{t('btn.edit')}</Tooltip>
    
                        <JobForm bind:open={jobActions[job.id].clone} action='clone' jobId={job.id} />
                        <Button size="xs" on:click={() => {jobActions[job.id].clone = true}}><FileCloneSolid/></Button>
                        <Tooltip>{t('btn.clone')}</Tooltip>
    
                        <Button size="xs" on:click={() => {deleteJob(job.id)}}><TrashBinSolid/></Button>
                        <Tooltip>{t('btn.delete')}</Tooltip>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
    </TableBody>
  </Table>
</div>

<div>
    {#each jobList as job (job.id)}
        <div id="job-infos-{job.id}">
            <Popover triggeredBy="#job-name-{job.id}" class={classPopover} placement="bottom-start">
                <div class="p-3 space-y-2">
                    <h3 class={classPopoverTitle}>Job Information</h3>
                </div>
                <table>
                    <tbody>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.comment')}:
                            </td>
                            <td class={classPopoverColumn2Text}>
                                {job.comment ? job.comment : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.inventory_file')}:
                            </td>
                            <td class={classPopoverColumn2Text}>
                                {job.inventory_file ? job.inventory_file : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.playbook_file')}:
                            </td>
                            <td class={classPopoverColumn2Text}>
                                {job.playbook_file}
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.limit')}:
                            </td>
                            <td class={classPopoverColumn2Text}>
                                {job.limit ? job.limit : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.mode_diff')}:
                            </td>
                            <td class={classPopoverColumn2Div}>
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.mode_diff}></Radio>
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.mode_check')}:
                            </td>
                            <td class={classPopoverColumn2Div}>
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.mode_check}></Radio>
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('jobs.form.credentials_needed')}:
                            </td>
                            <td class={classPopoverColumn2Div}>
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.credentials_needed}></Radio>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </Popover>
            <Popover triggeredBy="#job-schedule-{job.id}" class={classPopover} placement="bottom-start">
                <div class="p-3 space-y-2">
                    <h3 class={classPopoverTitle}>Execution Information</h3>
                    <table>
                        <tbody>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    Schedule Enabled:
                                </td>
                                <td class={classPopoverColumn2Div}>
                                    <button class="cursor-default">
                                        <Radio checked={job.enabled}></Radio>
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    Schedule Cron:
                                </td>
                                <td class={classPopoverColumn2Text}>
                                    {job.schedule ? job.schedule : '-'}
                                </td>
                            </tr>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    Next Run:
                                </td>
                                <td class={classPopoverColumn2Text}>
                                    {job.next_run ? job.next_run : '-'}
                                </td>
                            </tr>
                            {#if job.executions.length}
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        Last Run:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].time_start}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        Status:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].status_name}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        Duration:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].time_duration}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        Failed:
                                    </td>
                                    <td class={classPopoverColumn2Div}>
                                        <button class="cursor-default">
                                            <Radio class="inline-block" checked={job.executions[0].failed}></Radio>
                                        </button>
                                    </td>
                                </tr>
                                {#if job.executions[0].failed}
                                    <tr>
                                        <td class={classPopoverColumn1}>
                                            Error:
                                        </td>
                                        <td class={classPopoverColumn2Div}>
                                            <Alert color="red" border>{job.executions[0].error_s}</Alert>
                                        </td>
                                    </tr>
                                {/if}
                            {/if}
                        </tbody>
                    </table>
                </div>
            </Popover>
            <Modal bind:open={jobActions[job.id].exec} size="sm" autoclose={true} placement="top-center" backdropClass={classModalBackdrop}>
                <Heading tag="h2">Execute Job</Heading>

                Execution Prompts HERE

                <div class={classModalBtns}>
                    <!-- todo: pass execution-prompt inputs to startJob -->
                    <Button type="button" on:click={() => {startJob(job.id)}}>{t('btn.execute')}</Button>
                    <Button on:click={() => (jobActions[job.id].exec = false)} class="inline-block">{t('btn.discard')}</Button>
                </div>
            </Modal>
            
        </div>
    {/each}
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button on:click={() => {addModalId = Date.now(); addModal = true}}>{t('btn.add')}</Button>
    </div>    
</div>

{#key addModalId}
    <JobForm bind:open={addModal} action='add' ></JobForm>
{/key}
