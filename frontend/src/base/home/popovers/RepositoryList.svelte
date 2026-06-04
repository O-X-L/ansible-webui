<script lang="ts">
    import {
        Popover, Radio
    } from 'flowbite-svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { isSet } from '../../../util/main.js';
    import type { repoType } from '../Types.js';
    import {
        classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div,
    } from '../../Style.js';

    let {
        repo = $bindable(null),
        repoKind = '',
    } : {
        repo: repoType,
        repoKind: string,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }
</script>

{#if repo}
<Popover triggeredBy="#repos-name-{repo.id}" class={classPopover} placement="bottom-start">
    <div class="p-3 space-y-2">
        <h3 class={classPopoverTitle}>{t('repos.info')}</h3>
    </div>
    <table>
        <tbody>
            <tr>
                <td class={classPopoverColumn1}>
                    {t('common.id')}:
                </td>
                <td class={classPopoverColumn2Text}>
                    {repo.id}
                </td>
            </tr>
            {#if repoKind == 'static'}
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('common.path')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.static_path}
                    </td>
                </tr>
            {:else}
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_origin')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.git_origin}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_branch')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.git_branch}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_credentials')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_credentials)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_limit_depth')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.git_limit_depth ? repo.git_limit_depth : '-'}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_playbook_base')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.git_playbook_base ? repo.git_playbook_base : '-'}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_lfs')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={repo.git_lfs}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_isolate')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={repo.git_isolate}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('system.ssh_hostkey')}:
                    </td>
                    <td class={classPopoverColumn2Text}>
                        {repo.ssh_hostkey_file ? repo.ssh_hostkey_file : '-'}
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_hook_pre')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_hook_pre)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_hook_post')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_hook_post)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_hook_cleanup')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_hook_cleanup)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_override_initialize')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_override_initialize)}></Radio>
                        </button>
                    </td>
                </tr>
                <tr>
                    <td class={classPopoverColumn1}>
                        {t('repos.form.git_override_update')}:
                    </td>
                    <td class={classPopoverColumn2Div}>
                        <button class="cursor-default">
                            <Radio class="inline-block" checked={isSet(repo.git_override_update)}></Radio>
                        </button>
                    </td>
                </tr>
            {/if}
        </tbody>
    </table>
</Popover>
{/if}
