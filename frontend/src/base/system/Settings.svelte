<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { FloppyDiskSolid, EnvelopeSolid, LayersSolid, TerminalSolid, FolderDuplicateSolid } from 'flowbite-svelte-icons';
    import {
        Button, Tooltip, Accordion, AccordionItem, Label, Input, Toggle, Select, Helper, Spinner,
        Heading, Hr,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { type formInfoType } from '../Types.js';
    import { SECRET_PLACEHOLDER } from '../Config.js';
    import { apiGet, cacheKey } from '../../util/api.js';
    import { choicesFromArray } from '../../util/form.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { valideInputBase, inputBaseColor, submitFormBase } from '../../util/form.js';
    import {
        classModalBtns, classModalLabel, classModalInput, classModalHelp, classModalInputDiv, classSpinnerDiv,
        classFooterSpacing, classSpoilerItem, classSpoilerPad,
    } from '../Style.js';

    let componentRoot;
    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let formWarningMsgs: string[] = $state([]);
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let loaded = $state(false);
    let pressedKeyAlt = $state(false);
    let pressedKeyS = $state(false);

    interface formInfoExtType extends formInfoType {
        env_vars: any
    }
    let formInfos: formInfoExtType = $state({defaults: {}, choices: {}, env_vars: {}});

    interface settingsBaseType {
        path_run: string
        path_play: string
        path_log: string
        path_template: string|null
        timezone: string
        run_timeout: number|string
        session_timeout: number|string
        path_ansible_config: string|null
        path_ssh_known_hosts: string|null
        debug: boolean
        audit_log: boolean
        logo_url: string
        ara_server: string|null
        global_environment_vars: string|null
        mail_server: string|null
        mail_transport: number
        mail_ssl_verify: boolean
        mail_sender: string|null
        mail_user: string|null
        ansible_executor: number
    }
    interface settingsReadType extends settingsBaseType {
        db: string
        db_migrate: boolean|null
        deployment: string
        version: string
        mail_pass_is_set: boolean
    }
    interface settingsReadFullType {
        read_only: string[]
        settings: settingsReadType
        env_vars: any
    }
    let settingsRead: settingsReadFullType = $state({env_vars: {}, settings: {}, read_only: []});
    let form = $state({
        path_run: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_play: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_log: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_template: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        timezone: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        run_timeout: {value: 60*60, color: inputBaseColor, required: true},
        session_timeout: {value: 60*60*12, color: inputBaseColor, required: true},
        path_ansible_config: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        path_ssh_known_hosts: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        debug: {value: false},
        audit_log: {value: true},
        logo_url: {value: 'img/logo.svg', color: inputBaseColor, required: false, regex: /^.{0,200}/},
        ara_server: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        global_environment_vars: {value: '', color: inputBaseColor, required: false, regex: /^.{0,1000}/},
        mail_server: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        mail_transport: {value: 0, color: inputBaseColor, required: false, regex: /^.{0,100}/},
        mail_ssl_verify: {value: false},
        mail_sender: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        mail_user: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        mail_pass: {value: '', color: inputBaseColor, required: false, regex: /^.{0,100}/},
        ansible_executor: {value: 0, color: inputBaseColor, required: false},
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    function submitForm() {
        apiSuccessMsg = 'config.action.update';
        let [valid, errors] = submitFormBase(
            form, 'put', 'config', apiResponseHandler.handleRes, t, 'config.form.', settingsRead.read_only,
        );
        if (!valid) {
            formWarningMsgs = errors;
        }
    }

    function setFormInfos(j: any) {
        formInfos = j;
        for (let [k, v] of Object.entries(formInfos.defaults)) {
            if (k in form) {
                form[k].value = v;
            }
        }
        loaded = true;
        buildUpdateSettings();
    }

    function isRO(k: string): boolean {
        return settingsRead.read_only.includes(k);
    }

    function isDeploymentDev(): boolean {
        return Object.keys(settingsRead.env_vars).includes('deployment') && settingsRead.env_vars['deployment'] == 'dev';
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function loadSettings(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        settingsRead = j;
        for (let [k, v] of Object.entries(settingsRead.settings)) {
            if (k in form) {
                form[k].value = v;
            }
        }
        if (settingsRead.settings.mail_pass_is_set) {
            form.mail_pass.value = SECRET_PLACEHOLDER;
        }
        apiDataHash = h;
    }

    function buildUpdateSettings() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`config?hash=${apiDataHash}`, loadSettings);
    }

    function fetchInfos() {
        apiGet(`frontend/form/config?${cacheKey($share)}`, setFormInfos)
    }

    onMount(() => {
        if (!loaded) {
            setTimeout(fetchInfos, 500);  // wait to fetch version
        }
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateSettings();
        }, $share.updateInterval);
    });

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
        if (!loaded) {
            setTimeout(fetchInfos, 500);  // wait to fetch version
        }

        if (componentRoot) {
            componentRoot.addEventListener('keyup', handleKeyUp);
            componentRoot.addEventListener('keydown', handleKeyDown);
        }

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateSettings();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
        clearInterval(updateLoop);
        if (componentRoot) {
            componentRoot.removeEventListener('keyup', handleKeyUp);
            componentRoot.removeEventListener('keydown', handleKeyDown);
        }
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg}
    bind:warningMsgs={formWarningMsgs} />

