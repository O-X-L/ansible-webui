<script lang="ts">
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
        CloseCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip, Modal, Heading,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Input, Toggle, Label, Select,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import JobForm from './forms/Job.svelte';
    import { classModalLabel } from '../Style.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import { choicesFromArray } from '../../util/form.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { type executionPromptsType, API_STATUS_CODES_OK } from './Config.js';
    import {
        classModalBackdrop, classModalBtns, classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div, classCenterChildDiv, classSpinnerDiv,
        classListContent, classListHeader,
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
        execution_prompts_json: string|null,
        next_run: string|null,
        executions: executionInfos[],
    }

    const JOB_EXEC_STATI_ACTIVE = [0, 1, 2, 7];

    let apiResponseHandler: APIResponseHandler = $state();
    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let entryList: jobInfos[] = $state([]);
    let entryActions = $state({});
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');

    interface executionPromptsFieldValues {
        tags: string,
        tags_skip: string,
        mode_check: boolean,
        mode_diff: boolean,
        limit: string,
        environment_vars: string,
        cmd_args: string,
        credentials: number|null,
    }
    interface executionPromptsFullType {
        config: executionPromptsType,
        field_values: executionPromptsFieldValues,
        var_values: any,
    }
    interface credentialType {
        id: number,
        name: string,
    }
    interface credentialsType {
        shared: credentialType[],
        user: credentialType[],
    }

    const executionPromptsDefault: executionPromptsFullType = {
        config: {enforce: false, fields: [], vars: []},
        field_values: {
            tags: '', tags_skip: '', mode_check: false, mode_diff: false, limit: '',
            environment_vars: '', cmd_args: '', credentials: null,
        },
        var_values: {},
    }

    let executionPrompts: executionPromptsFullType = $state(JSON.parse(JSON.stringify(executionPromptsDefault)));
    let usableCredentials: credentialsType = $state({shared: [], user: []});
    let usableCredentialChoices = $derived(buildCredentialChoices(usableCredentials));

    function t(code: string) {
      return tq($share, code);
    }

    function loadJobList(j: any, h: string) {
        for (let job of j) {
            if (!entryActions[job.id]) {
                entryActions[job.id] = {edit: false, clone: false, exec: false, logs: false};
            }
        }
        if (!j || h == apiDataHash) {
            return;
        }
        entryList = j;
        apiDataHash = h;
    }

    function isJobActive(job: jobInfos) {
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

    function startJob(jobId: number) {
        if (!jobId) {
            return;
        }
        let promptData = {};

        for (let f of executionPrompts.config.fields) {
            promptData[f] = executionPrompts.field_values[f];
        }

        if (executionPrompts.config.vars.length) {
            let c: string[] = [];

            for (let [k, v] of Object.entries(executionPrompts.var_values)) {
                if (v && v.trim()) {
                    c.push(`-e "${k}=${v}"`)
                }
            }

            if (c.length) {
                if (!executionPrompts.config.fields.includes('cmd_args')) {
                    promptData['cmd_args'] = '';
                }
                promptData['cmd_args'] += ` ${c.join(' ')}`
            }
        }

        apiSuccessMsg = 'jobs.action.start';
        apiEdit('post', `job/${jobId}`, promptData, apiResponseHandler.handleRes);
        entryActions[jobId].exec = false;
    }

    function updateExecutionPrompts(encodedPrompts: string|null) {
        executionPrompts = JSON.parse(JSON.stringify(executionPromptsDefault));
        if (!encodedPrompts) {
            return;
        }
        executionPrompts.config = JSON.parse(encodedPrompts);
    }

    function loadCredentialInfos(j: any) {
        usableCredentials = j;
    }

    function buildCredentialChoices(cr: credentialsType) {
        let choices = [];
        for (let c of cr.user) {
            choices.push({value: c.id, name: `${t('creds.user')} - ${c.name}`});
        }
        for (let c of cr.shared) {
            choices.push({value: c.id, name: `${t('creds.shared')} - ${c.name}`});
        }
        return choices;
    }

    function buildUpdateJobList() {
        if (typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`job?executions=true&execution_count=1&hash=${apiDataHash}`, loadJobList);
    }

    // todo: refresh data over websockets
    setInterval(() => {
        buildUpdateJobList();
    }, $share.updateInterval)

    onMount(() => {
        buildUpdateJobList();
        apiGet('credentials', loadCredentialInfos);
    })
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:successMsg={apiSuccessMsg} />

<div>
  <Table striped={true}>
    <TableHead theadClass={classListHeader}>
        <TableHeadCell>{t('jobs.job')}</TableHeadCell>
        <TableHeadCell class="max-lg:hidden">{t('jobs.form.inventory_file')}</TableHeadCell>
        <TableHeadCell class="max-lg:hidden">{t('jobs.form.playbook_file')}</TableHeadCell>
        <TableHeadCell class="max-sm:hidden">{t('jobs.form.schedule')}</TableHeadCell>
        <TableHeadCell>{t('common.actions')}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each entryList as job (job.id)}
            <TableBodyRow>
                <TableBodyCell tdClass={classListContent}>
                    {job.name}
                    <button id="job-name-{job.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">{t('jobs.info')}</span>
                    </button>
                </TableBodyCell>
                <TableBodyCell class="{classListContent} max-lg:hidden">{job.inventory_file ? job.inventory_file : '-'}</TableBodyCell>
                <TableBodyCell class="{classListContent} max-lg:hidden">{job.playbook_file}</TableBodyCell>    
                <TableBodyCell class="{classListContent} max-sm:hidden">
                    {job.next_run ? job.next_run : '-'}
                    <button id="job-schedule-{job.id}" class="ml-1">
                        <InfoCircleSolid size="sm"/>
                        <span class="sr-only">{t('jobs.info.execution')}</span>
                    </button>
                </TableBodyCell>
                <TableBodyCell tdClass={classListContent}>
                    <div>
                        <Button size="xs" on:click={() => {
                            entryActions[job.id].exec = true; updateExecutionPrompts(job.execution_prompts_json);
                            }} disabled={isJobActive(job)}>
                            <PlaySolid/>
                        </Button>
                        <Tooltip>{t('btn.execute')}</Tooltip>

                        <Button size="xs" on:click={() => {stopJob(job.id, job.executions[0].id)}}
                            disabled={!isJobActive(job)} >
                            <StopSolid/>
                        </Button>
                        <Tooltip>{t('btn.stop')}</Tooltip>

                        <Button size="xs" on:click={() => {entryActions[job.id].logs = true}}><BookOpenSolid/></Button>
                        <Tooltip>{t('btn.logs')}</Tooltip>
                    </div>
                    <div class="mt-2">
                        <JobForm bind:open={entryActions[job.id].edit} action='edit' existingID={job.id} />
                        <Button size="xs" on:click={() => {entryActions[job.id].edit = true}}><EditSolid/></Button>
                        <Tooltip>{t('btn.edit')}</Tooltip>
    
                        <JobForm bind:open={entryActions[job.id].clone} action='clone' existingID={job.id} />
                        <Button size="xs" on:click={() => {entryActions[job.id].clone = true}}><FileCloneSolid/></Button>
                        <Tooltip>{t('btn.clone')}</Tooltip>
    
                        <Button size="xs" on:click={() => {deleteJob(job.id)}}><TrashBinSolid/></Button>
                        <Tooltip>{t('btn.delete')}</Tooltip>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
    </TableBody>
  </Table>
  {#if !entryList.length}
    <div class={classSpinnerDiv}><Spinner/></div>
  {/if}
</div>

<div>
    {#each entryList as job (job.id)}
        <div id="job-infos-{job.id}">
            <Popover triggeredBy="#job-name-{job.id}" class={classPopover} placement="bottom-start">
                <div class="p-3 space-y-2">
                    <h3 class={classPopoverTitle}>{t('jobs.info')}</h3>
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
                    <h3 class={classPopoverTitle}>{t('jobs.info.execution')}</h3>
                    <table>
                        <tbody>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    {t('jobs.form.enabled')}:
                                </td>
                                <td class={classPopoverColumn2Div}>
                                    <button class="cursor-default">
                                        <Radio checked={job.enabled}></Radio>
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    {t('jobs.form.cron')}:
                                </td>
                                <td class={classPopoverColumn2Text}>
                                    {job.schedule ? job.schedule : '-'}
                                </td>
                            </tr>
                            <tr>
                                <td class={classPopoverColumn1}>
                                    {t('jobs.info.next_run')}:
                                </td>
                                <td class={classPopoverColumn2Text}>
                                    {job.next_run ? job.next_run : '-'}
                                </td>
                            </tr>
                            {#if job.executions.length}
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        {t('jobs.info.last_run')}:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].time_start}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        {t('common.status')}:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].status_name}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        {t('jobs.info.duration')}:
                                    </td>
                                    <td class={classPopoverColumn2Text}>
                                        {job.executions[0].time_duration}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        {t('jobs.info.failed')}:
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
                                            {t('common.error')}:
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
            <Modal bind:open={entryActions[job.id].exec} size="sm" autoclose={true} placement="top-center" backdropClass={classModalBackdrop}>
                <Heading tag="h2">{t('jobs.execute')}</Heading>

                {#if executionPrompts.config.fields.includes('limit')}
                    <Label for="job_prompt_{job.id}_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
                    <Input id="job_prompt_{job.id}_limit" bind:value={executionPrompts.field_values.limit} />
                {/if}
                <div>
                    {#if executionPrompts.config.fields.includes('mode_check')}
                        <Label for="job_prompt_{job.id}_mode_check" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
                        <div class={classCenterChildDiv}>
                            <Toggle id="job_prompt_{job.id}_mode_check" bind:checked={executionPrompts.field_values.mode_check} />
                        </div>
                    {/if}
                    {#if executionPrompts.config.fields.includes('mode_diff')}
                        <Label for="job_prompt_{job.id}_mode_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
                        <div class={classCenterChildDiv}>
                            <Toggle id="job_prompt_{job.id}_mode_diff" bind:checked={executionPrompts.field_values.mode_diff} />
                        </div>
                    {/if}
                </div>
                {#if executionPrompts.config.fields.includes('tags')}
                    <Label for="job_prompt_{job.id}_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
                    <Input id="job_prompt_{job.id}_tags" bind:value={executionPrompts.field_values.tags} />
                {/if}
                {#if executionPrompts.config.fields.includes('tags_skip')}
                    <Label for="job_prompt_{job.id}_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
                    <Input id="job_prompt_{job.id}_tags_skip" bind:value={executionPrompts.field_values.tags_skip} />
                {/if}
                {#if executionPrompts.config.fields.includes('environment_vars')}
                    <Label for="job_prompt_{job.id}_env_vars" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
                    <Input id="job_prompt_{job.id}_env_vars" bind:value={executionPrompts.field_values.environment_vars} />
                {/if}
                {#if executionPrompts.config.fields.includes('cmd_args')}
                    <Label for="job_prompt_{job.id}_cmd_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
                    <Input id="job_prompt_{job.id}_cmd_args" bind:value={executionPrompts.field_values.cmd_args} />
                {/if}
                {#if executionPrompts.config.fields.includes('credentials')}
                    <Label for="job_prompt_{job.id}_creds" class={classModalLabel}>{t('jobs.form.credentials')}</Label>
                    <Select id="job_prompt_{job.id}_creds" items={usableCredentialChoices}
                        bind:value={executionPrompts.field_values.credentials} />
                {/if}
                {#each executionPrompts.config.vars as v, i (v.name)}
                    {#if v.kind == 'text'}
                        <Label for="job_prompt_{job.id}_var_{i}" class={classModalLabel}>{v.name}</Label>
                        <Input id="job_prompt_{job.id}_var_{i}" bind:value={executionPrompts.var_values[v.varName]} />
                        <!-- todo: regex validation -->
                    {:else}
                        <Label for="job_prompt_{job.id}_var_{i}" class={classModalLabel}>{v.name}</Label>
                        <Select id="job_prompt_{job.id}_var_{i}" items={choicesFromArray(v.choices)}
                            bind:value={executionPrompts.var_values[v.varName]} />
                    {/if}                    
                {/each}

                <div class={classModalBtns}>
                    <!--
                    todo: pass execution-prompt inputs to startJob 
                    todo: validate execution_prompts_enforce
                    -->
                    <Button type="button" on:click={() => {startJob(job.id)}}><PlaySolid/></Button>
                    <Tooltip>{t('btn.execute')}</Tooltip>

                    <Button on:click={() => (entryActions[job.id].exec = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
                    <Tooltip>{t('btn.discard')}</Tooltip>
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
    <JobForm bind:open={addModal} action='add' />
{/key}
