<script lang="ts">
    import {
        Popover, Radio
    } from 'flowbite-svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import type { alertGlobalType, alertGroupType, alertUserType } from '../Types.js';
    import {
        classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div,
    } from '../../Style.js';

    let {
        alert = $bindable(null),
        pluginName = '',
    } : {
        alert: alertGlobalType|alertGroupType|alertUserType,
        pluginName: string,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }

    // todo: de-duplicate (list-view)
    const ALERT_TYPE_PLUGIN: number = 1;
    const ALERT_TYPE_CHOICES: Record<number, string> = {
        0: t('alerts.type.email'),
        ALERT_TYPE_PLUGIN: t('alerts.plugin'),
    }
    const ALERT_CONDITION_CHOICES: Record<number, string> = {
        0: t('alerts.condition.failure'),
        1: t('alerts.condition.success'),
        2: t('alerts.condition.always'),
    }
</script>

{#if alert}
<Popover triggeredBy="#alerts-name-{alert.id}" class={classPopover} placement="bottom-start">
    <div class="p-3 space-y-2">
        <h3 class={classPopoverTitle}>{t('alerts.info')}</h3>
    </div>
    <table>
        <tbody>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.id')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {alert.id}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.name')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {alert.name}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.kind')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {ALERT_TYPE_CHOICES[alert.alert_type]}
                </td>
            </tr>
            {#if alert.alert_type == ALERT_TYPE_PLUGIN}
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('alerts.plugin')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {pluginName}
                    </td>
                </tr>
            {/if}
            <tr>
                <td class={classPopoverColumn1}>
                    {t('alerts.form.condition')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {ALERT_CONDITION_CHOICES[alert.condition]}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('alerts.form.jobs_all')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={alert.jobs_all}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('home.jobs')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    <!-- todo: get job names from ids.. -->
                    {alert.jobs ? alert.jobs : '-'}
                </td>
            </tr>
        </tbody>
    </table>
</Popover>
{/if}
