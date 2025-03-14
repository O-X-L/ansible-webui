<script lang="ts">
    import {
        Heading, Spinner, Button, Modal, Input, Label, Helper,
        // Dropdown, DropdownItem,
    } from 'flowbite-svelte';
    // import { } from 'flowbite-svelte-icons'

    import { share } from '../State.js';
    import { tq } from '../../util/translate.ts';
    import {
        classModalBackdrop, classModalLabel, classModalHelp, classModalBtns, classModalForm,
    } from '../Style.js';
    import { apiForm, getCSRFFormToken } from '../../util/api.ts';

    let addModal = false;

    function t(code: string) {
      return tq($share, code);
    }

    function handleAddJobResponse(j: any) {
        console.log("RES", j);
        // if not error
        addModal = false;
    }

    function addJob(e: SubmitEvent) {
        console.log(e);
        apiForm(e, handleAddJobResponse);
    }
</script>

<div class="flex justify-between">
    <div></div>
    <div>
        <Button on:click={() => (addModal = true)}>{t('btn.add')}</Button>
    </div>    
</div>

<div class="text-center mt-20">
    <Spinner/>
</div>

<Modal bind:open={addModal} size="xs" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{t('jobs.new')}</Heading>
    <form on:submit={addJob} action="/api/job" method="post" class={classModalForm}>
        <Label for="job_name" class={classModalLabel}>{t('jobs.form.name')}</Label>
        <Input id="job_name" name="name"  />

        <Label for="job_repo" class={classModalLabel}>{t('jobs.form.repository')}</Label>
        <Input id="job_repo" name="repository"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.repository')}</Helper>

        <Label for="job_pb" class={classModalLabel}>{t('jobs.form.playbook_file')}</Label>
        <Input id="job_pb" name="playbook_file"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.playbook_file')}</Helper>

        <Label for="job_inv" class={classModalLabel}>{t('jobs.form.inventory_file')}</Label>
        <Input id="job_inv" name="inventory_file"  />
        <Helper class={classModalHelp}>{@html t('jobs.form.help.inventory_file')}</Helper>

        <Label for="job_cmt" class={classModalLabel}>{t('jobs.form.comment')}</Label>
        <Input id="job_cmt" name="comment"  />

        <Label for="job_cron" class={classModalLabel}>{t('jobs.form.schedule')}</Label>
        <Input id="job_cron" name="schedule"  />
        <Helper class={classModalHelp}>{@html t('jobs.form.help.schedule')}</Helper>

        <Label for="job_cron_en" class={classModalLabel}>{t('jobs.form.enabled')}</Label>
        <Input id="job_cron_en" name="enabled"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.enabled')}</Helper>

        <Label for="job_limit" class={classModalLabel}>{t('jobs.form.limit')}</Label>
        <Input id="job_limit" name="limit"  />
        <Helper class={classModalHelp}>{@html t('jobs.form.help.limit')}</Helper>

        <Label for="job_tags" class={classModalLabel}>{t('jobs.form.tags')}</Label>
        <Input id="job_tags" name="tags"  />
        <Helper class={classModalHelp}>{@html t('jobs.form.help.tags')}</Helper>

        <Label for="job_tags_skip" class={classModalLabel}>{t('jobs.form.tags_skip')}</Label>
        <Input id="job_tags_skip" name="tags_skip"  />

        <Label for="job_diff" class={classModalLabel}>{t('jobs.form.mode_diff')}</Label>
        <Input id="job_diff" name="mode_diff"  />

        <Label for="job_chk" class={classModalLabel}>{t('jobs.form.mode_check')}</Label>
        <Input id="job_chk" name="mode_check"  />
        <Helper class={classModalHelp}>{@html t('jobs.form.help.mode_check')}</Helper>

        <Label for="job_env" class={classModalLabel}>{t('jobs.form.environment_vars')}</Label>
        <Input id="job_env" name="environment_vars"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.environment_vars')}</Helper>

        <Label for="job_args" class={classModalLabel}>{t('jobs.form.cmd_args')}</Label>
        <Input id="job_args" name="cmd_args"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.cmd_args')}</Helper>

        <Label for="job_creds" class={classModalLabel}>{t('jobs.form.credentials_needed')}</Label>
        <Input id="job_creds" name="credentials_needed"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_needed')}</Helper>

        <Label for="job_creds_dflt" class={classModalLabel}>{t('jobs.form.credentials_default')}</Label>
        <Input id="job_creds_dflt" name="credentials_default"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_default')}</Helper>

        <Label for="job_creds_cat" class={classModalLabel}>{t('jobs.form.credentials_category')}</Label>
        <Input id="job_creds_cat" name="credentials_category"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.credentials_category')}</Helper>

        <Label for="job_prompts_req" class={classModalLabel}>{t('jobs.form.execution_prompts_required')}</Label>
        <Input id="job_prompts_req" name="execution_prompts_required"  />
        <Helper class={classModalHelp}>{t('jobs.form.help.execution_prompts_required')}</Helper>

        <Label for="job_prompts_opt" class={classModalLabel}>{t('jobs.form.execution_prompts_optional')}</Label>
        <Input id="job_prompts_opt" name="execution_prompts_optional"  />

        <Label for="job_verb" class={classModalLabel}>{t('jobs.form.verbosity')}</Label>
        <Input id="job_verb" name="verbosity"  />

        {@html getCSRFFormToken()}
        <div class={classModalBtns}>
            <Button type="submit">{t('btn.save')}</Button>
            <Button on:click={() => (addModal = false)} class="inline-block">{t('btn.discard')}</Button>
        </div>
    </form>
</Modal>
