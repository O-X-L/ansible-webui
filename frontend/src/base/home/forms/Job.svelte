<script lang="ts">
    import { onMount } from 'svelte';

    import {
        FolderSolid, FileSolid, CloseCircleSolid, TrashBinSolid, FloppyDiskSolid, CirclePlusSolid,
    } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Helper, Toggle, Select, Spinner, Tooltip,
        AccordionItem, Accordion,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';
    import MultiInput from '../../../flowbite-custom/MultiInput.svelte';

    import { share } from '../../Share.js';
    import { isSet, rsplit } from '../../../util/main.js';
    import { tq } from '../../../util/translate.js';
    import { apiGet, apiEdit, cacheKey } from '../../../util/api.js';
    import { type formInfoType, type inputColorType } from '../../Types.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import { type executionPromptsType, type executionPromptVarType } from '../Types.js';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalHelp, classModalBtns, classModalForm,
        classModalInputDiv, classCenterChildDiv, classModalInput, classSpinnerDiv, classSpoilerItem,
    } from '../../Style.js';

    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
    } = $props();

    const urlExisting = `job/${existingID}`;

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? 'job' : urlExisting);
    let title = $derived(actionNew ? t('jobs.new') : t('jobs.edit'));
    let formWarningMsgs: string[] = $state([]);

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true},
        comment: {value: '', color: inputBaseColor},
        repository: {value: null, color: inputBaseColor},
        playbook_file: {value: '', color: inputBaseColor, required: true},
        inventory_file: {value: '', color: inputBaseColor},  // NOTE: not required bc of dynamic inventories..
        limit: {value: '', color: inputBaseColor},
        tags: {value: '', color: inputBaseColor},
        tags_skip: {value: '', color: inputBaseColor},
        mode_diff: {value: false},
        mode_check: {value: false},
        verbosity: {value: 0, color: inputBaseColor},
        credentials_needed: {value: true},
        credentials_default: {value: '', color: inputBaseColor},
        credentials_category: {value: '', color: inputBaseColor},
        schedule: {
            value: '', color: inputBaseColor,
            blank: true,
            regex: /^()|(@(annually|yearly|monthly|weekly|daily|hourly))|(@every (\d+(s|m|h))+)|((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5,7})$/
        },
        enabled: {value: true},
        environment_vars: {value: '', color: inputBaseColor},
        cmd_args: {value: '', color: inputBaseColor},
        execution_prompts: {value: '', color: inputBaseColor},  // legacy prompts
        execution_prompts_json: {value: '', color: inputBaseColor},
        owner: {value: $share.backend.user_id},
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function valideInputInstance(e: Event, i: any) {
        valideInputBase(e, i);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'jobs.action.create' : 'jobs.action.update';
            success = true;
            open = false;
        } else {
            apiResponseHandler.handleRes(s, j);
        }
    }

    function submitForm() {
        execPromptsEncode();
        let [valid, errors] = submitFormBase(
            form, method, url, handleSubmitResponse, t, 'jobs.form.',
        );
        if (!valid) {
            formWarningMsgs = errors;
        }
    }

    function setFormInfos(j: any) {
        formInfos = j;
        if (action == 'add') {
            for (let [k, v] of Object.entries(formInfos.defaults)) {
                if (form[k]) {
                    form[k].value = v;
                }
            }
            loaded = true;
        }
    }

    function loadExisting(j: any) {
        existing = j;
        if (action == 'clone') {
            existing.name = `${existing.name} - Copy`;
        }
        for (let [k, v] of Object.entries(existing)) {
            if (form[k]) {
                form[k].value = v;
            }
        }
        execPromptsDecode();
        loaded = true;
    }

    function fetchBuild() {
        apiGet(`frontend/form/job?${cacheKey($share)}`, setFormInfos);

        if (action != 'add' && existingID) {
            apiGet(urlExisting, loadExisting);
        }
    }

    $effect(() => {
        if (!open || loaded) {
            return;
        }
        setTimeout(fetchBuild, 500);  // wait to fetch version
    })

    // autocomplete via api filesystem-browsing (playbook/inventory)
    //   todo: browing not working for git-isolate enabled repo
    interface browseResponse {
        dirs: string[],
        files: string[],
    }
    const classFsBrowse = 'bg-gray-100 dark:bg-gray-600 text-gray-800 p-2 dark:text-gray-50 text-sm ml-5 mt-1 mb-3 max-h-80 overflow-y-scroll rounded-b';
    const classFsBrowseItem = 'block hover:bg-primary-200 dark:hover:bg-primary-600 w-full text-left py-1 round';
    const fsBrowseNone = {dirs: [], files: []};
    let fsBrowseActive: string = $state('');
    let fsBrowseChoices: browseResponse = $state(fsBrowseNone);

    function fsBrowseClick(f: string) {
        if (fsBrowseActive == f) {
            return;
        }
        fsBrowse(f);
    }

    function fsBrowseBase(full: string) : string {
        let b = '';
        let p = rsplit(full, '/');
        if (p[1] && fsBrowseChoices.dirs.includes(p[1])) {
            b = full;

        } else if (p[0] != full || fsBrowseChoices.dirs.includes(p[0])) {
            b = p[0];
        }
        return b;
    }

    function fsBrowse(f: string) {
        let b = '';
        b = fsBrowseBase(form[f].value);
        if (b == form[f].value && !(form[f].value.slice(-1)[0] == '/') && form[f].value != '') {
            form[f].value += '/';
        }

        apiGet(`fs/browse/${form.repository.value||0}?base=${b}`, (j: any) => {fsBrowseUpdate(j, f)});
    }

    function fsBrowseClear() {
        fsBrowseActive = '';
        fsBrowseChoices = fsBrowseNone;
    }

    function fsBrowseValidate(full: string) : inputColorType {
        let p = rsplit(full, '/');
        if ((p[0] && fsBrowseChoices.files.includes(p[0])) || (p[1] && fsBrowseChoices.files.includes(p[1]))) {
            fsBrowseClear();
            return 'green';
        } else if (full != '') {
            return 'red';
        } else {
            return inputBaseColor;
        }
    }

    function fsBrowseUpdate(j: any, f: string) {
        fsBrowseActive = f;
        if (j.error) {
            return;
        }
        fsBrowseChoices.files = j.files.sort()
        fsBrowseChoices.dirs = j.dirs.sort()

        form[f].color = fsBrowseValidate(form[f].value);
    }

    function fsBrowseSelect(f: string, c: string) {
        let p = rsplit(form[f].value, '/');
        if (p[1] == null && !fsBrowseChoices.dirs.includes(p[0])) {
            form[f].value = c;
        } else {
            form[f].value = `${p[0]}/${c}`;
        }

        fsBrowse(f);
    }

    // execution prompts

    const PROMPT_KIND_CHOICES = [
        {'name': t('jobs.form.prompt_choice_text'), 'value': 'text'},
        {'name': t('common.choices'), 'value': 'dropdown'},
    ];

    interface executionPrompt {
        id: number,
        name: {value: string, color: inputColorType, required: boolean},
        varName: {value: string, color: inputColorType, required: boolean},
        kind: {value: 'text'|'dropdown'},
        required: {value: boolean},
        choices: {value: string[]},
        regex: {value: string, color: inputColorType, regex: RegExp},
    }
    interface executionPromptSwitches {
        tags: boolean,
        tags_skip: boolean,
        mode_check: boolean,
        mode_diff: boolean,
        limit: boolean,
        limit_req: boolean,
        environment_vars: boolean,
        cmd_args: boolean,
        verbosity: boolean,
        credentials: boolean,
        credentials_req: boolean,
        credentials_tmp: boolean,
        comment: boolean,
    }

    let executionPromptsSimple: executionPromptSwitches = $state({
        tags: false, tags_skip: false, mode_check: true, mode_diff: false, limit: true, limit_req: false,
        environment_vars: false, cmd_args: false, verbosity: true, credentials: true, comment: true,
        credentials_req: false, credentials_tmp: false,
    });
    let executionPrompts: executionPrompt[] = $state([]);
    let executionPromptId = 0;

    function execPromptsDecode() {
        if (!form.execution_prompts_json.value) {
            return;
        }
        let promptsJSON: executionPromptsType = JSON.parse(form.execution_prompts_json.value);

        for (let k of Object.keys(executionPromptsSimple)) {
            if (promptsJSON.fields.includes(k)) {
                executionPromptsSimple[k] = true;
            }
        }

        for (let prompt of promptsJSON.vars) {
            execPromptAddWithDefaults(prompt);
        }
    }

    function execPromptsEncode() {
        let prompts: executionPromptsType = {fields: [], vars: []};
        for (let [s, v] of Object.entries(executionPromptsSimple)) {
            if (v) {
                prompts.fields.push(s);
            }
        }

        for (let p of executionPrompts) {
            let prompt: executionPromptVarType = {
                name: p.name.value,
                varName: p.varName.value,
                kind: p.kind.value,
                required: p.required.value,
                choices: p.choices.value,
                regex: p.regex.value,
            };
            prompts.vars.push(prompt);
        }

        form.execution_prompts_json.value = JSON.stringify(prompts);
    }

    function execPromptAddWithDefaults(p: executionPromptVarType) {
        executionPromptId += 1;
        let p2: executionPrompt = {
            id: executionPromptId,
            name: {value: p.name, required: true, color: inputBaseColor},
            varName: {value: p.varName, required: true, color: inputBaseColor},
            kind: {value: p.kind},
            required: {value: p.required},
            choices: {value: p.choices},
            regex: {value: p.regex, color: inputBaseColor, regex: /^(?!.*\x22.*)(^.*$)$/},
        }
        executionPrompts = [...executionPrompts, p2];
    }

    function execPromptAdd() {
        let prompt: executionPromptVarType = {
            name: `Prompt ${executionPromptId+1}`,
            varName: '',
            kind: 'text',
            required: false,
            choices: [],
            regex: '',
        };
        execPromptAddWithDefaults(prompt);
    }

    function execPromptRemove(promptId: number) {
        let filtered = [];
        for (let p of executionPrompts) {
            if (p.id != promptId) {
                filtered.push(p);
            }
        }
        executionPrompts = filtered;
    }

    // update isolated git repo
    function nullCallback() {}

    function updateCreateGitRepo() {
        if (isSet(form.repository.value)) {
            apiEdit('post', `repository/${form.repository.value}`, null, nullCallback);
        }
    }

    onMount(() => {
        updateCreateGitRepo();
    })

    $effect(() => {
        if (isSet(form.repository.value)) {
            updateCreateGitRepo();
        }
    })
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{title}</Heading>
    {#if !loaded}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <APIResponseHandler bind:this={apiResponseHandler} bind:warningMsgs={formWarningMsgs} />

        <Accordion class={classModalForm}>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-main">
                <span slot="header">Main</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_name" class={classModalLabel}>{t('jobs.form.name')}</Label>
                        <Input id="job_name" bind:value={form.name.value} bind:color={form.name.color}
                            on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
                        <Input id="job_cmt" bind:value={form.comment.value} bind:color={form.comment.color} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_repo" class={classModalLabel}>{t('jobs.form.repository')}</Label>
                        <Select id="job_repo" items={formInfos.choices.repository}
                            bind:value={form.repository.value} bind:color={form.repository.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.repository')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_pb" class={classModalLabel}>{t('jobs.form.playbook_file')}</Label>
                        <Input id="job_pb" bind:value={form.playbook_file.value} bind:color={form.playbook_file.color}
                            on:input={valideInput} on:blur={valideInput} required={form.playbook_file.required}
                            on:input={() => {fsBrowse('playbook_file')}}
                            on:click={() => {fsBrowseClick('playbook_file')}} />
                        {#if fsBrowseActive == 'playbook_file'}
                            <div class={classFsBrowse}>
                                {#each fsBrowseChoices.files as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect('playbook_file', c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoices.dirs as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect('playbook_file', c)}}>
                                        <FolderSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#if !fsBrowseChoices.dirs.length && !fsBrowseChoices.files.length}
                                    <div class={classSpinnerDiv}><Spinner size="sm"/></div>
                                {/if}
                            </div>
                        {/if}
                        <Helper class={classModalHelp}>{t('jobs.form.help.playbook_file')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_inv" class={classModalLabel}>{t('jobs.form.inventory_file')}</Label>
                        <Input id="job_inv"
                            bind:value={form.inventory_file.value} bind:color={form.inventory_file.color}
                            on:input={() => {fsBrowse('inventory_file')}}
                            on:click={() => {fsBrowseClick('inventory_file')}} />
                        {#if fsBrowseActive == 'inventory_file'}
                            <div class={classFsBrowse}>
                                {#each fsBrowseChoices.files as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect('inventory_file', c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoices.dirs as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect('inventory_file', c)}}>
                                        <FolderSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#if !fsBrowseChoices.dirs.length && !fsBrowseChoices.files.length}
                                    <Spinner size="sm"/>
                                {/if}
                            </div>
                        {/if}
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.inventory_file')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-exec">
                <span slot="header">Execution</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
                        <Input id="job_limit"
                            bind:value={form.limit.value} bind:color={form.limit.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.limit')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
                        <Input id="job_tags"
                            bind:value={form.tags.value} bind:color={form.tags.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.tags')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
                        <Input id="job_tags_skip"
                            bind:value={form.tags_skip.value} bind:color={form.tags_skip.color} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
                        <Toggle id="job_diff" bind:checked={form.mode_diff.value} />

                        <Label for="job_chk" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
                        <Toggle id="job_chk" bind:checked={form.mode_check.value} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.mode_check')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_verb" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
                        <Select id="job_verb" items={formInfos.choices.verbosity}
                            bind:value={form.verbosity.value} bind:color={form.verbosity.color} />
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-creds">
                <span slot="header">Credentials</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_creds" class={classModalLabel}>{t('jobs.form.credentials_needed')}</Label>
                        <Toggle id="job_creds" bind:checked={form.credentials_needed.value} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_needed')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_creds_dflt" class={classModalLabel}>{t('jobs.form.credentials_default')}</Label>
                        <Select id="job_creds_dflt" items={formInfos.choices.credentials_default}
                            bind:value={form.credentials_default.value} bind:color={form.credentials_default.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_default')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_creds_cat" class={classModalLabel}>{t('jobs.form.credentials_category')}</Label>
                        <Input id="job_creds_cat"
                            bind:value={form.credentials_category.value} bind:color={form.credentials_category.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_category')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-schedule">
                <span slot="header">Scheduling</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_cron" class={classModalLabel}>{t('jobs.form.schedule')}</Label>
                        <Input id="job_cron" on:input={valideInput}
                            bind:value={form.schedule.value} bind:color={form.schedule.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.schedule')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_cron_en" class={classModalLabel}>{t('jobs.form.enabled')}</Label>
                        <Toggle id="job_cron_en" bind:checked={form.enabled.value} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.enabled')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-misc">
                <span slot="header">Additional</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_env" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
                        <Input id="job_env" bind:value={form.environment_vars.value} bind:color={form.environment_vars.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.environment_vars')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
                        <Input id="job_args" bind:value={form.cmd_args.value} bind:color={form.cmd_args.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.cmd_args')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-prompts">
                <span slot="header">{t('jobs.form.execution_prompts')}</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInputDiv}>
                        <Heading tag="h3">{t('jobs.form.prompt_fields')}:</Heading>
                        <div>
                            <Label for="job_exec_prompt_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_cmt" bind:checked={executionPromptsSimple.comment} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_tags" bind:checked={executionPromptsSimple.tags} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_tags_skip" bind:checked={executionPromptsSimple.tags_skip} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_mode_check" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_mode_check" bind:checked={executionPromptsSimple.mode_check} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_mode_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_mode_diff" bind:checked={executionPromptsSimple.mode_diff} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_limit" bind:checked={executionPromptsSimple.limit} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_limit_req" class={classModalLabel}>{t('jobs.form.prompt_limit_req')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_limit_req" bind:checked={executionPromptsSimple.limit_req}
                                disabled={!executionPromptsSimple.limit} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_env_vars" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_env_vars" bind:checked={executionPromptsSimple.environment_vars} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_cmd_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_cmd_args" bind:checked={executionPromptsSimple.cmd_args} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_verbosity" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_verbosity" bind:checked={executionPromptsSimple.verbosity} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_creds" class={classModalLabel}>{t('jobs.form.credentials')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_creds" bind:checked={executionPromptsSimple.credentials} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_creds_req" class={classModalLabel}>{t('jobs.form.prompt_credentials_req')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_creds_req" bind:checked={executionPromptsSimple.credentials_req}
                                disabled={!executionPromptsSimple.credentials} />
                            </div>
                        </div>
                        <div>
                            <Label for="job_exec_prompt_creds_tmp" class={classModalLabel}>{t('jobs.form.prompt_credentials_tmp')}</Label>
                            <div class={classCenterChildDiv}>
                                <Toggle id="job_exec_prompt_creds_tmp" bind:checked={executionPromptsSimple.credentials_tmp}
                                disabled={!executionPromptsSimple.credentials} />
                            </div>
                        </div>
                    </div>
                    <div>
                        <Heading tag="h3">{t('jobs.form.prompt_vars')}:</Heading>
                        {#each executionPrompts as p (p.id)}
                            <hr class="mt-10 mb-2">
                            <div class={classModalInputDiv}>
                                <div class={classModalInput}>
                                    <Label for="job_prompt_{p.id}_name" class={classModalLabel}>{t('jobs.form.prompt_name')}</Label>
                                    <Input id="job_prompt_{p.id}_name" on:input={(e) => {valideInputInstance(e, p)}} 
                                        bind:value={p.name.value} bind:color={p.name.color} />
                                </div>
                                <div class={classModalInput}>
                                    <Label for="job_prompt_{p.id}_varName" class={classModalLabel}>{t('jobs.form.prompt_varname')}</Label>
                                    <Input id="job_prompt_{p.id}_varName" on:input={(e) => {valideInputInstance(e, p)}} 
                                        bind:value={p.varName.value} bind:color={p.varName.color} />
                                </div>
                                <div>
                                    <Label for="job_prompt_{p.id}_kind" class={classModalLabel}>{t('jobs.form.prompt_kind')}</Label>
                                    <Select id="job_prompt_{p.id}_kind" items={PROMPT_KIND_CHOICES} bind:value={p.kind.value} />
                                </div>
                                <div>
                                    <Label for="job_prompt_{p.id}_req" class={classModalLabel}>{t('common.required')}</Label>
                                    <div class={classCenterChildDiv}>
                                        <Toggle id="job_prompt_{p.id}_req" bind:checked={p.required.value} />
                                    </div>
                                </div>
                                {#if p.kind.value == 'dropdown'}
                                    <div class={classModalInput}>
                                        <Label for="job_prompt_{p.id}_choices" class={classModalLabel}>{t('common.choices')}</Label>
                                        <MultiInput id="job_prompt_{p.id}_choices" bind:value={p.choices.value} />
                                        <Helper class={classModalHelp}>{t('jobs.form.help.prompt_choices')}</Helper>
                                    </div>
                                {/if}
                                {#if p.kind.value == 'text'}
                                    <div class={classModalInput}>
                                        <Label for="job_prompt_{p.id}_regex" class={classModalLabel}>{t('jobs.form.prompt_regex')}</Label>
                                        <Input id="job_prompt_{p.id}_regex" on:input={(e) => {valideInputInstance(e, p)}} 
                                            bind:value={p.regex.value} bind:color={p.regex.color} />
                                        <Helper class={classModalHelp}>{@html t('jobs.form.help.prompt_regex')}</Helper>
                                    </div>
                                {/if}
                            </div>
                            <div class="flex justify-between">
                                <div></div>
                                <div class="mr-5 mt-10">
                                    <Button type="button" on:click={() => {execPromptRemove(p.id)}}><TrashBinSolid/></Button>
                                    <Tooltip>{t('btn.delete')}</Tooltip>
                                </div>    
                            </div>                            
                        {/each}
                        <div class={classModalBtns}>
                            <Button type="button" on:click={execPromptAdd}><CirclePlusSolid/></Button>
                            <Tooltip>{t('btn.add')}</Tooltip>
                        </div>
                    </div>
                </div>
            </AccordionItem>
        </Accordion>

        <div class={classModalBtns}>
            <Button id="job-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button id="job-btn-discard" on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
    {/if}
</Modal>
