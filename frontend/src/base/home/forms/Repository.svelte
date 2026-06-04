<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Spinner, Tooltip, Helper, Select, Toggle,
        AccordionItem, Accordion,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { type formInfoType } from '../../Types.js';
    import { apiGet, cacheKey } from '../../../util/api.js';
    import { repoKindMap, REGEX_FORM_INT_GT0 } from '../../Config.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalForm, classModalInputDiv,
        classModalInput, classModalHelp, classSpinnerDiv, classSpoilerItem, classModalBody,
        classModalDialog, classSpoilerPad,
    } from '../../Style.js';

    let componentRoot;
    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
        rtypeName = 'static',
    } = $props();

    const urlExisting = `repository/${existingID}`;
    const ignoreFieldsStatic = [
        'git_origin',
        'git_branch',
        'git_credentials',
        'git_isolate',
        'git_lfs',
        'git_limit_depth',
        'git_hook_pre',
        'git_hook_post',
        'git_hook_cleanup',
        'git_override_initialize',
        'git_override_update',
        'git_playbook_base',
        'git_timeout',
        'ssh_hostkey_file',
    ];
    const ignoreFieldsGit = ['static_path'];

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let loaded = $state(false);
    let submitted = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? 'repository' : urlExisting);
    let title = $derived(actionNew ? t('repos.new') : t('repos.edit'));
    let formWarningMsgs: string[] = $state([]);
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        rtype: {value: repoKindMap[rtypeName]},
        static_path: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        git_origin: {value: '', color: inputBaseColor, required: true, regex: /^.{1,300}/},
        git_branch: {value: '', color: inputBaseColor, required: true, regex: /^.{0,300}/},
        git_credentials: {value: '', color: inputBaseColor, required: false, regex: /^.{0,50}/},
        git_isolate: {value: false, color: inputBaseColor, required: false, regex: /^.{0,300}/},
        git_lfs: {value: false, color: inputBaseColor, required: false, regex: /^.{0,300}/},
        git_limit_depth: {value: '', color: inputBaseColor, required: false, regex: /^.{0,3000}/},
        git_hook_pre: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_hook_post: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_hook_cleanup: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_override_initialize: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_override_update: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_playbook_base: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        git_timeout: {value: '', color: inputBaseColor, required: false, regex: REGEX_FORM_INT_GT0},
        ssh_hostkey_file: {value: '', color: inputBaseColor, required: false},
    });

    function t(code: string) : string {
        return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'repos.action.create' : 'repos.action.update';
            success = true;
            open = false;
        } else {
            apiResponseHandler.handleRes(s, j);
            submitted = false;
        }
    }

    function submitForm() {
        if (submitted) {
            return;
        }
        let igoreFields = ignoreFieldsStatic;
        if (rtypeName == 'git') {
            igoreFields = ignoreFieldsGit;
        }

        submitted = true;
        let [valid, errors] = submitFormBase(
            form, method, url, handleSubmitResponse, t, 'repos.form.', [], igoreFields,
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
            form.rtype.value = repoKindMap[rtypeName];
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
        loaded = true;
    }

    function fetchBuild() {
        apiGet(`frontend/form/repository?${cacheKey($share)}`, setFormInfos);

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
    });

    onDestroy(()=>{
        if (componentRoot) {
            componentRoot.removeEventListener('keyup', handleKeyUp);
            componentRoot.removeEventListener('keydown', handleKeyDown);
        }
    });
</script>

