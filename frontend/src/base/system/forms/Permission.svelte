<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Spinner, Tooltip, Select, Toggle,
        MultiSelect,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { isSet } from '../../../util/main.js';
    import { tq } from '../../../util/translate.js';
    import { type formInfoType } from '../../Types.js';
    import { apiGet, cacheKey } from '../../../util/api.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import {
        inputBaseColor, valideInputBase, submitFormBase, getMethod,
        type formMethod,
    } from '../../../util/form.js';
    import {
        classModalBackdrop, classModalLabel, classModalBtns, classModalInputDiv,
        classModalInput, classFooterSpacing, classSpinnerDiv, classModalBody, classModalDialog,
    } from '../../Style.js';

    let componentRoot;
    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
   } = $props();

    const urlExisting = `permission/${existingID}`;
    const fieldsList = ['jobs', 'credentials', 'repositories', 'users', 'groups'];

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let loaded = $state(false);
    let submitted = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? 'permission' : urlExisting);
    let title = $derived(actionNew ? t('permission.new') : t('permission.edit'));
    let formWarningMsgs: string[] = $state([]);
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        permission: {value: 0, color: inputBaseColor, required: true},
        jobs: {value: [], color: inputBaseColor, required: false},
        jobs_all: {value: false, color: inputBaseColor, required: false},
        credentials: {value: [], color: inputBaseColor, required: false},
        credentials_all: {value: false, color: inputBaseColor, required: false},
        repositories: {value: [], color: inputBaseColor, required: false},
        repositories_all: {value: false, color: inputBaseColor, required: false},
        users: {value: [], color: inputBaseColor, required: false},
        groups: {value: [], color: inputBaseColor, required: false},
    });

    function t(code: string) : string {
        return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'permission.action.create' : 'permission.action.update';
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
        submitted = true;
        let [valid, errors] = submitFormBase(
            form, method, url, handleSubmitResponse, t, 'permission.form.', [],
        );
        if (!valid) {
            formWarningMsgs = errors;
        }
    }

    function setFormInfos(j: any) {
        for (let f of fieldsList) {
            if (!isSet(j.choices[f])) {
                j.choices[f] = [];
            }
        }
        formInfos = j;

        if (action == 'add') {
            for (let [k, v] of Object.entries(formInfos.defaults)) {
                if (k in form) {
                    if (fieldsList.includes(k) && !isSet(v)) {
                        continue;
                    }
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
                if (fieldsList.includes(k) && !isSet(v)) {
                    continue;
                }
                form[k].value = v;
            }
        }
        loaded = true;
    }

    function fetchBuild() {
        apiGet(`frontend/form/permission?${cacheKey($share)}`, setFormInfos);

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
        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_name" class={classModalLabel}>{t('common.name')}</Label>
                <Input id="perm_name" bind:value={form.name.value} bind:color={form.name.color}
                    on:input={valideInput} on:blur={valideInput} required={form.name.required} />
            </div>
            <div class={classModalInput}>
                <Label for="perm_lvl" class={classModalLabel}>{t('permission.level')}</Label>
                <Select id="perm_lvl" items={formInfos.choices.permission}
                    bind:value={form.permission.value} bind:color={form.permission.color} />
            </div>
        </div>
        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_job_all" class={classModalLabel}>{t('permission.jobs_all')}</Label>
                <Toggle id="perm_job_all" bind:checked={form.jobs_all.value} />
            </div>
            <div class={classModalInput}>
                <Label for="perm_creds_all" class={classModalLabel}>{t('permission.credentials_all')}</Label>
                <Toggle id="perm_creds_all" bind:checked={form.credentials_all.value} />
            </div>
            <div class={classModalInput}>
                <Label for="perm_repos_all" class={classModalLabel}>{t('permission.repositories_all')}</Label>
                <Toggle id="perm_repos_all" bind:checked={form.repositories_all.value} />
            </div>
        </div>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_jobs" class={classModalLabel}>{t('home.jobs')}</Label>
                <MultiSelect id="perm_jobs" items={formInfos.choices.jobs}
                    disabled={!formInfos.choices.jobs || formInfos.choices.jobs.length == 0 || form.jobs_all.value}
                    bind:value={form.jobs.value} bind:color={form.jobs.color} />
            </div>
        </div>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_creds" class={classModalLabel}>{t('home.creds')}</Label>
                <MultiSelect id="perm_creds" items={formInfos.choices.credentials}
                    disabled={!formInfos.choices.credentials || formInfos.choices.credentials.length == 0 || form.credentials_all.value}
                    bind:value={form.credentials.value} bind:color={form.credentials.color} />
            </div>
        </div>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_repos" class={classModalLabel}>{t('home.repos')}</Label>
                <MultiSelect id="perm_repos" items={formInfos.choices.repositories}
                    disabled={!formInfos.choices.repositories || formInfos.choices.repositories.length == 0 || form.repositories_all.value}
                    bind:value={form.repositories.value} bind:color={form.repositories.color} />
            </div>
        </div>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="perm_users" class={classModalLabel}>{t('permission.users')}</Label>
                <MultiSelect id="perm_users" items={formInfos.choices.users}
                    bind:value={form.users.value} bind:color={form.users.color} />
            </div>
            <div class={classModalInput}>
                <Label for="perm_groups" class={classModalLabel}>{t('permission.groups')}</Label>
                <MultiSelect id="perm_groups" items={formInfos.choices.groups}
                    bind:value={form.groups.value} bind:color={form.groups.color} />
            </div>
        </div>
        <div class={classModalBtns}>
            <Button id="perm-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button id="perm-btn-discard" on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
        <div class={classFooterSpacing}></div>
    {/if}
</Modal>
</div>