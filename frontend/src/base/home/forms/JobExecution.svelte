<script lang="ts">
    import { onMount } from 'svelte';

    import {
        PlaySolid, CloseCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Button, Tooltip, Heading,
        Input, Toggle, Label, Select,
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { classModalLabel } from '../../Style.js';
    import { choicesFromArray } from '../../../util/form.js';
    import { isSet } from '../../../util/main.js';
    import { redirectLogs } from '../util/JobUtils';
    import CredentialsForm from './Credentials.svelte';
    import InventoryListField from './fields/InventoryListField.svelte';
    import { apiEdit } from '../../../util/api.js';
    import type { jobType, executionPromptsType } from '../Types.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import type { formChoiceType, inputColorType } from '../../Types.js';
    import { setURLHashParams } from '../../../util/main.js';
    import {
        classModalBackdrop, classModalBtns, classCenterChildDiv, classModalDialog, classModalBody,
    } from '../../Style.js';

    const URL_HASH = 'jobs';

    let {
        open = $bindable(false),
        job = $bindable(null),
        usableCredentialChoices = [],
        formChoices = $bindable({}),
        apiResponseHandler = $bindable(null),
        apiSuccessMsg = $bindable(''),
        apiSuccess = $bindable(false),
        apiErrorMsg = $bindable(''),
        apiError = $bindable(false),
    } : {
        open: boolean,
        job: jobType,
        formChoices: formChoiceType,
        usableCredentialChoices: formChoiceType[],
        apiResponseHandler: APIResponseHandler,
        apiSuccessMsg: string,
        apiSuccess: boolean,
        apiErrorMsg: string,
        apiError: boolean,
    } = $props();

    let jobStarted = $state(false);

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
        extra_vars: string,
    }
    interface executionPromptsFullType {
        config: executionPromptsType,
        field_values: executionPromptsFieldValues,
        var_values: Record<string, any>,
    }

    const executionPromptsDefault: executionPromptsFullType = {
        config: {fields: [], vars: []},
        field_values: {
            tags: '', tags_skip: '', mode_check: false, mode_diff: false, limit: '',
            environment_vars: '', extra_vars: '', cmd_args: '', credentials: null, credentials_req: false,
            comment: '', verbosity: 0,
        },
        var_values: {},
    }

    let executionPrompts: executionPromptsFullType = $state(JSON.parse(JSON.stringify(executionPromptsDefault)));
    let addTMPCredsModal = $state(false);
    let addTMPCredsModalId = $state(Date.now());
    let executionPromptJumpToLogs = $state(false);
    let colorLimit: inputColorType = $state('base');

    function t(code: string) : string {
        return tq($share, code);
    }

    function closeExecutionPrompt() {
        setURLHashParams(URL_HASH, null);
        open = false;
    }

    function isValidJSON(value: string): boolean {
        try {
            JSON.parse(value);
        } catch (e) {
            return false;
        }
        return true;
    }

    function startJob() {
        if (!job.id) {
            return;
        }
        let promptData: Record<string, any> = {};

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

        const extraVarsSupplied = executionPrompts.config.fields.includes('extra_vars') && isSet(executionPrompts.field_values.extra_vars);
        if (extraVarsSupplied && !isValidJSON(executionPrompts.field_values.extra_vars)) {
            apiErrorMsg = t('jobs.execute.extra_vars_json_invalid');
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
                    if (executionPrompts.field_values.credentials && executionPrompts.field_values.credentials.includes('user-')) {
                        credsKind = 'credentials_user';
                    }
                    if (executionPrompts.field_values.credentials) {
                        promptData[credsKind] = parseInt(executionPrompts.field_values.credentials.split('-')[1], 10);
                    }
                }
            } else if (f != 'credentials_req') {
                promptData[f] = executionPrompts.field_values[f];
            }
        }

        if (executionPrompts.config.vars.length) {
            const promptExtraVars: Record<string, string> = {};

            for (let [k, v] of Object.entries(executionPrompts.var_values)) {
                if (v && v.trim()) {
                    promptExtraVars[k] = v.trim();
                }
            }

            if (Object.keys(promptExtraVars).length > 0) {
                if (extraVarsSupplied) {
                    const userSuppliedExtraVars: Record<any, any> = JSON.parse(promptData['extra_vars']);
                    promptData['extra_vars'] = JSON.stringify({...userSuppliedExtraVars, ...promptExtraVars});
                } else {
                    promptData['extra_vars'] = JSON.stringify(promptExtraVars);
                }
            }
        }

        apiSuccessMsg = 'jobs.action.start';
        jobStarted = false;
        apiEdit('post', `job/${job.id}`, promptData, jobStartCallback);
        open = false;
        if (executionPromptJumpToLogs) {
            setTimeout(() => {
                if (jobStarted) {
                    redirectLogs(job.id)
                }
            }, 1000);
        }
        setURLHashParams(URL_HASH, null);
    }

    function jobStartCallback(s: number, j: any) {
        jobStarted = true;
        apiResponseHandler.handleRes(s, j);
    }

    function initExecutionPrompts() {
        if (!job) {
            return;
        }
        executionPromptJumpToLogs = false;
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
        if (job.extra_vars) {
            executionPrompts.field_values.extra_vars = job.extra_vars;
        }

        // set default values as configured for dropdown-variables
        for (const prompt_var of executionPrompts.config.vars) {
            if (prompt_var.kind != 'dropdown') {
                continue;
            }
            if (prompt_var.defaultChoice && prompt_var.choices.includes(prompt_var.defaultChoice)) {
                executionPrompts.var_values[prompt_var.varName] = prompt_var.defaultChoice;
            }
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

    onMount(() => {
        initExecutionPrompts();
    });
</script>

<Modal bind:open={open} size="sm" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <Heading tag="h2">{t('jobs.execute')}</Heading>
    <div>
        {t('jobs.job')}: {job.name}
    </div>

    {#if executionPrompts.config.fields.includes('limit')}
        <Label for="job_prompt_{job.id}_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
        <InventoryListField elementID="job_prompt_{job.id}_limit" required={executionPrompts.config.fields.includes('limit_req')}
            inventoryListFieldInFocus=''
            bind:value={executionPrompts.field_values.limit} bind:color={colorLimit}
            bind:repositoryID={job.repository} bind:inventoryFile={job.inventory_file} />
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
    {#if executionPrompts.config.fields.includes('extra_vars')}
        <Label for="job_prompt_{job.id}_extra_vars" class={classModalLabel}>{t('jobs.form.extra_vars_json')}</Label>
        <Input id="job_prompt_{job.id}_extra_vars" bind:value={executionPrompts.field_values.extra_vars} />
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
        <Select id="job_prompt_{job.id}_verb" items={formChoices.verbosity}
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
    <hr/>
    <div>
        <div class={classCenterChildDiv}>
            <Label for="job_prompt_{job.id}_jump_to_logs" class={classModalLabel}>{t('jobs.form.execution_jump_to_logs')}</Label>
        </div>
        <div class={classCenterChildDiv}>
            <Toggle id="job_prompt_{job.id}_jump_to_logs" bind:checked={executionPromptJumpToLogs} />
        </div>
    </div>
    <div class={classModalBtns}>
        <Button id="jobs-btn-exec-start" type="button" on:click={() => {startJob()}}><PlaySolid/></Button>
        <Tooltip>{t('btn.execute')}</Tooltip>

        <Button id="jobs-btn-exec-close" on:click={() => (closeExecutionPrompt())} class="inline-block ml-2">
            <CloseCircleSolid/>
        </Button>
        <Tooltip>{t('btn.close')}</Tooltip>
    </div>
</Modal>

{#if executionPrompts.config.fields.includes('credentials_tmp')}
    {#key addTMPCredsModalId}
        <CredentialsForm bind:open={addTMPCredsModal} action='add' kind='tmp'
            bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} customResponseHandler={handleExecutionCredentialsCreateResponse} />
    {/key}
{/if}
