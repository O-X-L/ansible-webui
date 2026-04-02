<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        FolderSolid, FileSolid, CloseCircleSolid, TrashBinSolid, FloppyDiskSolid, CirclePlusSolid,
        ServerSolid, InfoCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Helper, Toggle, Select, Spinner, Tooltip,
        AccordionItem, Accordion, Popover,
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';
    import MultiInput from '../../../flowbite-custom/MultiInput.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { isSet, rsplit } from '../../../util/main.js';
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
        classModalDialog, classModalBody, classSpoilerPad, classPopover, classPopoverTitle,
    } from '../../Style.js';

    let componentRoot;
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
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

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
        ssh_hostkey_file: {value: '', color: inputBaseColor},
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
                if (k in form) {
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
            if (k in form) {
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
    // todo: inventory_file multi-input
    interface browseResponse {
        dirs: string[],
        files: string[],
    }
    const classDynChoices = 'bg-gray-100 dark:bg-gray-600 text-gray-800 p-2 dark:text-gray-50 text-sm ml-5 mt-1 mb-3 max-h-80 overflow-y-scroll rounded-b';
    const classDynChoicesRow = 'block w-full text-left py-1 round';
    const classDynChoicesItem = `${classDynChoicesRow} hover:bg-primary-200 dark:hover:bg-primary-600`;

    const fsBrowseNone = {dirs: [], files: []};
    let fsBrowseField: string = $state('');
    let fsBrowseCurrentBase: string = $state('');
    let fsBrowseChoices: browseResponse = $state(fsBrowseNone);  // cached full-list of dirs/files
    let fsBrowseChoicesActive: browseResponse = $state(fsBrowseNone);  // list we actually show to the user; to be manipulated

    function fsBrowseClick(f: 'playbook_file'|'inventory_file') {
        fsBrowseClearActive();
        fsBrowse(f);
    }

    function fsBrowse(f: 'playbook_file'|'inventory_file', event: Event|null = null) {
        // validate current input and query new contents if required
        fsBrowseField = f;
        fsBrowseValidate(f);
        let requireQuery = false;

        // if we are new - no value was selected yet or we have not yet got an API response
        if (!form[f].value || (fsBrowseChoices.files.length == 0 && fsBrowseChoices.dirs.length == 0)) {
            requireQuery = true;
        }

        // autocorrect
        if (form[f].value && form[f].value.includes('//')) {
            form[f].value = form[f].value.replaceAll('//', '/');
        }

        let base = fsBrowseBase(f);

        // backspace - the user exited the child-directory; we need to re-query the parent-dir
        if (base != fsBrowseCurrentBase) {
            requireQuery = true;
            fsBrowseCurrentBase = base;
        }

        // if the current input is a valid directory - append a slash and query its content
        if (form[f].value != '' && base == form[f].value) {
            if (!form[f].value.endsWith('/')) {
                form[f].value += '/';
            }
            requireQuery = true;
        }

        if (requireQuery) {
            fsBrowseQueryNew(f, base);

        } else {
            fsBrowseSubstringFilter(f);
            if (event && event.data) {
                // ignore backspace
                fsBrowseAutoComplete(f);
                fsBrowseValidate(f);
            }
        }
    }

    function fsBrowseQueryNew(f: 'playbook_file'|'inventory_file', base: string|null = null) {
        if (!base) {
            base = fsBrowseBase(f);
        }

        apiGet(
            `fs/browse/${form.repository.value||0}?base=${base}`,
            (j: any) => {fsBrowseUpdate(j, f)},
        );
    }

    function fsBrowseSubstringFilter(f: 'playbook_file'|'inventory_file') {
        // filter choices by sub-string
        let [_, current] = fsBrowseGetPathCurrent(f);
        if (!current) {
            fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseChoices));
            return;
        }

        let newChoices: browseResponse = JSON.parse(JSON.stringify(fsBrowseNone));
        for (let d of fsBrowseChoices.dirs) {
            if (d.includes(current)) {
                newChoices.dirs.push(d);
            }
        }
        for (let f of fsBrowseChoices.files) {
            if (f.includes(current)) {
                newChoices.files.push(f);
            }
        }
        fsBrowseChoicesActive = newChoices;
    }

    function fsBrowseAutoComplete(f: 'playbook_file'|'inventory_file') {
        // autocomplete if only one option is left
        if (fsBrowseChoicesActive.files.length == 0 && fsBrowseChoicesActive.dirs.length == 1) {
            fsBrowseSetCurrent(f, fsBrowseChoicesActive.dirs[0] + '/');
            fsBrowseQueryNew(f);

        } else if (fsBrowseChoicesActive.files.length == 1 && fsBrowseChoicesActive.dirs.length == 0) {
            fsBrowseSetCurrent(f, fsBrowseChoicesActive.files[0]);
            fsBrowseChoicesActive.files = [];
        }
    }

    function fsBrowseBase(f: 'playbook_file'|'inventory_file') : string {
        // get directory-path without (partial-) files
        let full = form[f].value;
        let base = '';
        let [path, current] = fsBrowseGetPathCurrent(f);

        if (current && fsBrowseChoices.dirs.includes(current)) {
            base = full;

        } else if (path && (path != full || fsBrowseChoices.dirs.includes(path))) {
            base = path;
        }
        return base;
    }

    function fsBrowseGetPathCurrent(f: 'playbook_file'|'inventory_file') : [string|null, string|null] {
        let full = form[f].value;
        if (!full) {
            return [null, null];
        }
        if (!full.includes('/')) {
            return [null, full];
        }

        let p = rsplit(full, '/');
        return [p[0], p[1]];
    }

    function fsBrowseSetCurrent(f: 'playbook_file'|'inventory_file', current: string) {
        let [path, _] = fsBrowseGetPathCurrent(f);
        if (path) {
            form[f].value = `${path}/${current}`;
        } else {
            form[f].value = current;
        }
    }

    function fsBrowseClearActive() {
        fsBrowseField = '';
        fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseNone));
    }

    function fsBrowseClear() {
        fsBrowseClearActive();
        fsBrowseChoices = fsBrowseNone;
    }

    function fsBrowseValidate(f: 'playbook_file'|'inventory_file') {
        // checks if the current input (without base-path) is a valid choice
        let [path, current] = fsBrowseGetPathCurrent(f);

        if (fsBrowseChoices.files.length == 0 && fsBrowseChoices.dirs.length == 0) {
            return;
        }

        if ((path && fsBrowseChoices.files.includes(path)) || (current && fsBrowseChoices.files.includes(current))) {
            fsBrowseClearActive();
            form[f].color = 'green';
        } else if (form[f].value != '') {
            form[f].color = 'red';
        } else {
            form[f].color = inputBaseColor;
        }
    }

    function fsBrowseUpdate(j: any, f: 'playbook_file'|'inventory_file') {
        fsBrowseField = f;
        if (j.error) {
            return;
        }
        fsBrowseChoices = j;
        fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseChoices));
    }

    function fsBrowseSelect(f: 'playbook_file'|'inventory_file', c: string) {
        if (fsBrowseChoices.dirs.includes(c) && !c.endsWith('/')) {
            c += '/';
        }

        if (form[f].value && form[f].value.endsWith('/')) {
            form[f].value += c;
            fsBrowse(f);
            return;
        }

        let [path, _] = fsBrowseGetPathCurrent(f);
        if (!path) {
            form[f].value = c;
        } else {
            form[f].value = `${path}/${c}`;
        }
        fsBrowse(f);
    }

    // autocomplete via api inventory-listing (limit)
    interface inventoryListResponse {
        hosts: string[],
        groups: string[],
        members: any,
        ansible_hosts: any,
    }

    const inventoryListNone = {hosts: [], groups: [], members: {}, ansible_hosts: {}};
    let inventoryListLoad: boolean = $state(false);
    let inventoryListChoices: inventoryListResponse = $state(inventoryListNone);
    let inventoryListChoicesActive: inventoryListResponse = $state(inventoryListNone);
    let inventoryCurrentRepo: number = $state(0);
    let inventoryCurrentFile: string = $state('');

    function inventoryList(event: Event|null = null) {
        if (!form.inventory_file.value) {
            return;
        }

        inventoryListValidate();

        // autocorrect
        if (form.limit.value && form.limit.value.includes(',,')) {
            form.limit.value = form.limit.value.replaceAll(',,', ',');
        }

        inventoryListSubstringFilter();
        if (event && event.data) {
            // ignore backspace
            inventoryListAutoComplete();
        }
        inventoryListQueryNew();
    }

    function inventoryListSubstringFilter() {
        // filter choices by sub-string
        let limits = inventoryListGet();
        if (limits.length == 0 || form.limit.value.endsWith(',')) {
            inventoryListChoicesActive = JSON.parse(JSON.stringify(inventoryListChoices));
            return;
        }
        let current = limits.pop();
        if (!current) {
            return;
        }

        let newChoices: inventoryListResponse = JSON.parse(JSON.stringify(inventoryListNone));
        for (let g of inventoryListChoices.groups) {
            if (g.includes(current) && !limits.includes(g)) {
                newChoices.groups.push(g);
            }
        }
        for (let h of inventoryListChoices.hosts) {
            if (h.includes(current) && !limits.includes(h)) {
                newChoices.hosts.push(h);
            }
        }
        inventoryListChoicesActive = newChoices;
    }

    function inventoryListAutoComplete() {
        // autocomplete if only one option is left
        if (inventoryListChoicesActive.hosts.length == 0 && inventoryListChoicesActive.groups.length == 1) {
            inventoryListSetCurrent(inventoryListChoicesActive.groups[0]);
            inventoryListChoicesActive.groups = [];

        } else if (inventoryListChoicesActive.hosts.length == 1 && inventoryListChoicesActive.groups.length == 0) {
            inventoryListSetCurrent(inventoryListChoicesActive.hosts[0]);
            inventoryListChoicesActive.hosts = [];
        }
    }

    function inventoryListQueryNew() {
        // we do not have to re-query the same inventory
        let requireQuery = false;

        // inventory has changed
        if (form.inventory_file.value != inventoryCurrentFile) {
            requireQuery = true;
            inventoryCurrentFile = form.inventory_file.value;
        }
        // repo has changed
        if (!form.repository.value) {
            inventoryCurrentRepo = 0;
        } else if (form.repository.value != inventoryCurrentRepo) {
            requireQuery = true;
            inventoryCurrentRepo = form.repository.value;
        }

        if (!requireQuery) {
            return;
        }
   
        inventoryListLoad = true;
        apiGet(
            `inventory/list?limit=all&inventory=${form.inventory_file.value}&repository=${form.repository.value||0}`,
            (j: any) => {inventoryListUpdate(j)},
        );
    }

    function inventoryListUpdate(j: any) {
        if (j.error) {
            return;
        }

        inventoryListChoices = j
        inventoryListChoicesActive = JSON.parse(JSON.stringify(inventoryListChoices))

        inventoryListLoad = false;
        inventoryListValidate();
    }

    function inventoryListGet() : string[] {
        if (!form.limit.value) {
            return [];
        }
        return form.limit.value.split(',').filter(e => e !== '');
    }

    function inventoryListSetCurrent(current: string) {
        let limits = inventoryListGet();
        if (limits.length == 0) {
            form.limit.value = current;
            inventoryListValidate();
            return;
        }
        if (limits.includes(current)) {
            return;
        }
        let last = limits.pop();
        if (last && (inventoryListChoices.hosts.includes(last) || inventoryListChoices.groups.includes(last))) {
            current = `${last},${current}`;
        }
        if (limits.length == 0) {
            form.limit.value = current;
        } else {
            form.limit.value = `${limits.join(',')},${current}`;
        }

        inventoryListValidate();
    }

    function inventoryListValidate() {
        if (!form.limit.value || form.limit.value == '') {
            form.limit.color = inputBaseColor;
            return;
        }
        let results = [];
        for (let v of inventoryListGet()) {
            results.push(
                inventoryListChoices.hosts.includes(v) || inventoryListChoices.groups.includes(v)
            )
        }

        if (results.every(v => v === true)) {
            form.limit.color = 'green';
        } else {
            form.limit.color = 'red';
        }
    }

    function inventoryListClear() {
        inventoryListChoices = JSON.parse(JSON.stringify(inventoryListNone));
        inventoryListChoicesActive = JSON.parse(JSON.stringify(inventoryListNone));
    }

    function inventoryListGroupMembers(group: string) : string[] {
        let members = inventoryListChoices.members[group];
        if (!members) {
            return [];
        }
        return members;
    }

    function inventoryListHostIP(host: string) : string|null {
        let ansible_host = inventoryListChoices.ansible_hosts[host];
        if (!ansible_host) {
            return null;
        }
        return ansible_host;
    }

    function inventoryListHostIPStr(host: string) : string {
        let ip = inventoryListHostIP(host);
        if (!ip) {
            return '';
        }
        return ` (${ip})`;
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
        defaultChoice: {value: string|null},
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
        if (!existing.execution_prompts_json) {
            return;
        }
        let promptsJSON: executionPromptsType = JSON.parse(existing.execution_prompts_json);

        for (let k of Object.keys(executionPromptsSimple)) {
            executionPromptsSimple[k] = promptsJSON.fields.includes(k);
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
            if (!isSet(p.varName.value)) {
                // will be an invalid extra-var..; todo: show warning
                continue;
            }
            let prompt: executionPromptVarType = {
                name: p.name.value,
                varName: p.varName.value,
                kind: p.kind.value,
                required: p.required.value,
                choices: p.choices.value,
                defaultChoice: p.defaultChoice.value,
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
            defaultChoice: {value: p.defaultChoice},
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
            defaultChoice: null,
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

    // ALT+S quick-save
    function handleKeyUp(e: KeyboardEvent) {
        switch (e.key) {
        case 'Alt':
            pressedKeyAlt = false;
            break;
        case 's':
        case 'S':
            pressedKeyS = false;
            break;
        default:
            return;
        }
    }
    
    function handleKeyDown(e: KeyboardEvent) {
        switch (e.key) {
        case 'Alt':
            pressedKeyAlt = true;
            break;
        case 's':
        case 'S':
            pressedKeyS = true;
            break;
        default:
            return;
        }
    }

    $effect(() => {
        if (open && componentRoot) {
            componentRoot.focus();
        }
    });

    $effect(() => {
        if (pressedKeyAlt && pressedKeyS) {
            submitForm();
        }
    });

    onMount(() => {
        if (componentRoot) {
            componentRoot.addEventListener('keyup', handleKeyUp);
            componentRoot.addEventListener('keydown', handleKeyDown);
        }
        updateCreateGitRepo();
    });

    onDestroy(()=>{
        if (componentRoot) {
            componentRoot.removeEventListener('keyup', handleKeyUp);
            componentRoot.removeEventListener('keydown', handleKeyDown);
        }
        fsBrowseClear();
        inventoryListClear();
    });

    $effect(() => {
        if (isSet(form.repository.value)) {
            updateCreateGitRepo();
        }
    });
</script>

<div bind:this={componentRoot} tabindex="-1" class="inline-block">
<Modal bind:open={open} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} dialogClass={classModalDialog} bodyClass={classModalBody}>
    <Heading tag="h2">{title}</Heading>
    {#if !loaded}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <APIResponseHandler bind:this={apiResponseHandler} bind:warningMsgs={formWarningMsgs} />

        <Accordion class={classModalForm}>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-main" paddingDefault={classSpoilerPad}>
                <span slot="header">Main</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_name" class={classModalLabel}>{t('common.name')}</Label>
                        <Input id="job_name" bind:value={form.name.value} bind:color={form.name.color}
                            on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_cmt" class={classModalLabel}>{t('common.comment')}</Label>
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
                            required={form.playbook_file.required}
                            on:blur={() => {fsBrowseValidate('playbook_file')}}
                            on:input={(event) => {fsBrowse('playbook_file', event)}}
                            on:click={() => {fsBrowseClick('playbook_file')}} />
                        {#if fsBrowseField == 'playbook_file'}
                            <div class={classDynChoices}>
                                {#each fsBrowseChoicesActive.files as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {fsBrowseSelect('playbook_file', c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoicesActive.dirs as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {fsBrowseSelect('playbook_file', c)}}>
                                        <FolderSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#if !fsBrowseChoicesActive.dirs.length && !fsBrowseChoicesActive.files.length}
                                    <div class="{classDynChoicesRow} cursor-wait">
                                        - {t('jobs.form.file_browse.empty')} -
                                    </div>
                                {/if}
                            </div>
                        {/if}
                        <Helper class={classModalHelp}>{t('jobs.form.help.playbook_file')}</Helper>
                    </div>
                    <div class={classModalInput}>
                        <Label for="job_inv" class={classModalLabel}>{t('jobs.form.inventory_file')}</Label>
                        <Input id="job_inv"
                            bind:value={form.inventory_file.value} bind:color={form.inventory_file.color}
                            on:blur={() => {fsBrowseValidate('inventory_file')}}
                            on:input={(event) => {fsBrowse('inventory_file', event)}}
                            on:click={() => {fsBrowseClick('inventory_file')}} />
                        {#if fsBrowseField == 'inventory_file'}
                            <div class={classDynChoices}>
                                {#each fsBrowseChoicesActive.files as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {fsBrowseSelect('inventory_file', c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoicesActive.dirs as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {fsBrowseSelect('inventory_file', c)}}>
                                        <FolderSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#if !fsBrowseChoicesActive.dirs.length && !fsBrowseChoicesActive.files.length}
                                    <div class="{classDynChoicesRow} cursor-wait">
                                        - {t('jobs.form.file_browse.empty')} -
                                    </div>
                                {/if}
                            </div>
                        {/if}
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.inventory_file')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-exec" paddingDefault={classSpoilerPad}>
                <span slot="header">Execution</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInput}>
                        <Label for="job_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
                        <Input id="job_limit"
                            bind:value={form.limit.value} bind:color={form.limit.color}
                            on:blur={() => {inventoryListValidate()}}
                            on:input={(event) => {inventoryList(event)}}
                            on:click={() => {inventoryList()}} />
                        {#if inventoryListChoicesActive.groups.length > 0 || inventoryListChoicesActive.hosts.length > 0}
                            <div class={classDynChoices}>
                                {#each inventoryListChoicesActive.groups as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {inventoryListSetCurrent(c)}}>
                                        <FolderSolid class="inline-block" /> {c}
                                        <span id="limit-group-members-{c}" class="ml-1">
                                            <InfoCircleSolid class="inline-block" size="sm"/>
                                            <span class="sr-only">{t('alerts.group')} {t('permission.members')}</span>
                                        </span>
                                        <Popover triggeredBy="#limit-group-members-{c}" class="{classPopover} max-h-60 overflow-y-scroll" placement="bottom-start">
                                            <div class="p-3 space-y-2">
                                                <h3 class={classPopoverTitle}>{t('alerts.group')} {t('permission.members')}</h3>
                                            </div>
                                            <div class="font-bold">{t('permission.members')}: {inventoryListGroupMembers(c).length}</div>
                                            {#each inventoryListGroupMembers(c) as host}
                                                <div><ServerSolid class="inline-block" /> {host}{inventoryListHostIPStr(host)}</div>
                                            {/each}
                                        </Popover>
                                    </button>
                                {/each}
                                {#each inventoryListChoicesActive.hosts as c}
                                    <button type="button" class={classDynChoicesItem}
                                        onclick={(e) => {inventoryListSetCurrent(c)}}>
                                        <ServerSolid class="inline-block" /> {c}
                                        {#if inventoryListHostIP(c)}
                                            <span id="limit-host-ip-{c}" class="ml-1">
                                                <InfoCircleSolid class="inline-block" size="sm"/>
                                                <span class="sr-only">{t('alerts.group')} {t('permission.members')}</span>
                                            </span>
                                            <Popover triggeredBy="#limit-host-ip-{c}" class="{classPopover} max-h-60 overflow-y-scroll" placement="bottom-start">
                                                <div class="p-3 space-y-2">
                                                    <h3 class={classPopoverTitle}>Ansible Host</h3>
                                                </div>
                                                <div class="font-bold">{inventoryListHostIP(c)}</div>
                                            </Popover>
                                        {/if}
                                    </button>
                                {/each}
                            </div>
                        {:else if inventoryListLoad}
                            <div class={classSpinnerDiv}><Spinner/></div>
                        {/if}
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
            <AccordionItem defaultClass="{classSpoilerItem} job-form-creds" paddingDefault={classSpoilerPad}>
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
            <AccordionItem defaultClass="{classSpoilerItem} job-form-schedule" paddingDefault={classSpoilerPad}>
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
            <AccordionItem defaultClass="{classSpoilerItem} job-form-misc" paddingDefault={classSpoilerPad}>
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
                    <!-- todo: allow user to de-select hostkey-file -->
                    <div class={classModalInput}>
                        <Label for="job_ssh_hostkey_file" class={classModalLabel}>{t('system.ssh_hostkey')}</Label>
                        <Select id="job_ssh_hostkey_file" items={formInfos.choices.ssh_hostkey_file}
                            bind:value={form.ssh_hostkey_file.value} bind:color={form.ssh_hostkey_file.color} />
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem defaultClass="{classSpoilerItem} job-form-prompts" paddingDefault={classSpoilerPad}>
                <span slot="header">{t('jobs.form.execution_prompts')}</span>
                <div class={classModalInputDiv}>
                    <div class={classModalInputDiv}>
                        <Heading tag="h3">{t('jobs.form.prompt_fields')}:</Heading>
                        <div>
                            <Label for="job_exec_prompt_cmt" class={classModalLabel}>{t('common.comment')}</Label>
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
                                    <Label for="job_prompt_{p.id}_kind" class={classModalLabel}>{t('common.kind')}</Label>
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
                                    <div class={classModalInput}>
                                        <Label for="job_prompt_{p.id}_default_choice" class={classModalLabel}>{t('jobs.form.prompt_default_choice')}</Label>
                                        <Input id="job_prompt_{p.id}_default_choice" bind:value={p.defaultChoice.value} />
                                        <Helper class={classModalHelp}>{t('jobs.form.help.prompt_default_choice')}</Helper>
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
</div>
