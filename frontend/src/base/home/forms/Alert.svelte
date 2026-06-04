<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    
    import { CloseCircleSolid, FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Heading, Button, Input, Label, Spinner, Tooltip, Select, Toggle, MultiSelect,
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
        classModalInput, classSpinnerDiv, classModalBody, classModalDialog,
    } from '../../Style.js';

    const ALERT_TYPE_PLUGIN = 1;

    let componentRoot;
    let {
        open = $bindable(false),
        successMsg = $bindable(''),
        success = $bindable(false),
        action = 'add',
        existingID = null,
        kind = 'global',
    } = $props();

    const urlBase = `alert/${kind}`
    const urlExisting = `${urlBase}/${existingID}`;
    const exclusiveFieldGroup = 'group';
    const exclusiveFieldUser = 'user';

    let apiResponseHandler: APIResponseHandler = $state();
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});
    let loaded = $state(false);
    let submitted = $state(false);
    let existing = $state({});
    let method: formMethod = $derived(getMethod(action));
    let actionNew = $derived(['add', 'clone'].includes(action));
    let url = $derived(actionNew ? urlBase : urlExisting);
    let title = $derived(actionNew ? t('alerts.new') : t('alerts.edit'));
    let formWarningMsgs: string[] = $state([]);
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

    let form = $state({
        name: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        alert_type: {value: 0, color: inputBaseColor, required: false},
        plugin: {value: 0, color: inputBaseColor, required: true},
        jobs_all: {value: false, color: inputBaseColor, required: false},
        jobs: {value: [], color: inputBaseColor, required: false},
        condition: {value: 0, color: inputBaseColor, required: false},
        group: {value: 0, color: inputBaseColor, required: true},
        user: {value: $share.backend.user_id},
    });

    function t(code: string) : string {
        return tq($share, code);
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            successMsg = actionNew ? 'alerts.action.create' : 'alerts.action.update';
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
        let igoreFields = [];
        if (kind != 'group') {
            igoreFields.push(exclusiveFieldGroup);
        }
        if (kind != 'user') {
            igoreFields.push(exclusiveFieldUser);
        }
        if (form.alert_type.value != ALERT_TYPE_PLUGIN) {
            igoreFields.push('plugin');
        }

        submitted = true;
        let [valid, errors] = submitFormBase(
            form, method, url, handleSubmitResponse, t, 'alerts.form.', [], igoreFields,
        );
        if (!valid) {
            formWarningMsgs = errors;
        }
    }

    function setFormInfos(j: any) {
        formInfos = j;
        if (!isSet(formInfos.choices.jobs)) {
            formInfos.choices.jobs = [];
        }
        if (action == 'add') {
            for (let [k, v] of Object.entries(formInfos.defaults)) {
                if (k in form) {
                    if (k == 'jobs' && !isSet(v)) {
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
                form[k].value = v;
            }
        }
        loaded = true;
    }

    function fetchBuild() {
        apiGet(`frontend/form/alert/${kind}?${cacheKey($share)}`, setFormInfos);

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
                <Label for="alert_name" class={classModalLabel}>{t('common.name')}</Label>
                <Input id="alert_name" bind:value={form.name.value} bind:color={form.name.color}
                    on:input={valideInput} on:blur={valideInput} required={form.name.required} />
            </div>
            <div class={classModalInput}>
                <Label for="alert_condition" class={classModalLabel}>{t('alerts.form.condition')}</Label>
                <Select id="alert_condition" items={formInfos.choices.condition}
                    bind:value={form.condition.value} bind:color={form.condition.color} />
            </div>
            <div class={classModalInput}>
                <Label for="alert_type" class={classModalLabel}>{t('common.kind')}</Label>
                <Select id="alert_type" items={formInfos.choices.alert_type}
                    bind:value={form.alert_type.value} bind:color={form.alert_type.color} />
            </div>
            {#if form.alert_type.value == ALERT_TYPE_PLUGIN}
                <div class={classModalInput}>
                    <Label for="alert_plugin" class={classModalLabel}>{t('alerts.plugin')}</Label>
                    <Select id="alert_plugin" items={formInfos.choices.plugin}
                        bind:value={form.plugin.value} bind:color={form.plugin.color} />
                </div>
            {/if}
        </div>
        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="alert_jobs" class={classModalLabel}>{t('home.jobs')}</Label>
                <MultiSelect id="alert_jobs" items={formInfos.choices.jobs}
                    disabled={!formInfos.choices.jobs || formInfos.choices.jobs.length == 0}
                    bind:value={form.jobs.value} bind:color={form.jobs.color} />
            </div>
            <div class={classModalInput}>
                <Label for="alert_all_jobs" class={classModalLabel}>{t('alerts.form.jobs_all')}</Label>
                <Toggle id="alert_all_jobs" bind:checked={form.jobs_all.value} />
            </div>
            {#if kind == 'group'}
                <div class={classModalInput}>
                    <Label for="alert_group" class={classModalLabel}>{t('alerts.group')}</Label>
                    <Select id="alert_group" items={formInfos.choices.group}
                        bind:value={form.group.value} bind:color={form.group.color} />
                </div>
            {/if}
        </div>

        <div class={classModalBtns}>
            <Button id="alert-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
            <Tooltip>{t('btn.save')}</Tooltip>

            <Button id="alert-btn-discard" on:click={() => (open = false)} class="inline-block ml-2"><CloseCircleSolid/></Button>
            <Tooltip>{t('btn.discard')}</Tooltip>
        </div>
    {/if}
</Modal>
</div>
