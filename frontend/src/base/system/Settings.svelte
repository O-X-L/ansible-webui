<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Accordion, AccordionItem, Label, Input, Toggle, Select, Helper,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { type formInfoType } from '../Types.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import { choicesFromArray } from '../../util/form.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { valideInputBase, inputBaseColor, submitFormBase } from '../../util/form.js';
    import {
        classSpinnerDiv, classModalBtns, classModalLabel, classModalInput, classModalHelp, classModalInputDiv,
    } from '../Style.js';

    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let loaded = $state(false);
    let formInfos: formInfoType = $state({defaults: {}, choices: {}});

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
        logo_url: string
        ara_server: string|null
        global_environment_vars: string|null
        mail_server: string|null
        mail_transport: number
        mail_ssl_verify: boolean
        mail_sender: string|null
        mail_user: string|null
    }
    interface settingsReadType extends settingsBaseType {
        db: string
        db_migrate: boolean|null
        deployment: string
        version: string
        mail_pass_is_set: boolean
    }
    interface settingsWriteType extends settingsBaseType {
        mail_pass: string|null
    }
    interface settingsReadFullType {
        read_only: string[]
        settings: settingsReadType
        env_vars: any
    }
    let settingsRead: settingsReadFullType = $state();
    let form = $state({
        path_run: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_play: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_log: {value: '', color: inputBaseColor, required: true, regex: /^.{1,100}/},
        path_template: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        timezone: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        run_timeout: {value: 60*60, color: inputBaseColor, required: true},
        session_timeout: {value: 60*60*12, color: inputBaseColor, required: true},
        path_ansible_config: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        path_ssh_known_hosts: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        debug: {value: false},
        logo_url: {value: '', color: inputBaseColor, required: true, regex: /^.{1,200}/},
        ara_server: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        global_environment_vars: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        mail_server: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        mail_transport: {value: 0, color: inputBaseColor, required: false, regex: /^.{1,100}/},
        mail_ssl_verify: {value: false},
        mail_sender: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
        mail_user: {value: '', color: inputBaseColor, required: false, regex: /^.{1,100}/},
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    function submitForm() {
        apiSuccessMsg = 'config.action.update';
        apiEdit('put', 'config', null, apiResponseHandler.handleRes);
    }

    function setFormInfos(j: any) {
        formInfos = j;
        for (let [k, v] of Object.entries(formInfos.defaults)) {
            if (form[k]) {
                form[k].value = v;
            }
        }
        loaded = true;
        buildUpdateSettings();
    }

    function valideInput(e: Event) {
        valideInputBase(e, form);
    }

    function loadSettings(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        settingsRead = j;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function buildUpdateSettings() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`config?hash=${apiDataHash}`, loadSettings);
    }

    onMount(() => {
        if (!loaded) {
            apiGet('frontend/form/config', setFormInfos);
        }
    
        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateSettings();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<Accordion>
    <AccordionItem>
        <span slot="header">{t('config.paths')}</span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_path_run" class={classModalLabel}>{t('config.form.path_run')}</Label>
                <Input id="cnf_path_run" bind:value={form.path_run.value} bind:color={form.path_run.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_run.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.path_run')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_play" class={classModalLabel}>{t('config.form.path_play')}</Label>
                <Input id="cnf_path_play" bind:value={form.path_play.value} bind:color={form.path_play.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_play.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.path_play')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_log" class={classModalLabel}>{t('config.form.path_log')}</Label>
                <Input id="cnf_path_log" bind:value={form.path_log.value} bind:color={form.path_log.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required} />
                <Helper class={classModalHelp}>{t('config.form.help.path_log')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_tmpl" class={classModalLabel}>{t('config.form.path_template')}</Label>
                <Input id="cnf_path_tmpl" bind:value={form.path_template.value} bind:color={form.path_template.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_template.required} />
                <Helper class={classModalHelp}>{t('config.form.help.path_template')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_ans_cnf" class={classModalLabel}>{t('config.form.path_ansible_config')}</Label>
                <Input id="cnf_path_ans_cnf" bind:value={form.path_ansible_config.value} bind:color={form.path_ansible_config.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_ansible_config.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.path_ansible_config')}</Helper>
            </div>
    
            <div class={classModalInput}>
                <Label for="cnf_path_ssh_kh" class={classModalLabel}>{t('config.form.path_ssh_known_hosts')}</Label>
                <Input id="cnf_path_ssh_kh" bind:value={form.path_ssh_known_hosts.value} bind:color={form.path_ssh_known_hosts.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_ssh_known_hosts.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.path_ssh_known_hosts')}</Helper>
            </div>
        </div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('config.execution')}</span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_ara" class={classModalLabel}>{t('config.form.ara_server')}</Label>
                <Input id="cnf_ara" bind:value={form.ara_server.value} bind:color={form.ara_server.color}
                    on:input={valideInput} on:blur={valideInput} required={form.ara_server.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.ara_server')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_glob_env_vars" class={classModalLabel}>{t('config.form.global_environment_vars')}</Label>
                <Input id="cnf_glob_env_vars" bind:value={form.global_environment_vars.value}
                    bind:color={form.global_environment_vars.color} on:input={valideInput} on:blur={valideInput}
                    required={form.global_environment_vars.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.global_environment_vars')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_to_run" class={classModalLabel}>{t('config.form.run_timeout')}</Label>
                <Input id="cnf_to_run" bind:value={form.run_timeout.value} bind:color={form.run_timeout.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required} type="number" />
            </div>
        </div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('config.internal')}</span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_tz" class={classModalLabel}>{t('config.form.timezone')}</Label>
                <Select id="cnf_tz" items={choicesFromArray(formInfos.choices.timezone)}
                    bind:value={form.timezone.value} />
            </div>

            <div class={classModalInput}>
                <Label for="cnf_to_session" class={classModalLabel}>{t('config.form.session_timeout')}</Label>
                <Input id="cnf_to_session" bind:value={form.session_timeout.value} bind:color={form.session_timeout.color}
                    on:input={valideInput} on:blur={valideInput} required={form.path_log.required} type="number" />
            </div>

            <div class={classModalInput}>
                <Label for="cnf_debug" class={classModalLabel}>{t('config.form.debug')}</Label>
                <Toggle id="cnf_debug" bind:checked={form.debug.value} />
                <Helper class={classModalHelp}>{t('config.form.help.debug')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_logo" class={classModalLabel}>{t('config.form.logo_url')}</Label>
                <Input id="cnf_logo" bind:value={form.logo_url.value} bind:color={form.logo_url.color}
                    on:input={valideInput} on:blur={valideInput} required={form.logo_url.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.logo_url')}</Helper>
            </div>
        </div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('config.mailing')}</span>

        <div class={classModalInputDiv}>
            <div class={classModalInput}>
                <Label for="cnf_mail_srv" class={classModalLabel}>{t('config.form.mail_server')}</Label>
                <Input id="cnf_mail_srv" bind:value={form.mail_server.value} bind:color={form.mail_server.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_server.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.mail_server')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_mail_trans" class={classModalLabel}>{t('config.form.mail_transport')}</Label>
                <Select id="cnf_mail_trans" items={formInfos.choices.mail_transport}
                    bind:value={form.mail_transport.value} />
            </div>

            {#if form.mail_transport.value != 0}
                <div class={classModalInput}>
                    <Label for="cnf_mail_ssl_verify" class={classModalLabel}>{t('config.form.mail_ssl_verify')}</Label>
                    <Toggle id="cnf_mail_ssl_verify" bind:checked={form.mail_ssl_verify.value} />
                    <Helper class={classModalHelp}>{t('config.form.help.mail_ssl_verify')}</Helper>
                </div>
            {/if}

            <div class={classModalInput}>
                <Label for="cnf_mail_sender" class={classModalLabel}>{t('config.form.mail_sender')}</Label>
                <Input id="cnf_mail_sender" bind:value={form.mail_sender.value} bind:color={form.mail_sender.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_sender.required} />
                <Helper class={classModalHelp}>{@html t('config.form.help.mail_sender')}</Helper>
            </div>

            <div class={classModalInput}>
                <Label for="cnf_mail_user" class={classModalLabel}>{t('config.form.mail_user')}</Label>
                <Input id="cnf_mail_user" bind:value={form.mail_user.value} bind:color={form.mail_user.color}
                    on:input={valideInput} on:blur={valideInput} required={form.mail_user.required} />
            </div>
        </div>
    </AccordionItem>
</Accordion>

<div class={classModalBtns}>
    <Button type="button" on:click={submitForm}><FloppyDiskSolid/></Button>
    <Tooltip>{t('btn.save')}</Tooltip>
</div>