<div bind:this={componentRoot} tabindex="-1" class="inline-block">
<Modal bind:open={open} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <Heading tag="h2">
        {title}{#if !actionNew}: "{form.name.value}"{/if}
    </Heading>
    {#if !loaded}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <APIResponseHandler bind:this={apiResponseHandler} bind:warningMsgs={formWarningMsgs} />
        {#if rtypeName == 'static'}
            <div class={classModalInputDiv}>
                <div class={classModalInput}>
                    <Label for="repo_name" class={classModalLabel}>{t('common.name')}</Label>
                    <Input id="repo_name" bind:value={form.name.value} bind:color={form.name.color}
                        on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                </div>
                    <div class={classModalInput}>
                        <Label for="repo_path" class={classModalLabel}>{t('common.path')}</Label>
                        <Input id="repo_path" bind:value={form.static_path.value} bind:color={form.static_path.color}
                            on:input={valideInput} on:blur={valideInput} required={form.static_path.required} />
                        <Helper class={classModalHelp}>{@html t('repos.form.help.static_path')}</Helper>
                    </div>
                </div>
        {:else}
            <div class={classModalInputDiv}>
                <div class={classModalInput}>
                    <Label for="repo_name" class={classModalLabel}>{t('common.name')}</Label>
                    <Input id="repo_name" bind:value={form.name.value} bind:color={form.name.color}
                        on:input={valideInput} on:blur={valideInput} required={form.name.required} />
                </div>
                <div class={classModalInput}>
                    <Label for="repos_git_origin" class={classModalLabel}>{t('repos.form.git_origin')}</Label>
                    <Input id="repos_git_origin" required={form.git_origin.required}
                        bind:value={form.git_origin.value} bind:color={form.git_origin.color}
                        on:input={valideInput} on:blur={valideInput} />
                    <Helper class={classModalHelp}>{@html t('repos.form.help.git_origin')}</Helper>
                </div>
                <div class={classModalInput}>
                    <Label for="repos_git_branch" class={classModalLabel}>{t('repos.form.git_branch')}</Label>
                    <Input id="repos_git_branch" required={form.git_branch.required}
                        bind:value={form.git_branch.value} bind:color={form.git_branch.color}
                        on:input={valideInput} on:blur={valideInput} />
                </div>
                <div class={classModalInput}>
                    <Label for="repos_git_creds" class={classModalLabel}>{t('repos.form.git_credentials')}</Label>
                    <Select id="repos_git_creds" items={formInfos.choices.git_credentials}
                        bind:value={form.git_credentials.value} bind:color={form.git_credentials.color} />
                    <Helper class={classModalHelp}>{t('repos.form.help.git_credentials')}</Helper>
                </div>
            </div>
            <Accordion class={classModalForm}>
                <AccordionItem defaultClass="{classSpoilerItem} repo-form-git-opts" paddingDefault={classSpoilerPad}>
                    <span slot="header">{t('repos.form.git_options')}</span>
                    <div class={classModalInputDiv}>
                        <div class={classModalInput}>
                            <Label for="repos_git_depth" class={classModalLabel}>{t('repos.form.git_limit_depth')}</Label>
                            <Input id="repos_git_depth" type="number"
                                bind:value={form.git_limit_depth.value} bind:color={form.git_limit_depth.color}
                                on:input={valideInput} on:blur={valideInput} />
                        </div>
                        <div class={classModalInput}>
                            <Label for="repos_git_pb_base" class={classModalLabel}>{t('repos.form.git_playbook_base')}</Label>
                            <Input id="repos_git_pb_base" bind:value={form.git_playbook_base.value}
                                bind:color={form.git_playbook_base.color}
                                on:input={valideInput} on:blur={valideInput} />
                            <Helper class={classModalHelp}>{@html t('repos.form.help.git_playbook_base')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repo_git_lfs" class={classModalLabel}>{t('repos.form.git_lfs')}</Label>
                            <Toggle id="repo_git_lfs" bind:checked={form.git_lfs.value} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_lfs')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repo_git_isolate" class={classModalLabel}>{t('repos.form.git_isolate')}</Label>
                            <Toggle id="repo_git_isolate" bind:checked={form.git_isolate.value} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_isolate')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repo_git_timeout" class={classModalLabel}>{t('repos.form.git_timeout')}</Label>
                            <Input id="repo_git_timeout" type="number" bind:value={form.git_timeout.value}
                                bind:color={form.git_timeout.color}
                                on:input={valideInput} on:blur={valideInput} />
                        </div>
                        <div class={classModalInput}>
                            <Label for="repo_ssh_hostkey_file" class={classModalLabel}>{t('system.ssh_hostkey')}</Label>
                            <Select id="repo_ssh_hostkey_file" items={formInfos.choices.ssh_hostkey_file}
                                bind:value={form.ssh_hostkey_file.value} bind:color={form.ssh_hostkey_file.color} />
                        </div>
                    </div>
                </AccordionItem>
                <AccordionItem defaultClass="{classSpoilerItem} repo-form-git-hooks" paddingDefault={classSpoilerPad}>
                    <span slot="header">{t('repos.form.git_hooks')}</span>
                    <div class={classModalInputDiv}>
                        <div class={classModalInput}>
                            <Label for="repos_git_hook_pre" class={classModalLabel}>{t('repos.form.git_hook_pre')}</Label>
                            <Input id="repos_git_hook_pre" bind:value={form.git_hook_pre.value} bind:color={form.git_hook_pre.color}
                                on:input={valideInput} on:blur={valideInput} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_hook_pre')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repos_git_hook_post" class={classModalLabel}>{t('repos.form.git_hook_post')}</Label>
                            <Input id="repos_git_hook_post" bind:value={form.git_hook_post.value} bind:color={form.git_hook_post.color}
                                on:input={valideInput} on:blur={valideInput} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_hook_post')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repos_git_hook_clean" class={classModalLabel}>{t('repos.form.git_hook_cleanup')}</Label>
                            <Input id="repos_git_hook_clean" bind:value={form.git_hook_cleanup.value} bind:color={form.git_hook_cleanup.color}
                                on:input={valideInput} on:blur={valideInput} />
                        </div>
                        <div class={classModalInput}>
                            <Label for="repos_git_hook_ovr_init" class={classModalLabel}>{t('repos.form.git_override_initialize')}</Label>
                            <Input id="repos_git_hook_ovr_init" bind:value={form.git_override_initialize.value} bind:color={form.git_override_initialize.color}
                                on:input={valideInput} on:blur={valideInput} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_override_initialize')}</Helper>
                        </div>
                        <div class={classModalInput}>
                            <Label for="repos_git_hook_ovr_update" class={classModalLabel}>{t('repos.form.git_override_update')}</Label>
                            <Input id="repos_git_hook_ovr_update" bind:value={form.git_override_update.value} bind:color={form.git_override_update.color}
                                on:input={valideInput} on:blur={valideInput} />
                            <Helper class={classModalHelp}>{t('repos.form.help.git_override_update')}</Helper>
                        </div>
                    </div>
                </AccordionItem>
            </Accordion>
        {/if}

        <div class={classModalBtns}>
            <Button id="repo-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button id="repo-btn-discard" on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
    {/if}
</Modal>
</div>