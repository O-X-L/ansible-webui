<script lang="ts">
    import {
        Popover, Radio
    } from 'flowbite-svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import type { credentialsUserType, credentialsSharedType } from '../Types.js';
    import {
        classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div,
    } from '../../Style.js';

    let {
        creds = $bindable(null),
        credsKind = '',
    } : {
        creds: credentialsUserType|credentialsSharedType,
        credsKind: string,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }
</script>

{#if creds}
<Popover triggeredBy="#creds-name-{credsKind}-{creds.id}" class={classPopover} placement="bottom-start">
    <div class="p-3 space-y-2">
        <h3 class={classPopoverTitle}>{t('creds.info')}</h3>
    </div>
    <table>
        <tbody>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.id')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {creds.id}
                </td>
            </tr>
            {#if credsKind == 'user'}
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('creds.form.category')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {creds.category ? creds.category : '-'}
                    </td>
                </tr>
            {/if}
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.connect_user')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {creds.connect_user ? creds.connect_user : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.connect_pwd')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={creds.connect_pass_is_set}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.ssh_key')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={creds.ssh_key_is_set}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.become_user')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {creds.become_user ? creds.become_user : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.become_pwd')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={creds.become_pass_is_set}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.vault_pwd')}:
                </td>
                <td class={classPopoverColumn2Div}>
                    <button class="cursor-default">
                        <Radio class="inline-block" checked={creds.vault_pass_is_set}></Radio>
                    </button>
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.vault_file')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {creds.vault_file ? creds.vault_file : '-'}
                </td>
            </tr>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('creds.form.vault_id')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {creds.vault_id ? creds.vault_id : '-'}
                </td>
            </tr>
        </tbody>
    </table>
</Popover>
{/if}