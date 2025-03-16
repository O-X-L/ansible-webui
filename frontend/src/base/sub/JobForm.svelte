<script lang="ts">
    import { onMount } from 'svelte';

    import { FolderSolid, FileSolid, CloseCircleSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Modal, Input, Label, Helper, Toggle, Select, Spinner, Alert,
        AccordionItem, Accordion,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { apiGet } from '../../util/api.js';
    import { rsplit } from '../../util/main.js';
    import { tq } from '../../util/translate.js';
    import {
        inputBaseColor, toggleBaseColor, valideInputBase, inputRequiredBaseColor, submitFormBase,
        type formMethod,
    } from '../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalHelp, classModalBtns, classModalForm,
        classModalInputDiv,
    } from '../Style.js';

    // todo: reset to default if 'add' form gets closed
    let { open = $bindable(false), action = 'add', jobId = null, clone = false } = $props();

    const formErrorAlert = 'form-job-alert';
    const urlExisting = `/api/job/${jobId}`;
    let formInfos = $state({});
    let loaded = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let url = $derived(['add', 'clone'].includes(action) ? '/api/job' : urlExisting);
    let formError = $state('');

    let form = $state({
        name: {value: '', color: inputRequiredBaseColor, required: true},
        comment: {value: '', color: inputBaseColor},
        repository: {value: 0, color: inputBaseColor},
        playbook_file: {value: '', color: inputRequiredBaseColor, browse: 'pb', required: true},
        inventory_file: {value: '', color: inputRequiredBaseColor, browse: 'inv'},  // NOTE: not required bc of dynamic inventories..
        limit: {value: '', color: inputBaseColor},
        tags: {value: '', color: inputBaseColor},
        tags_skip: {value: '', color: inputBaseColor},
        mode_diff: {value: false, color: toggleBaseColor},
        mode_check: {value: false, color: toggleBaseColor},
        verbosity: {value: 0, color: inputBaseColor},
        credentials_needed: {value: true, color: toggleBaseColor},
        credentials_default: {value: '', color: inputBaseColor},
        credentials_category: {value: '', color: inputBaseColor},
        schedule: {
            value: '', color: inputBaseColor,
            blank: true,
            regex: /^()|(@(annually|yearly|monthly|weekly|daily|hourly))|(@every (\d+(s|m|h))+)|((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5,7})$/
        },
        enabled: {value: true, color: toggleBaseColor},
        environment_vars: {value: '', color: inputBaseColor},
        cmd_args: {value: '', color: inputBaseColor},
        execution_prompts_required: {value: '', color: inputBaseColor},
        execution_prompts_optional: {value: '', color: inputBaseColor},
    });

    function getMethod(a: string) {
        if (a == 'delete') {
            return 'delete';
        }
        if (a == 'edit') {
            return 'put';
        }
        return 'post';
    }

    function t(code: string) {
      return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        console.log("RES", j);
        if (s == 200 && j.error === undefined) {
            open = false;
        } else {
            formError = `${j.error} (${s})`;
            let a = document.getElementById(formErrorAlert);
            if (a) {
                a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            }
        }
    }

    function submitForm() {
        // todo: write response errors to UI
        submitFormBase(form, method, url, handleSubmitResponse);
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
        if (clone) {
            existing.name = `${existing.name} - Copy`;
        }
        for (let [k, v] of Object.entries(existing)) {
            if (form[k]) {
                form[k].value = v;
            }
        }
        loaded = true;
    }

    onMount(() => {
        apiGet('frontend/form/job', setFormInfos);

        if (action != 'add' && jobId) {
            apiGet(urlExisting, loadExisting);
        }
    })

    // autocomplete via api filesystem-browsing (playbook/inventory)
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

    function fsBrowseBase(full: string) {
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

    function fsBrowseValidate(full: string) {
        console.log("TEST1", full);
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
        console.log("TEST2", form[f].value);
        let p = rsplit(form[f].value, '/');
        if (p[1] == null && !fsBrowseChoices.dirs.includes(p[0])) {
            form[f].value = c;
        } else {
            form[f].value = `${p[0]}/${c}`;
        }

        fsBrowse(f);
    }
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{t('jobs.new')}</Heading>
    {#if !loaded}
        <Spinner/>
    {:else}
        <div id={formErrorAlert} class="h-0"></div>
        {#if formError}
            <Alert border color="red">
                <CloseCircleSolid slot="icon" class="w-5 h-5" /> {formError}
            </Alert>
        {/if}
        <Accordion class={classModalForm}>
            <AccordionItem>
                <span slot="header">Main</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_name" class={classModalLabel}>{t('jobs.form.name')}</Label>
                        <Input id="job_name" name="name" bind:value={form.name.value} bind:color={form.name.color}
                        on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                    </div>
                    <div>
                        <Label for="job_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
                        <Input id="job_cmt" name="comment" bind:value={form.comment.value} bind:color={form.comment.color}
                        on:input={valideInput} />
                    </div>
                    <div>
                        <Label for="job_repo" class={classModalLabel}>{t('jobs.form.repository')}</Label>
                        <Select id="job_repo" name="repository" items={formInfos.choices.repository}
                        bind:value={form.repository.value} bind:color={form.repository.color} on:input={valideInput} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.repository')}</Helper>
                    </div>
                    <div>
                        <Label for="job_pb" class={classModalLabel}>{t('jobs.form.playbook_file')}</Label>
                        <Input id="job_pb" name="playbook_file"
                        bind:value={form.playbook_file.value} bind:color={form.playbook_file.color}
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
                                    <Spinner size="sm"/>
                                {/if}
                            </div>
                        {/if}
                        <Helper class={classModalHelp}>{t('jobs.form.help.playbook_file')}</Helper>
                    </div>
                    <div>
                        <Label for="job_inv" class={classModalLabel}>{t('jobs.form.inventory_file')}</Label>
                        <Input id="job_inv" name="inventory_file" on:input={valideInput}
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
            <AccordionItem>
                <span slot="header">Execution</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
                        <Input id="job_limit" name="limit" on:input={valideInput}
                        bind:value={form.limit.value} bind:color={form.limit.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.limit')}</Helper>
                    </div>
                    <div>
                        <Label for="job_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
                        <Input id="job_tags" name="tags" on:input={valideInput}
                        bind:value={form.tags.value} bind:color={form.tags.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.tags')}</Helper>
                    </div>
                    <div>
                        <Label for="job_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
                        <Input id="job_tags_skip" name="tags_skip" on:input={valideInput}
                        bind:value={form.tags_skip.value} bind:color={form.tags_skip.color} />
                    </div>
                    <div>
                        <Label for="job_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
                        <Toggle id="job_diff" name="mode_diff" bind:checked={form.mode_diff.value} bind:color={form.mode_diff.color} />

                        <Label for="job_chk" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
                        <Toggle id="job_chk" name="mode_check" bind:checked={form.mode_check.value} bind:color={form.mode_check.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.mode_check')}</Helper>
                    </div>
                    <div>
                        <Label for="job_verb" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
                        <Select id="job_verb" name="verbosity" items={formInfos.choices.verbosity}
                        bind:value={form.verbosity.value} bind:color={form.verbosity.color} />
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Credentials</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_creds" class={classModalLabel}>{t('jobs.form.credentials_needed')}</Label>
                        <Toggle id="job_creds" name="credentials_needed"
                        bind:checked={form.credentials_needed.value} bind:color={form.credentials_needed.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_needed')}</Helper>
                    </div>
                    <div>
                        <Label for="job_creds_dflt" class={classModalLabel}>{t('jobs.form.credentials_default')}</Label>
                        <Select id="job_creds_dflt" name="credentials_default" items={formInfos.choices.credentials_default}
                        bind:value={form.credentials_default.value} bind:color={form.credentials_default.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_default')}</Helper>
                    </div>
                    <div>
                        <Label for="job_creds_cat" class={classModalLabel}>{t('jobs.form.credentials_category')}</Label>
                        <Input id="job_creds_cat" name="credentials_category" on:input={valideInput}
                        bind:value={form.credentials_category.value} bind:color={form.credentials_category.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_category')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Scheduling</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_cron" class={classModalLabel}>{t('jobs.form.schedule')}</Label>
                        <Input id="job_cron" name="schedule" on:input={valideInput}
                        bind:value={form.schedule.value} bind:color={form.schedule.color} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.schedule')}</Helper>
                    </div>
                    <div>
                        <Label for="job_cron_en" class={classModalLabel}>{t('jobs.form.enabled')}</Label>
                        <Toggle id="job_cron_en" name="enabled" on:input={valideInput}
                        bind:checked={form.enabled.value} bind:color={form.enabled.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.enabled')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Additional</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_env" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
                        <Input id="job_env" name="environment_vars" on:input={valideInput}
                        bind:value={form.environment_vars.value} bind:color={form.environment_vars.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.environment_vars')}</Helper>
                    </div>
                    <div>
                        <Label for="job_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
                        <Input id="job_args" name="cmd_args" on:input={valideInput} 
                        bind:value={form.cmd_args.value} bind:color={form.cmd_args.color} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.cmd_args')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Execution Prompts</span>
                <div class={classModalInputDiv}>
                    <!--
                    <Label for="job_prompts_req" class={classModalLabel}>{t('jobs.form.execution_prompts_required')}</Label>
                    <Input id="job_prompts_req" name="execution_prompts_required" value={defaults.execution_prompts_required} />

                    <Label for="job_prompts_opt" class={classModalLabel}>{t('jobs.form.execution_prompts_optional')}</Label>
                    <Input id="job_prompts_opt" name="execution_prompts_optional" value={defaults.execution_prompts_optional} />
                    -->
                </div>
            </AccordionItem>
        </Accordion>

        <div class={classModalBtns}>
            <Button type="button" on:click={submitForm}>{t('btn.save')}</Button>
            <Button on:click={() => (open = false)} class="inline-block">{t('btn.discard')}</Button>
        </div>
    {/if}
</Modal>
