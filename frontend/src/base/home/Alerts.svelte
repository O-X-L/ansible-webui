<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, UserSolid, UsersGroupSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid, FileCodeSolid, DribbbleSolid, PlaySolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Popover, Radio,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import AlertForm from './forms/Alert.svelte';
    import type { entryActionState } from '../Types.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import AlertPluginForm from './forms/AlertPlugin.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classPopoverColumn1, classListHeader, classListContent,
        classPopover, classPopoverColumn2Div, classPopoverColumn2Text, classPopoverTitle, classFooterSpacing,
        classSpoilerItem, classSpoilerPad,
    } from '../Style.js';
 
    const alertKinds = ['global', 'group', 'user'];
    const alertKindsAll = ['plugins'];
    alertKindsAll.push(...alertKinds);

    let { open = $bindable(false) } = $props();

    interface entryActionsType {
        [category: string]: {
            [id: number]: entryActionState;
        };
    }

    let apiResponseHandler: APIResponseHandler = $state();
    let addGlobalModal = $state(false);
    let addGroupModal = $state(false);
    let addUserModal = $state(false);
    let addPluginModal = $state(false);
    let addGlobalModalId = $state(Date.now());
    let addGroupModalId = $state(Date.now());
    let addUserModalId = $state(Date.now());
    let addPluginModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let entryActions: entryActionsType = $state({'global': {}, 'group': {}, 'user': {}, 'plugins': {}});
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let searchedAt = $state(0);

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

    interface alertBaseType {
        id: number,
        name: string,
        alert_type: number,
        plugin: number,
        jobs_all: boolean,
        jobs: number[],
        condition: number,
    }
    interface alertGlobalType extends alertBaseType {}
    interface alertGroupType extends alertBaseType {
        group: number,
    }
    interface alertUserType extends alertBaseType {
        user: number,
    }
    interface alertPluginType {
        id: number,
        name: string,
        executable: string,
    }
    interface alertsFullType {
        global: alertGlobalType[],
        group: alertGroupType[],
        user: alertUserType[],
        plugins: alertPluginType[],
    }

    let entryLists: alertsFullType = $state({'global': [], 'group': [], 'user': [], 'plugins': []});

    function t(code: string) : string {
      return tq($share, code);
    }

    function loadAlertList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        for (let kind of alertKindsAll) {
            if (!entryActions[kind]) {
                entryActions[kind] = {};
            }
            for (let c of j[kind]) {
                if (!entryActions[kind][c.id]) {
                    entryActions[kind][c.id] = {edit: false, clone: false};
                }
            }
        }
        entryLists = j;
        apiDataHash = h;
        updatedAt = Date.now();
    }

    function searchAlertFilter(item: alertGlobalType|alertGroupType|alertUserType, searchTerm: string) : boolean {
        searchedAt = Date.now();
        let s = searchTerm.toLowerCase();
        return (
            item.name.toLowerCase().includes(s) ||
            ALERT_TYPE_CHOICES[item.alert_type].toLowerCase().includes(s) ||
            ALERT_CONDITION_CHOICES[item.condition].toLowerCase().includes(s)
        )
    }

    function searchPluginFilter(item: alertPluginType, searchTerm: string) : boolean {
        searchedAt = Date.now();
        let s = searchTerm.toLowerCase();
        return (
            item.name.toLowerCase().includes(s) ||
            item.executable.toLowerCase().includes(s)
        )
    }

    function getPluginNameByID(pluginID: number) : string {
        for (let p of entryLists.plugins) {
            if (p.id == pluginID) {
                return p.name;
            }
        }
        return '?';
    }

    function deleteAlert(alertID: number, kind: string) {
        if (!alertID) {
            return;
        }
        apiSuccessMsg = 'alerts.action.delete';
        apiEdit('delete', `alert/${kind}/${alertID}`, null, apiResponseHandler.handleRes);
    }

    function testAlert(alertID: number, kind: string) {
        if (!alertID) {
            return;
        }
        apiSuccessMsg = 'alerts.action.test';
        apiEdit('post', `alert/${kind}/${alertID}`, null, apiResponseHandler.handleRes);
    }

    function buildUpdateAlertList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (addGlobalModal || addGroupModal || addUserModal || addPluginModal || isUserEditing()) {
            // user currently adding/editing entry
            return;
        }
        apiGet(`alert?hash=${apiDataHash}`, loadAlertList);
    }

    function isUserEditing(): boolean {
        let any_open = Object.values(entryActions.global).some(state => state.edit);
        if (!any_open) {
            any_open = Object.values(entryActions.user).some(state => state.edit)
        }
        if (!any_open) {
            any_open = Object.values(entryActions.group).some(state => state.edit)
        }
        if (!any_open) {
            any_open = Object.values(entryActions.plugin).some(state => state.edit)
        }
        return any_open;
    }

    onMount(() => {
        buildUpdateAlertList();

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateAlertList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg}
    bind:successMsg={apiSuccessMsg} bind:showSuccess={apiSuccess} />

<div>
    <Accordion>
        {#each alertKinds as alertKind (alertKind) }
            <AccordionItem defaultClass="{classSpoilerItem} alerts-kind-{alertKind}" paddingDefault={classSpoilerPad}>
                <span slot="header">
                    {#if alertKind == 'global'}
                        <DribbbleSolid class="inline-block"/>
                    {:else if alertKind == 'group'}
                        <UsersGroupSolid class="inline-block"/>
                    {:else}
                        <UserSolid class="inline-block"/>
                    {/if}
                    {t(`alerts.${alertKind}`)}
                </span>
                <div>
                    <Table striped={true} bind:items={entryLists[alertKind]} hoverable={true} shadow
                        placeholder={t('common.search')} filter={(item, searchTerm) => {return searchAlertFilter(item, searchTerm)}}>
                    <TableHead theadClass={classListHeader}>
                        <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                            {t('common.name')}
                        </TableHeadCell>
                        <TableHeadCell class="max-sm:hidden" sort={(a, b) => a.condition.localeCompare(b.condition)}>
                            {t('alerts.form.condition')}
                        </TableHeadCell>
                        <TableHeadCell class="max-lg:hidden"
                            sort={(a, b) => ALERT_TYPE_CHOICES[a.alert_type].localeCompare(ALERT_TYPE_CHOICES[b.alert_type])}>
                            {t('common.kind')}
                        </TableHeadCell>
                        <TableHeadCell>{t('common.actions')}</TableHeadCell>
                    </TableHead>
                    {#key updatedAt}
                    <TableBody tableBodyClass="divide-y">
                        <TableBodyRow slot="row" let:item>
                            <TableBodyCell tdClass={classListContent}>
                                {item.name}
                                {#key item.id}
                                    <button id="alerts-name-{item.id}" class="ml-1">
                                        <InfoCircleSolid size="sm"/>
                                        <span class="sr-only">{t('alerts.info')}</span>
                                    </button>
                                {/key}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                                {ALERT_CONDITION_CHOICES[item.condition]}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} max-lg:hidden">
                                {ALERT_TYPE_CHOICES[item.alert_type]}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} action-btns">
                                <div class="mb-2">
                                    <Button size="xs" on:click={() => (testAlert(item.id, alertKind))} disabled>
                                        <PlaySolid/>
                                    </Button>
                                    <Tooltip>{t('btn.execute')}</Tooltip>
                                </div>
                                <div>
                                    <Button size="xs" on:click={() => {entryActions[alertKind][item.id].edit = true}}><EditSolid/></Button>
                                    <Tooltip>{t('btn.edit')}</Tooltip>
                
                                    <Button size="xs" on:click={() => {entryActions[alertKind][item.id].clone = true}}><FileCloneSolid/></Button>
                                    <Tooltip>{t('btn.clone')}</Tooltip>
                
                                    <Button size="xs" on:click={() => {deleteAlert(item.id, alertKind)}}><TrashBinSolid/></Button>
                                    <Tooltip>{t('btn.delete')}</Tooltip>

                                    <div class="w-0 h-0 inline">
                                        {#key item.id}
                                            <AlertForm bind:open={entryActions[alertKind][item.id].edit} action='edit' kind={alertKind}
                                                existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                                            <AlertForm bind:open={entryActions[alertKind][item.id].clone} action='clone' kind={alertKind}
                                                existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                        {/key}
                                    </div>
                                </div>
                                </TableBodyCell>
                        </TableBodyRow>
                    </TableBody>
                    {/key}
                    </Table>
                    {#if !entryLists[alertKind].length}
                        <div class={classSpinnerDiv}><Spinner/></div>
                    {/if}
                </div>
                <div>
                    {#each entryLists[alertKind] as alert (alert.id)}
                        {#key searchedAt}
                        <div id="alerts-infos-{alert.id}">
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
                                                    {getPluginNameByID(alert.plugin)}
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
                        </div>
                        {/key}
                    {/each}
                </div>
            </AccordionItem>
        {/each}
        <AccordionItem defaultClass="{classSpoilerItem} alerts-kind-plugin" paddingDefault={classSpoilerPad}>
            <span slot="header">
                <FileCodeSolid class="inline-block"/> {t('alerts.plugin')}
            </span>
            <div>
                <Table striped={true} bind:items={entryLists.plugins} hoverable={true} shadow
                    placeholder={t('common.search')} filter={(item, searchTerm) => {return searchPluginFilter(item, searchTerm)}}>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                        {t('common.name')}
                    </TableHeadCell>
                    <TableHeadCell class="max-sm:hidden" sort={(a, b) => a.executable.localeCompare(b.executable)}>
                        {t('alerts.form.plugin.executable')}
                    </TableHeadCell>
                    <TableHeadCell>{t('common.actions')}</TableHeadCell>
                </TableHead>
                {#key updatedAt}
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow slot="row" let:item>
                        <TableBodyCell tdClass={classListContent}>
                            {item.name}
                        </TableBodyCell>
                        <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                            {item.executable}
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>
                            <div>
                                <Button size="xs" on:click={() => (testAlert(item.id, 'plugin'))} disabled>
                                    <PlaySolid/>
                                </Button>
                                <Tooltip>{t('btn.execute')}</Tooltip>
                            </div>
                            <div>
                                <Button size="xs" on:click={() => {entryActions.plugins[item.id].edit = true}}><EditSolid/></Button>
                                <Tooltip>{t('btn.edit')}</Tooltip>
            
                                <Button size="xs" on:click={() => {entryActions.plugins[item.id].clone = true}}><FileCloneSolid/></Button>
                                <Tooltip>{t('btn.clone')}</Tooltip>
            
                                <Button size="xs" on:click={() => {deleteAlert(item.id, 'plugin')}}><TrashBinSolid/></Button>
                                <Tooltip>{t('btn.delete')}</Tooltip>
                                <div class="w-0 h-0 inline">
                                    {#key item.id}
                                        <AlertPluginForm bind:open={entryActions.plugins[item.id].edit} action='edit'
                                            existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                                        <AlertPluginForm bind:open={entryActions.plugins[item.id].clone} action='clone'
                                            existingID={item.id} bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                    {/key}
                                </div>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                </TableBody>
                {/key}
                </Table>
                {#if !entryLists.plugins.length}
                    <div class={classSpinnerDiv}><Spinner/></div>
                {/if}
            </div>
        </AccordionItem>
    </Accordion>    
</div>
    
<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button id="alerts-btn-add-dd">{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem id="alerts-btn-add-global" on:click={() => {addGlobalModalId = Date.now(); addGlobalModal = true}}>
                <DribbbleSolid class="inline-block"/> {t('alerts.global')}
            </DropdownItem>
            <DropdownItem id="alerts-btn-add-group" on:click={() => {addGroupModalId = Date.now(); addGroupModal = true}}>
                <UsersGroupSolid class="inline-block"/> {t('alerts.group')}
            </DropdownItem>
            <DropdownItem id="alerts-btn-add-user" on:click={() => {addUserModalId = Date.now(); addUserModal = true}}>
                <UserSolid class="inline-block"/> {t('alerts.user')}
            </DropdownItem>
            <DropdownItem id="alerts-btn-add-plugin" on:click={() => {addPluginModalId = Date.now(); addPluginModal = true}}>
                <FileCodeSolid class="inline-block"/> {t('alerts.plugin')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>

{#key addGlobalModalId}
    <AlertForm bind:open={addGlobalModal} action='add' kind='global'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key addGroupModalId}
    <AlertForm bind:open={addGroupModal} action='add' kind='group'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key addUserModalId}
    <AlertForm bind:open={addUserModal} action='add' kind='user'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key addPluginModalId}
    <AlertPluginForm bind:open={addPluginModal} action='add'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
