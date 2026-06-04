<script lang="ts">
    import {
        Popover, Radio, Alert
    } from 'flowbite-svelte';

    import { share } from '../../Share.js';
    import { isSet } from '../../../util/main.js';
    import type { jobType } from '../Types.js';
    import { tq } from '../../../util/translate.js';
    import { EXEC_STATUS_FAILED } from '../../Config.js';
    import {
        classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div,
    } from '../../Style.js';

    let {
        job = $bindable(null),
    } : {
        job: jobType,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }
</script>

{#if job}
<Popover triggeredBy="#job-name-{job.id}" class={classPopover} placement="bottom-start">
    <div class="p-3 space-y-2">
        <h3 class={classPopoverTitle}>{t('jobs.info')}</h3>
    </div>
    <table>
        <tbody>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.id')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {job.id}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.comment')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {job.comment ? job.comment : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.inventory_file')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {job.inventory_file ? job.inventory_file : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.playbook_file')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {job.playbook_file}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.limit')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {job.limit ? job.limit : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.mode_diff')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={job.mode_diff}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.mode_check')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={job.mode_check}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('jobs.form.credentials_needed')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={job.credentials_needed}></Radio>
                    </button>
                </td>
            </tr>
        </tbody>
    </table>
</Popover>
<Popover triggeredBy="#job-schedule-{job.id}" class={classPopover} placement="bottom-start">
    <div class="p-3 space-y-2">
        <h3 class={classPopoverTitle}>{t('jobs.info.execution')}</h3>
        <table>
            <tbody>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('jobs.form.enabled')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio checked={job.enabled && isSet(job.schedule)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('jobs.form.cron')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {job.schedule ? job.schedule : '-'}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('jobs.info.next_run')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {job.next_run ? job.next_run : '-'}
                    </td>
                </tr>
                {#if job.executions.length}
                    <tr>
                        <td class="{classPopoverColumn1} pt-3">
                            {t('jobs.info.last_run')}:
                        </td>
                        <td class="{classPopoverColumn2Text} pt-3">
                            {job.executions[0].time_start}
                        </td>
                    </tr>
                    <tr>
                        <td class={classPopoverColumn1}>
                            {t('common.status')}:
                        </td>
                        <td class="{classPopoverColumn2Text} {job.executions[0].status == EXEC_STATUS_FAILED ? 'text-red-600' : 'text-green-600'}">
                            {job.executions[0].status_name}
                        </td>
                    </tr>
                    <tr>
                        <td class={classPopoverColumn1}>
                            {t('jobs.info.duration')}:
                        </td>
                        <td class={classPopoverColumn2Text}>
                            {job.executions[0].time_duration}
                        </td>
                    </tr>
                    <tr>
                        <td class={classPopoverColumn1}>
                            {t('jobs.info.failed')}:
                        </td>
                        <td class={classPopoverColumn2Div}>
                            <button class="cursor-default">
                                <Radio class="inline-block" checked={job.executions[0].failed}></Radio>
                            </button>
                        </td>
                    </tr>
                    {#if job.executions[0].failed && job.executions[0].error_s?.length && job.executions[0].error_s.length > 0}
                        <tr>
                            <td class={classPopoverColumn1}>
                                {t('common.error')}:
                            </td>
                            <td class={classPopoverColumn2Div}>
                                <Alert color="red" border>{job.executions[0].error_s}</Alert>
                            </td>
                        </tr>
                    {/if}
                {/if}
            </tbody>
        </table>
    </div>
</Popover>
{/if}
