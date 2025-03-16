<script lang="ts">
    import { onMount } from 'svelte';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import JobForm from './JobForm.svelte';
    import { apiGet } from '../../util/api.js';
    import { tq } from '../../util/translate.js';

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

    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let jobList: jobInfos[] = $state([]);
    let jobActions = $state({});

    function t(code: string) {
      return tq($share, code);
    }

    function loadJobList(j: any) {
        for (let job of j) {
            jobActions[job.id] = {edit: false, clone: false, exec: false};
        }
        jobList = j;
    }

    onMount(() => {
        apiGet('job?executions=true&execution_count=1', loadJobList);
    })
</script>

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
                        <Button size="xs" on:click={() => {jobActions[job.id].exec = true}}><PlaySolid/></Button>
                        <Tooltip>{t('btn.execute')}</Tooltip>

                        <Button size="xs" on:click={() => {jobActions[job.id].logs = true}}><BookOpenSolid/></Button>
                        <Tooltip>{t('btn.logs')}</Tooltip>

                        <Button size="xs" on:click={() => {}}><StopSolid/></Button>
                        <Tooltip>{t('btn.stop')}</Tooltip>
                    </div>
                    <div class="mt-2">
                        <JobForm bind:open={jobActions[job.id].edit} action='edit' jobId={job.id} />
                        <Button size="xs" on:click={() => {jobActions[job.id].edit = true}}><EditSolid/></Button>
                        <Tooltip>{t('btn.edit')}</Tooltip>
    
                        <JobForm bind:open={jobActions[job.id].clone} action='clone' jobId={job.id} />
                        <Button size="xs" on:click={() => {jobActions[job.id].clone = true}}><FileCloneSolid/></Button>
                        <Tooltip>{t('btn.clone')}</Tooltip>
    
                        <Button size="xs" on:click={() => {}}><TrashBinSolid/></Button>
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
            <Popover triggeredBy="#job-name-{job.id}" class="w-96 text-sm font-light text-gray-500 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400" placement="bottom-start">
                <div class="p-3 space-y-2">
                    <h3 class="font-semibold text-gray-900 dark:text-white">Job Information</h3>
                </div>
                <table>
                    <tbody>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.comment')}:
                            </td>
                            <td class="text-center">
                                {job.comment ? job.comment : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.inventory_file')}:
                            </td>
                            <td class="text-center">
                                {job.inventory_file ? job.inventory_file : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.playbook_file')}:
                            </td>
                            <td class="text-center">
                                {job.playbook_file}
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.limit')}:
                            </td>
                            <td class="text-center">
                                {job.limit ? job.limit : '-'}
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.mode_diff')}:
                            </td>
                            <td class="flex justify-center">
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.mode_diff}></Radio>
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.mode_check')}:
                            </td>
                            <td class="flex justify-center">
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.mode_check}></Radio>
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold mr-5">
                                {t('jobs.form.credentials_needed')}:
                            </td>
                            <td class="flex justify-center">
                                <button class="cursor-default">
                                    <Radio class="inline-block" checked={job.credentials_needed}></Radio>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </Popover>
            <Popover triggeredBy="#job-schedule-{job.id}" class="w-72 text-sm font-light text-gray-500 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400" placement="bottom-start">
                <div class="p-3 space-y-2">
                    <h3 class="font-semibold text-gray-900 dark:text-white">Execution Information</h3>
                    <table>
                        <tbody>
                            <tr>
                                <td class="font-bold mr-5">
                                    Schedule Enabled:
                                </td>
                                <td class="flex justify-center">
                                    <button class="cursor-default">
                                        <Radio checked={job.enabled}></Radio>
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td class="font-bold mr-5">
                                    Schedule Cron:
                                </td>
                                <td class="text-center">
                                    {job.schedule ? job.schedule : '-'}
                                </td>
                            </tr>
                            <tr>
                                <td class="font-bold mr-5">
                                    Next Run:
                                </td>
                                <td class="text-center">
                                    {job.next_run ? job.next_run : '-'}
                                </td>
                            </tr>
                            {#if job.executions.length}
                                <tr>
                                    <td class="font-bold mr-5">
                                        Last Run:
                                    </td>
                                    <td class="text-center">
                                        {job.executions[0].time_start}
                                    </td>
                                </tr>
                                <tr>
                                    <td class="font-bold mr-5">
                                        Status:
                                    </td>
                                    <td class="text-center">
                                        {job.executions[0].status_name}
                                    </td>
                                </tr>
                                <tr>
                                    <td class="font-bold mr-5">
                                        Duration:
                                    </td>
                                    <td class="text-center">
                                        {job.executions[0].time_duration}
                                    </td>
                                </tr>
                                <tr>
                                    <td class="font-bold mr-5">
                                        Failed:
                                    </td>
                                    <td class="flex justify-center">
                                        <button class="cursor-default">
                                            <Radio class="inline-block" checked={job.executions[0].failed}></Radio>
                                        </button>
                                    </td>
                                </tr>
                                {#if job.executions[0].failed}
                                    <tr>
                                        <td class="font-bold mr-5">
                                            Error:
                                        </td>
                                        <td class="flex justify-center">
                                            <Alert color="red" border>{job.executions[0].error_s}</Alert>
                                        </td>
                                    </tr>
                                {/if}
                            {/if}
                        </tbody>
                    </table>
                </div>
            </Popover>
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