<div bind:this={componentRoot} tabindex="-1" class="w-full">
{#if !loaded}
    <div class={classSpinnerDiv}><Spinner/></div>
{:else}
<Accordion>
    <AccordionItem defaultClass="{classSpoilerItem} settings-exec" paddingDefault={classSpoilerPad}>
        <span slot="header">
            <TerminalSolid class="inline-block"/> {t('config.execution')}
        </span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_executor" class={classModalLabel}>{t('config.form.ansible_executor')}</Label>
                <Select id="cnf_executor" items={formInfos.choices.ansible_executor}
                    bind:value={form.ansible_executor.value}
                    disabled={isRO('ansible_executor')} />
                {#if isRO('ansible_executor')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.ansible_executor')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_ara" class={classModalLabel}>{t('config.form.ara_server')}</Label>
                <Input id="cnf_ara" bind:value={form.ara_server.value} bind:color={form.ara_server.color}
                    on:input={valideInput} on:blur={valideInput} required={form.ara_server.required}
                    disabled={isRO('ara_server')} />
                {#if isRO('ara_server')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.ara_server')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_glob_env_vars" class={classModalLabel}>{t('config.form.global_environment_vars')}</Label>
                <Input id="cnf_glob_env_vars" bind:value={form.global_environment_vars.value}
                    bind:color={form.global_environment_vars.color} on:input={valideInput} on:blur={valideInput}
                    required={form.global_environment_vars.required} disabled={isRO('global_environment_vars')} />
                {#if isRO('global_environment_vars')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.global_environment_vars')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_to_run" class={classModalLabel}>{t('config.form.run_timeout')}</Label>
                <Input id="cnf_to_run" bind:value={form.run_timeout.value} bind:color={form.run_timeout.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required}
                    type="number" disabled={isRO('run_timeout')} />
                {#if isRO('run_timeout')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>
        </div>
    </AccordionItem>
    <AccordionItem defaultClass="{classSpoilerItem} settings-paths" paddingDefault={classSpoilerPad}>
        <span slot="header">
            <FolderDuplicateSolid class="inline-block"/> {t('config.paths')}
        </span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_path_run" class={classModalLabel}>{t('config.form.path_run')}</Label>
                <Input id="cnf_path_run" bind:value={form.path_run.value} bind:color={form.path_run.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_run.required}
                    disabled={isRO('path_run')} />
                {#if isRO('path_run')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.path_run')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_play" class={classModalLabel}>{t('config.form.path_play')}</Label>
                <Input id="cnf_path_play" bind:value={form.path_play.value} bind:color={form.path_play.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_play.required}
                    disabled={isRO('path_play')} />
                {#if isRO('path_play')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.path_play')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_log" class={classModalLabel}>{t('config.form.path_log')}</Label>
                <Input id="cnf_path_log" bind:value={form.path_log.value} bind:color={form.path_log.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required}
                    disabled={isRO('path_log')} />
                {#if isRO('path_log')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{t('config.form.help.path_log')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_tmpl" class={classModalLabel}>{t('config.form.path_template')}</Label>
                <Input id="cnf_path_tmpl" bind:value={form.path_template.value} bind:color={form.path_template.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_template.required}
                    disabled={isRO('path_template')} />
                {#if isRO('path_template')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{t('config.form.help.path_template')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_ans_cnf" class={classModalLabel}>{t('config.form.path_ansible_config')}</Label>
                <Input id="cnf_path_ans_cnf" bind:value={form.path_ansible_config.value} bind:color={form.path_ansible_config.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_ansible_config.required}
                    disabled={isRO('path_ansible_config')} />
                {#if isRO('path_ansible_config')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.path_ansible_config')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_ssh_kh" class={classModalLabel}>{t('config.form.path_ssh_known_hosts')}</Label>
                <Input id="cnf_path_ssh_kh" bind:value={form.path_ssh_known_hosts.value} bind:color={form.path_ssh_known_hosts.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_ssh_known_hosts.required}
                    disabled={isRO('path_ssh_known_hosts')} />
                 {#if isRO('path_ssh_known_hosts')}
                     <Tooltip>{t('config.is_read_only')}</Tooltip>
                 {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.path_ssh_known_hosts')}</Helper>
            </div>
        </div>
    </AccordionItem>
    <AccordionItem defaultClass="{classSpoilerItem} settings-mailing" paddingDefault={classSpoilerPad}>
        <span slot="header">
            <EnvelopeSolid class="inline-block"/> {t('config.mailing')}
        </span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_mail_srv" class={classModalLabel}>{t('config.form.mail_server')}</Label>
                <Input id="cnf_mail_srv" bind:value={form.mail_server.value} bind:color={form.mail_server.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_server.required}
                    disabled={isRO('mail_server')} />
                {#if isRO('mail_server')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.mail_server')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_mail_trans" class={classModalLabel}>{t('config.form.mail_transport')}</Label>
                <Select id="cnf_mail_trans" items={formInfos.choices.mail_transport}
                    bind:value={form.mail_transport.value}
                    disabled={isRO('mail_transport')} />
                {#if isRO('mail_transport')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>

            {#if form.mail_transport.value != 0}
                <div class={classModalInput}>
                    <Label for="cnf_mail_ssl_verify" class={classModalLabel}>{t('config.form.mail_ssl_verify')}</Label>
                    <Toggle id="cnf_mail_ssl_verify" bind:checked={form.mail_ssl_verify.value}
                        disabled={isRO('mail_ssl_verify')} />
                    {#if isRO('mail_ssl_verify')}
                        <Tooltip>{t('config.is_read_only')}</Tooltip>
                    {/if}
                    <Helper class={classModalHelp}>{t('config.form.help.mail_ssl_verify')}</Helper>
                </div>
            {/if}

            <div class={classModalInput}>
                <Label for="cnf_mail_sender" class={classModalLabel}>{t('config.form.mail_sender')}</Label>
                <Input id="cnf_mail_sender" bind:value={form.mail_sender.value} bind:color={form.mail_sender.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_sender.required}
                    disabled={isRO('mail_sender')} />
                {#if isRO('mail_sender')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.mail_sender')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_mail_user" class={classModalLabel}>{t('config.form.mail_user')}</Label>
                <Input id="cnf_mail_user" bind:value={form.mail_user.value} bind:color={form.mail_user.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_user.required}
                    disabled={isRO('mail_user')} />
                {#if isRO('mail_user')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>

            <div class={classModalInput}>
                <Label for="cnf_mail_pwd" class={classModalLabel}>{t('config.form.mail_pass')}</Label>
                <Input id="cnf_mail_pwd" bind:value={form.mail_pass.value} bind:color={form.mail_pass.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_pass.required}
                    type="password" disabled={isRO('mail_pass')}/>
                {#if isRO('mail_pass')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>
        </div>
    </AccordionItem>
    <AccordionItem defaultClass="{classSpoilerItem} settings-internal" paddingDefault={classSpoilerPad}>
        <span slot="header">
            <LayersSolid class="inline-block"/> {t('config.internal')}
        </span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_tz" class={classModalLabel}>{t('config.form.timezone')}</Label>
                <Select id="cnf_tz" items={choicesFromArray(formInfos.choices.timezone)}
                    bind:value={form.timezone.value} disabled={isRO('timezone')} />
                {#if isRO('timezone')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>

            <div class={classModalInput}>
                <Label for="cnf_to_session" class={classModalLabel}>{t('config.form.session_timeout')}</Label>
                <Input id="cnf_to_session" bind:value={form.session_timeout.value} bind:color={form.session_timeout.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required}
                    type="number" disabled={isRO('session_timeout')} />
                {#if isRO('session_timeout')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
            </div>

            <div class={classModalInput}>
                <Label for="cnf_debug" class={classModalLabel}>{t('config.form.debug')}</Label>
                <Toggle id="cnf_debug" bind:checked={form.debug.value} disabled={isRO('debug') || isDeploymentDev()} />
                {#if isRO('debug') || isDeploymentDev()}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{t('config.form.help.debug')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_audit_log" class={classModalLabel}>{t('config.form.audit_log')}</Label>
                <Toggle id="cnf_audit_log" bind:checked={form.audit_log.value} />
                <Helper class={classModalHelp}>{@html t('config.form.help.audit_log')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_logo" class={classModalLabel}>{t('config.form.logo_url')}</Label>
                <Input id="cnf_logo" bind:value={form.logo_url.value} bind:color={form.logo_url.color}
                    on:input={valideInput} on:blur={valideInput} required={form.logo_url.required}
                    disabled={isRO('logo_url')} />
                {#if isRO('cnf_logo')}
                    <Tooltip>{t('config.is_read_only')}</Tooltip>
                {/if}
                <Helper class={classModalHelp}>{@html t('config.form.help.logo_url')}</Helper>
            </div>
        </div>
    </AccordionItem>
</Accordion>

<div class={classModalBtns}>
    <Button id="settings-btn-save" type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
    <Tooltip>{t('btn.save')}</Tooltip>
</div>

{/if}
</div>

<Hr/>

<div>
    <div class="h-20"></div>
    <Heading tag="h3">{t('jobs.form.environment_vars')}</Heading>

    <div class={classModalInputDiv}>
        {#if !settingsRead.env_vars || !formInfos.env_vars}
            <div class={classSpinnerDiv}><Spinner/></div>
        {:else}
            {#each Object.entries(settingsRead.env_vars) as [k, v] (k)}
                <div class={classModalInput}>
                    <Label for="env_var_{k}" class={classModalLabel}>{formInfos.env_vars[k]}</Label>
                    <Input id="env_var_{k}" value={v} disabled={true} />
                </div>
            {/each}
        {/if}
    </div>
</div>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
