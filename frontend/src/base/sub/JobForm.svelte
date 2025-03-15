<script lang="ts">
    import { onMount } from 'svelte';

    import { FolderSolid, FileSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Modal, Input, Label, Helper, Toggle, Select, Spinner,
        AccordionItem, Accordion,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { rsplit } from '../../util/main.js';
    import { tq } from '../../util/translate.js';
    import {
        classModalBackdrop, classModalLabel, classModalHelp, classModalBtns, classModalForm,
        classModalInputDiv,
    } from '../Style.js';
    import { apiGet, apiForm, getCSRFFormToken } from '../../util/api.js';

    // todo: reset to default if 'add' form gets closed
    let { open = $bindable(false), action = 'add', jobId = null, clone = false } = $props();

    const urlExisting = `/api/job/${jobId}`;
    let formInfos = $state({});
    let loaded = $state(false);
    let existing = $state({});
    let method = $derived(getMethod(action));
    let defaults = $derived(action == 'add' ? formInfos.defaults : existing );
    let url = $derived(['add', 'clone'].includes(action) ? '/api/job' : urlExisting);

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

    function handleSubmitResponse(j: any) {
        console.log("RES", j);
        // if not error
        open = false;
    }

    function handleSubmit(e: SubmitEvent) {
        console.log(e);
        apiForm(e, handleSubmitResponse);
    }

    function setFormInfos(j: any) {
        formInfos = j;
        if (action == 'add') {
            loaded = true;
            repository = defaults.repository;
        }
    }

    function loadExisting(j: any) {
        existing = j;
        if (clone) {
            existing.name = `${existing.name} - Copy`;
        }
        repository = existing.repository;
        playbook = existing.playbook;
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
    const fsBrowseActivePb = 'pb';
    const fsBrowseActiveInv = 'inv';
    const inputBaseColor = 'base';
    let repository = $state(0);
    let playbook = $state('');
    let inventory = $state('');
    let fsBrowseActive: string = $state('');
    let fsBrowseChoices: browseResponse = $state(fsBrowseNone);
    let colorPlaybook = $state(inputBaseColor);
    let colorInventory = $state(inputBaseColor);

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
        if (f == fsBrowseActivePb) {
            b = fsBrowseBase(playbook);
            if (b == playbook && !(playbook.slice(-1)[0] == '/') && playbook != '') {
                playbook += '/';
            }

        } else if (f == fsBrowseActiveInv) {
            b = fsBrowseBase(inventory);
            if (b == inventory && !(inventory.slice(-1)[0] == '/') && inventory != '') {
                inventory += '/';
            }

        } else {
            return;
        }

        apiGet(`fs/browse/${repository||0}?base=${b}`, (j: any) => {fsBrowseUpdate(j, f)});
    }

    function fsBrowseClear() {
        fsBrowseActive = '';
        fsBrowseChoices = fsBrowseNone;
    }

    function fsBrowseValidate(full: string) {
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

        if (f == fsBrowseActivePb) {
            colorPlaybook = fsBrowseValidate(playbook);
        } else if (f == fsBrowseActiveInv) {
            colorInventory = fsBrowseValidate(inventory);
        }
    }

    function fsBrowseSelect(f: string, c: string) {
        if (f == fsBrowseActivePb) {
            let p = rsplit(playbook, '/');
            if (p[1] == null && !fsBrowseChoices.dirs.includes(p[0])) {
                playbook = c;
            } else {
                playbook = `${p[0]}/${c}`;
            }

        } else if (f == fsBrowseActiveInv) {
            let p = rsplit(inventory, '/');
            if (p[1] == null && !fsBrowseChoices.dirs.includes(p[0])) {
                inventory = c;
            } else {
                inventory = `${p[0]}/${c}`;
            }
        }

        fsBrowse(f);
    }
</script>

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{t('jobs.new')}</Heading>
    {#if !loaded}
        <Spinner/>
    {:else}
    <form onsubmit={handleSubmit} action={url} method={method} class={classModalForm}>
        <Accordion>
            <AccordionItem>
                <span slot="header">Main</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_name" class={classModalLabel}>{t('jobs.form.name')}</Label>
                        <Input id="job_name" name="name" value={defaults.name} />
                    </div>
                    <div>
                        <Label for="job_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
                        <Input id="job_cmt" name="comment" value={defaults.comment} />
                    </div>
                    <div>
                        <Label for="job_repo" class={classModalLabel}>{t('jobs.form.repository')}</Label>
                        <Select id="job_repo" name="repository" items={formInfos.choices.repository} bind:value={repository} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.repository')}</Helper>
                    </div>
                    <div>
                        <Label for="job_pb" class={classModalLabel}>{t('jobs.form.playbook_file')}</Label>
                        <Input id="job_pb" name="playbook_file" bind:value={playbook} bind:color={colorPlaybook}
                        on:input={() => {fsBrowse(fsBrowseActivePb)}}
                        on:click={() => {fsBrowseClick(fsBrowseActivePb)}} />
                        {#if fsBrowseActive == fsBrowseActivePb}
                            <div class={classFsBrowse}>
                                {#each fsBrowseChoices.files as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect(fsBrowseActivePb, c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoices.dirs as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect(fsBrowseActivePb, c)}}>
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
                        <Input id="job_inv" name="inventory_file" bind:value={inventory} bind:color={colorInventory}
                        on:input={() => {fsBrowse(fsBrowseActiveInv)}}
                        on:click={() => {fsBrowseClick(fsBrowseActiveInv)}} />
                        {#if fsBrowseActive == fsBrowseActiveInv}
                            <div class={classFsBrowse}>
                                {#each fsBrowseChoices.files as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect(fsBrowseActiveInv, c)}}>
                                        <FileSolid class="inline-block" /> {c}
                                    </button>
                                {/each}
                                {#each fsBrowseChoices.dirs as c}
                                    <button type="button" class={classFsBrowseItem}
                                    onclick={(e) => {fsBrowseSelect(fsBrowseActiveInv, c)}}>
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
                        <Input id="job_limit" name="limit" value={defaults.limit} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.limit')}</Helper>
                    </div>
                    <div>
                        <Label for="job_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
                        <Input id="job_tags" name="tags" value={defaults.tags} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.tags')}</Helper>
                    </div>
                    <div>
                        <Label for="job_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
                        <Input id="job_tags_skip" name="tags_skip" value={defaults.tags_skip} />
                    </div>
                    <div>
                        <Label for="job_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
                        <Toggle id="job_diff" name="mode_diff" value={defaults.mode_diff} />

                        <Label for="job_chk" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
                        <Toggle id="job_chk" name="mode_check" value={defaults.mode_check} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.mode_check')}</Helper>
                    </div>
                    <div>
                        <Label for="job_verb" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
                        <Select id="job_verb" name="verbosity" items={formInfos.choices.verbosity} value={defaults.verbosity} />
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Credentials</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_creds" class={classModalLabel}>{t('jobs.form.credentials_needed')}</Label>
                        <Toggle id="job_creds" name="credentials_needed" value={defaults.credentials_needed} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_needed')}</Helper>
                    </div>
                    <div>
                        <Label for="job_creds_dflt" class={classModalLabel}>{t('jobs.form.credentials_default')}</Label>
                        <Select id="job_creds_dflt" name="credentials_default" items={formInfos.choices.credentials_default} value={defaults.credentials_default} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_default')}</Helper>
                    </div>
                    <div>
                        <Label for="job_creds_cat" class={classModalLabel}>{t('jobs.form.credentials_category')}</Label>
                        <Input id="job_creds_cat" name="credentials_category" value={defaults.credentials_category} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_category')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Scheduling</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_cron" class={classModalLabel}>{t('jobs.form.schedule')}</Label>
                        <Input id="job_cron" name="schedule" value={defaults.schedule} />
                        <Helper class={classModalHelp}>{@html t('jobs.form.help.schedule')}</Helper>
                    </div>
                    <div>
                        <Label for="job_cron_en" class={classModalLabel}>{t('jobs.form.enabled')}</Label>
                        <Toggle id="job_cron_en" name="enabled" value={defaults.enabled} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.enabled')}</Helper>
                    </div>
                </div>
            </AccordionItem>
            <AccordionItem>
                <span slot="header">Additional</span>
                <div class={classModalInputDiv}>
                    <div>
                        <Label for="job_env" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
                        <Input id="job_env" name="environment_vars" value={defaults.environment_vars} />
                        <Helper class={classModalHelp}>{t('jobs.form.help.environment_vars')}</Helper>
                    </div>
                    <div>
                        <Label for="job_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
                        <Input id="job_args" name="cmd_args" value={defaults.cmd_args} />
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

        {@html getCSRFFormToken()}
        <div class={classModalBtns}>
            <Button type="submit">{t('btn.save')}</Button>
            <Button on:click={() => (open = false)} class="inline-block">{t('btn.discard')}</Button>
        </div>
    </form>
    {/if}
</Modal>
