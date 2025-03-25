<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
        CloseCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip, Modal, Heading,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Input, Toggle, Label, Select,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import JobForm from './forms/Job.svelte';
    import { tq } from '../../util/translate.js';
    import { classModalLabel } from '../Style.js';
    import { type formChoiceType } from '../Types.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import { choicesFromArray } from '../../util/form.js';
    import { redirectTo, isSet } from '../../util/main.js';
    import { JOB_EXEC_STATI_ACTIVE, PARAM_SEARCH } from '../Config.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { type jobType, type executionPromptsType} from './Types.js';
    import {
        classModalBackdrop, classModalBtns, classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div, classCenterChildDiv, classSpinnerDiv,
        classListContent, classListHeader, classFooterSpacing,
    } from '../Style.js';

    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let addModal = $state(false);
    let addModalId = $state(Date.now());
    let entryList: jobType[] = $state([]);
    let entryActions = $state({});
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiError = $state(false);
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    // todo: init search from url-param
    //let tableSearchTerm = $state('');
    //let loaded = $state(false);

    interface executionPromptsFieldValues {
        tags: string,
        tags_skip: string,
        mode_check: boolean,
        mode_diff: boolean,
        limit: string,
        environment_vars: string,
        cmd_args: string,
        credentials: string|null,  // credential_user / credential_global
        credentials_req: boolean,
        comment: string|null,
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
        config: {fields: [], vars: []},
        field_values: {
            tags: '', tags_skip: '', mode_check: false, mode_diff: false, limit: '',
            environment_vars: '', cmd_args: '', credentials: null, credentials_req: false,
            comment: '',
        },
        var_values: {},
    }

    let executionPrompts: executionPromptsFullType = $state(JSON.parse(JSON.stringify(executionPromptsDefault)));
    let usableCredentials: credentialsType = $state({shared: [], user: []});
    let usableCredentialChoices = $derived(buildCredentialChoices(usableCredentials));

    function t(code: string) : string {
      return tq($share, code);
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

    function startJob(jobId: number) {
        if (!jobId) {
            return;
        }
        let promptData = {};

        // validation
        if (executionPrompts.config.fields.includes('limit_req') && !isSet(executionPrompts.field_values.limit)) {
            apiErrorMsg = t('jobs.execute.required_limit');
            apiError = true;
            return;
        }

        if (executionPrompts.config.fields.includes('credentials_req') && !isSet(executionPrompts.field_values.credentials)) {
            apiErrorMsg = t('jobs.execute.required_credentials');
            apiError = true;
            return;
        }

        for (let v of executionPrompts.config.vars) {
            if (v.required && !isSet(executionPrompts.var_values[v.varName])) {
                apiErrorMsg = `${t('jobs.execute.required_var')}: "${v.name}"`;
                apiError = true;
                return;
            }
        }

        // encode prompt info
        for (let f of executionPrompts.config.fields) {
            if(f == 'credentials') {
                if (isSet(executionPrompts.field_values.credentials)) {
                    let credsKind = 'credentials_global';
                    if (executionPrompts.field_values.credentials.includes('user-')) {
                        credsKind = 'credentials_user';
                    }
                    promptData[credsKind] = parseInt(executionPrompts.field_values.credentials?.split('-')[1], 10);
                }
            } else {
                promptData[f] = executionPrompts.field_values[f];
            }
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

    function redirectLogs(jobId: number) {
        if (!jobId) {
            return;
        }
        redirectTo(`/ui#logs-job=${jobId}`);
    }

    function updateExecutionPrompts(encodedPrompts: string|null) {
        executionPrompts = JSON.parse(JSON.stringify(executionPromptsDefault));
        if (!encodedPrompts) {
            return;
        }
        executionPrompts.config = JSON.parse(encodedPrompts);
    }

    function searchFilter(item: jobType, searchTerm: string) : boolean {
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
        apiGet(`job?executions=true&execution_count=1&hash=${apiDataHash}`, loadJobList);
    }

    onMount(() => {
        buildUpdateJobList();
        apiGet('credentials', loadCredentialInfos);

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
                <button id="job-name-{item.id}" class="ml-1">
                    <InfoCircleSolid size="sm"/>
                    <span class="sr-only">{t('jobs.info')}</span>
                </button>
            </TableBodyCell>
            <TableBodyCell class="{classListContent} max-lg:hidden">{item.inventory_file ? item.inventory_file : '-'}</TableBodyCell>
            <TableBodyCell class="{classListContent} max-lg:hidden">{item.playbook_file}</TableBodyCell>    
            <TableBodyCell class="{classListContent} max-sm:hidden">
                {item.next_run ? item.next_run : '-'}
                <button id="job-schedule-{item.id}" class="ml-1">
                    <InfoCircleSolid size="sm"/>
                    <span class="sr-only">{t('jobs.info.execution')}</span>
                </button>
            </TableBodyCell>
            <TableBodyCell tdClass={classListContent}>
                <div>
                    <Button size="xs" on:click={() => {
                        entryActions[item.id].exec = true; updateExecutionPrompts(item.execution_prompts_json);
                        }} disabled={isJobActive(item)} id="jobs-btn-exec-{item.id}">
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
                <div class="mt-2">
                    <JobForm bind:open={entryActions[item.id].edit} action='edit' existingID={item.id}
                        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                    <Button size="xs" on:click={() => {entryActions[item.id].edit = true}} id="jobs-btn-edit-{item.id}">
                        <EditSolid/>
                    </Button>
                    <Tooltip>{t('btn.edit')}</Tooltip>

                    <JobForm bind:open={entryActions[item.id].clone} action='clone' existingID={item.id}
                        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                    <Button size="xs" on:click={() => {entryActions[item.id].clone = true}} id="jobs-btn-clone-{item.id}">
                        <FileCloneSolid/>
                    </Button>
                    <Tooltip>{t('btn.clone')}</Tooltip>

                    <Button size="xs" on:click={() => {deleteJob(item.id)}} id="jobs-btn-delete-{item.id}">
                        <TrashBinSolid/>
                    </Button>
                    <Tooltip>{t('btn.delete')}</Tooltip>
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
                                        <Radio checked={job.enabled && isSet(job.schedule)}></Radio>
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
                {#if executionPrompts.config.fields.includes('comment')}
                    <Label for="job_prompt_{job.id}_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
                    <Input id="job_prompt_{job.id}_cmt" bind:value={executionPrompts.field_values.comment} />
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
                    <Button id="jobs-btn-exec-start" type="button" on:click={() => {startJob(job.id)}}><PlaySolid/></Button>
                    <Tooltip>{t('btn.execute')}</Tooltip>

                    <Button id="jobs-btn-exec-close" on:click={() => (entryActions[job.id].exec = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
                    <Tooltip>{t('btn.close')}</Tooltip>
                </div>
            </Modal>
            
        </div>
    {/each}
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
