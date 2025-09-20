<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, PlaySolid, StopSolid, TrashBinSolid, EditSolid, FileCloneSolid, BookOpenSolid,
        CloseCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip, Heading,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Input, Toggle, Label, Select,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import JobForm from './forms/Job.svelte';
    import { tq } from '../../util/translate.js';
    import { classModalLabel } from '../Style.js';
    import { JOB_EXEC_STATI_ACTIVE } from '../Config.js';
    import { choicesFromArray } from '../../util/form.js';
    import { redirectTo, isSet } from '../../util/main.js';
    import CredentialsForm from './forms/Credentials.svelte';
    import { apiEdit, apiGet, cacheKey } from '../../util/api.js';
    import { type jobType, type executionPromptsType,} from './Types.js';
    import { type formChoiceType, type formInfoType } from '../Types.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { getURLHashParams, setURLHashParams, URL_HASH_PARAM_SEPARATOR, URL_HASH_PARAM_KV } from '../../util/main.js';
    import {
        classModalBackdrop, classModalBtns, classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div, classCenterChildDiv, classSpinnerDiv,
        classListContent, classListHeader, classFooterSpacing, classModalDialog, classModalBody,
    } from '../Style.js';

    const URL_HASH = 'jobs';
    const HASH_PARAM_EXEC = 'exec';
    const HASH_PARAM_EDIT = 'edit';

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
    let loaded = $state(false);

    interface executionPromptsFieldValues {
        tags: string,
        tags_skip: string,
        mode_check: boolean,
        mode_diff: boolean,
        limit: string,
        environment_vars: string,
        cmd_args: string,
        credentials: string|null,  // credential_user / credential_global / credentials_tmp
        credentials_req: boolean,
        comment: string|null,
        verbosity: number,
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

    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    const executionPromptsDefault: executionPromptsFullType = {
        config: {fields: [], vars: []},
        field_values: {
            tags: '', tags_skip: '', mode_check: false, mode_diff: false, limit: '',
            environment_vars: '', cmd_args: '', credentials: null, credentials_req: false,
            comment: '', verbosity: 0,
        },
        var_values: {},
    }

    let executionPrompts: executionPromptsFullType = $state(JSON.parse(JSON.stringify(executionPromptsDefault)));
    let usableCredentials: credentialsType = $state({shared: [], user: []});
    let usableCredentialChoices = $derived(buildCredentialChoices(usableCredentials));
    let addTMPCredsModal = $state(false);
    let addTMPCredsModalId = $state(Date.now());

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
        setURLHashParams(URL_HASH, {exec: job.id});
        entryActions[job.id].exec = true;
        updateExecutionPrompts(job);
    }

    function closeExecutionPrompt(jobId: number) {
        setURLHashParams(URL_HASH, null);
        entryActions[jobId].exec = false;
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
            let c = executionPrompts.var_values[v.varName];
            if (v.required && !isSet(c)) {
                apiErrorMsg = `${t('jobs.execute.required_var')}: "${v.name}"`;
                apiError = true;
                return;
            }
            if (isSet(executionPrompts.var_values[v.varName]) && isSet(v.regex) && !c.match(v.regex)) {
                apiErrorMsg = `${t('jobs.execute.regex_mismatch')}: "${v.name}" - "${v.regex}"`;
                apiError = true;
                return;
            }
        }

        // encode prompt info
        for (let f of executionPrompts.config.fields) {
            if (['credentials_tmp', 'credentials'].includes(f) && isSet(executionPrompts.field_values.credentials)) {
                if (f == 'credentials_tmp') {
                    promptData['credentials_tmp'] = executionPrompts.field_values.credentials;

                } else if (f == 'credentials') {
                    if (executionPrompts.config.fields.includes('credentials_tmp')) {
                        continue;
                    }
                    let credsKind = 'credentials_shared';
                    if (executionPrompts.field_values.credentials.includes('user-')) {
                        credsKind = 'credentials_user';
                    }
                    promptData[credsKind] = parseInt(executionPrompts.field_values.credentials?.split('-')[1], 10);
                }
            } else if (f != 'credentials_req') {
                promptData[f] = executionPrompts.field_values[f];
            }
        }

        if (executionPrompts.config.vars.length) {
            let c: string[] = [];

            for (let [k, v] of Object.entries(executionPrompts.var_values)) {
                if (v && v.trim()) {
                    c.push(`-e "${k}='${v}'"`)
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
        setURLHashParams(URL_HASH, null);
    }

    function redirectLogs(jobId: number) {
        if (!jobId) {
            return;
        }
        redirectTo(`/ui#logs${URL_HASH_PARAM_SEPARATOR}job${URL_HASH_PARAM_KV}${jobId}`);
    }

    function updateExecutionPrompts(job: jobType) {
        executionPrompts = JSON.parse(JSON.stringify(executionPromptsDefault));
        if (!job.execution_prompts_json) {
            return;
        }
        executionPrompts.config = JSON.parse(job.execution_prompts_json);

        // set default values as configured for job
        executionPrompts.field_values.mode_check = job.mode_check;
        executionPrompts.field_values.mode_diff = job.mode_diff;
        executionPrompts.field_values.credentials_req = job.credentials_needed;
        if (job.tags) {
            executionPrompts.field_values.tags = job.tags;
        }
        if (job.tags_skip) {
            executionPrompts.field_values.tags_skip = job.tags_skip;
        }
        if (job.limit) {
            executionPrompts.field_values.limit = job.limit;
        }
        if (job.verbosity) {
            executionPrompts.field_values.verbosity = job.verbosity;
        }
        if (job.environment_vars) {
            executionPrompts.field_values.environment_vars = job.environment_vars;
        }
        if (job.cmd_args) {
            executionPrompts.field_values.cmd_args = job.cmd_args;
        }
    }

    function handleExecutionCredentialsCreateResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            executionPrompts.field_values.credentials = j.id;
            apiSuccessMsg = 'creds.action.create';
            apiSuccess = true;
            addTMPCredsModal = false;
        } else {
            apiResponseHandler.handleRes(s, j);
        }
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
        apiGet(`job?executions=true&execution_count=1&hash=${apiDataHash}`, loadJobList);
    }

    function openModalByURL() {
        let params = getURLHashParams();
        let action = null;
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

    function updateURLHash(_: any) {
      // remove hash-params from URL if modals were closed
      if (!loaded) {
        return;
      }
      let any_open = false;
      for (let job of Object.keys(entryActions)) {
        if (entryActions[job].exec || entryActions[job].edit) {
            any_open = true;
            break;
        }
      }
      if (!any_open) {
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
            <TableBodyCell tdClass="{classListContent} action-btns">
                <div class="mt-4">
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
                <div class="mt-2">
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
                </div>

                <JobForm bind:open={entryActions[item.id].edit} action='edit' existingID={item.id}
                bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                <JobForm bind:open={entryActions[item.id].clone} action='clone' existingID={item.id}
                bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

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
                                {t('common.comment')}:
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
                                    <td class="{classPopoverColumn1} pt-3">
                                        {t('jobs.info.last_run')}:
                                    </td>
                                    <td class="{classPopoverColumn2Text} pt-3">
                                        {job.executions[0].time_start}
                                    </td>
                                </tr>
                                <tr>
                                    <td class={classPopoverColumn1}>
                                        {t('common.status')}:
                                    </td>
                                    <td class="{classPopoverColumn2Text} {job.executions[0].status_name == 'Failed' ? 'text-red-600' : 'text-green-600'}">
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
            <Modal bind:open={entryActions[job.id].exec} size="sm" autoclose={false} placement="top-center"
                backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
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
                {#if executionPrompts.config.fields.includes('credentials') && !executionPrompts.config.fields.includes('credentials_tmp')}
                    <Label for="job_prompt_{job.id}_creds" class={classModalLabel}>{t('jobs.form.credentials')}</Label>
                    <Select id="job_prompt_{job.id}_creds" items={usableCredentialChoices}
                        bind:value={executionPrompts.field_values.credentials} />
                {/if}
                {#if executionPrompts.config.fields.includes('comment')}
                    <Label for="job_prompt_{job.id}_cmt" class={classModalLabel}>{t('common.comment')}</Label>
                    <Input id="job_prompt_{job.id}_cmt" bind:value={executionPrompts.field_values.comment} />
                {/if}
                {#if executionPrompts.config.fields.includes('verbosity')}
                    <Label for="job_prompt_{job.id}_verb" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
                    <Select id="job_prompt_{job.id}_verb" items={formInfos.choices.verbosity}
                        bind:value={executionPrompts.field_values.verbosity} />
                {/if}
                {#each executionPrompts.config.vars as v, i (v.name)}
                    {#if v.kind == 'text'}
                        <Label for="job_prompt_{job.id}_var_{i}" class={classModalLabel}>{v.name}</Label>
                        <Input id="job_prompt_{job.id}_var_{i}" bind:value={executionPrompts.var_values[v.varName]} />
                    {:else}
                        <Label for="job_prompt_{job.id}_var_{i}" class={classModalLabel}>{v.name}</Label>
                        <Select id="job_prompt_{job.id}_var_{i}" items={choicesFromArray(v.choices)}
                            bind:value={executionPrompts.var_values[v.varName]} />
                    {/if}                    
                {/each}
                <div class={classModalBtns}>
                    {#if executionPrompts.config.fields.includes('credentials_tmp')}
                        <Button type="button" on:click={() => {addTMPCredsModalId = Date.now(); addTMPCredsModal = true}}
                            disabled={executionPrompts.field_values.credentials != null}>
                            {t('jobs.execute.tmp_credentials')}
                        </Button>
                    {/if}
                </div>
                <div class={classModalBtns}>
                    <Button id="jobs-btn-exec-start" type="button" on:click={() => {startJob(job.id)}}><PlaySolid/></Button>
                    <Tooltip>{t('btn.execute')}</Tooltip>

                    <Button id="jobs-btn-exec-close" on:click={() => (closeExecutionPrompt(job.id))} class="inline-block ml-2">
                        <CloseCircleSolid/>
                    </Button>
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
{#if executionPrompts.config.fields.includes('credentials_tmp')}
    {#key addTMPCredsModalId}
        <CredentialsForm bind:open={addTMPCredsModal} action='add' kind='tmp'
            bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} customResponseHandler={handleExecutionCredentialsCreateResponse} />
   
    {/key}
{/if}


<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
