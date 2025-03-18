<script lang="ts">
    import { onMount } from 'svelte';

    import {
        InfoCircleSolid, UserSolid, UsersGroupSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Popover, Radio,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import CredentialsForm from './forms/Credentials.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classPopoverColumn1, classListHeader, classListContent,
        classPopover, classPopoverColumn2Div, classPopoverColumn2Text, classPopoverTitle,
    } from '../Style.js';
 
    const credentialsKind = ['user', 'shared'];

    let apiResponseHandler: APIResponseHandler = $state();
    let addUserModal = $state(false);
    let addSharedModal = $state(false);
    let addUserModalId = $state(Date.now());
    let addSharedModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiDataHash = $state('');
    let entryActions = $state({'shared': {}, 'user': {}});

    interface credentialsSharedInfos {
        id: number,
        name: string,
        connect_user: string,
        become_user: string,
        vault_file: string,
        vault_id: string,
        vault_pass_is_set: boolean,
        become_pass_is_set: boolean,
        connect_pass_is_set: boolean,
        ssh_key_is_set: boolean,
    }
    interface credentialsUserInfos extends credentialsSharedInfos {
        category: string,
    }
    interface credentialsFullType {
        shared: credentialsSharedInfos[],
        user: credentialsUserInfos[],
    }

    let entryList: credentialsFullType = $state({'shared': [], 'user': []});

    function t(code: string) {
      return tq($share, code);
    }

    function loadCredentialsList(j: any, h: string) {
        if (!j || h == apiDataHash) {
            return;
        }
        for (let kind of credentialsKind) {
            if (!entryActions[kind]) {
                entryActions[kind] = {};
            }
            for (let c of j[kind]) {
                if (!entryActions[kind][c.id]) {
                    entryActions[kind][c.id] = {edit: false, clone: false};
                }
            }
        }
        entryList = j;
        apiDataHash = h;
    }

    function deleteCredentials(credentialsID: number, shared: boolean) {
        if (!credentialsID) {
            return;
        }
        apiSuccessMsg = 'creds.action.delete';
        apiEdit('delete', `credentials/${credentialsID}?shared=${shared}`, null, apiResponseHandler.handleRes);
    }

    function buildUpdateJobList() {
        if (typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`credentials?hash=${apiDataHash}`, loadCredentialsList);
    }

    // todo: refresh data over websockets
    setInterval(() => {
        buildUpdateJobList();
    }, $share.updateInterval)

    onMount(() => {
        buildUpdateJobList();
    })
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:errorMsg={apiErrorMsg} bind:successMsg={apiSuccessMsg} />

<div>
    <Accordion>
        {#each credentialsKind as credsKind (credsKind) }
            <AccordionItem>
                <span slot="header">{t(`creds.${credsKind}`)}</span>
        
                <div>
                    <Table striped={true}>
                    <TableHead theadClass={classListHeader}>
                        <TableHeadCell>{t('common.name')}</TableHeadCell>
                        <TableHeadCell>{t('creds.form.accounts')}</TableHeadCell>
                        <TableHeadCell class="max-lg:hidden">{t('creds.form.vault')}</TableHeadCell>
                        <TableHeadCell class="max-lg:hidden">{t('creds.form.secrets')}</TableHeadCell>
                        <TableHeadCell>{t('common.actions')}</TableHeadCell>
                    </TableHead>
                    <TableBody tableBodyClass="divide-y">
                        {#each entryList[credsKind] as creds (credsKind + creds.id)}
                            <TableBodyRow>
                                <TableBodyCell tdClass={classListContent}>
                                    {creds.name}
                                    <button id="creds-name-{credsKind}-{creds.id}" class="ml-1">
                                        <InfoCircleSolid size="sm"/>
                                        <span class="sr-only">{t('creds.info')}</span>
                                    </button>
                                </TableBodyCell>
                                <TableBodyCell tdClass={classListContent}>
                                    {#if creds.connect_user}
                                        <div>
                                            <b>{t('creds.form.connect_user')}</b>: {creds.connect_user}
                                        </div>
                                    {/if}
                                    {#if creds.become_user}
                                        <div>
                                            <b>{t('creds.form.become_user')}</b>: {creds.become_user}
                                        </div>
                                    {/if}
                                    {#if !creds.connect_user && !creds.become_user}
                                        -
                                    {/if}
                                </TableBodyCell>
                                <TableBodyCell class="{classListContent} max-lg:hidden">
                                    {#if creds.vault_pass_is_set}
                                        <div>
                                            <b>{t('creds.form.vault_pwd')}</b>
                                        </div>
                                    {/if}
                                    {#if creds.vault_file}
                                        <div>
                                            <b>{t('creds.form.vault_file')}</b>
                                        </div>
                                    {/if}
                                    {#if creds.vault_id}
                                        <div>
                                            <b>{t('creds.form.vault_id')}</b>: {creds.vault_id}
                                        </div>
                                    {/if}
                                    {#if !creds.vault_pass_is_set && !creds.vault_file && !creds.vault_id}
                                        -
                                    {/if}
                                </TableBodyCell>
                                <TableBodyCell class="{classListContent} font-bold max-lg:hidden">
                                    {#if creds.ssh_key_is_set}
                                        <div>
                                            {t('creds.form.ssh_key')}
                                        </div>
                                    {/if}
                                    {#if creds.connect_pass_is_set}
                                        <div>
                                            {t('creds.form.connect_pwd')}
                                        </div>
                                    {/if}
                                    {#if creds.become_pass_is_set}
                                        <div>
                                            {t('creds.form.become_pwd')}
                                        </div>
                                    {/if}
                                    {#if !creds.ssh_key_is_set && !creds.connect_pass_is_set && !creds.become_pass_is_set}
                                        -
                                    {/if}
                                </TableBodyCell>
                                <TableBodyCell tdClass={classListContent}>
                                    <CredentialsForm bind:open={entryActions[credsKind][creds.id].edit} action='edit'
                                    existingID={creds.id} shared={credsKind == 'shared'} />
                                    <Button size="xs" on:click={() => {entryActions[credsKind][creds.id].edit = true}}><EditSolid/></Button>
                                    <Tooltip>{t('btn.edit')}</Tooltip>
                
                                    <CredentialsForm bind:open={entryActions[credsKind][creds.id].clone} action='clone'
                                    existingID={creds.id} shared={credsKind == 'shared'} />
                                    <Button size="xs" on:click={() => {entryActions[credsKind][creds.id].clone = true}}><FileCloneSolid/></Button>
                                    <Tooltip>{t('btn.clone')}</Tooltip>
                
                                    <Button size="xs" on:click={() => {deleteCredentials(creds.id, credsKind == 'shared')}}><TrashBinSolid/></Button>
                                    <Tooltip>{t('btn.delete')}</Tooltip>
                                </TableBodyCell>
                            </TableBodyRow>
                        {/each}
                    </TableBody>
                    </Table>
                    {#if !entryList[credsKind].length}
                        <div class={classSpinnerDiv}><Spinner/></div>
                    {/if}
                </div>
                <div>
                    {#each entryList[credsKind] as creds (creds.id)}
                        <div id="creds-infos-{credsKind}-{creds.id}">
                            <Popover triggeredBy="#creds-name-{credsKind}-{creds.id}" class={classPopover} placement="bottom-start">
                                <div class="p-3 space-y-2">
                                    <h3 class={classPopoverTitle}>{t('creds.info')}</h3>
                                </div>
                                <table>
                                    <tbody>
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
                        </div>
                    {/each}
                </div>
            </AccordionItem>
        {/each}
    </Accordion>    
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button>{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem on:click={() => {addUserModalId = Date.now(); addUserModal = true}}>
                <UserSolid class="inline-block"/> {t('creds.user')}
            </DropdownItem>
            <DropdownItem on:click={() => {addSharedModalId = Date.now(); addSharedModal = true}}>
                <UsersGroupSolid class="inline-block"/> {t('creds.shared')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>

{#key addUserModalId}
    <CredentialsForm bind:open={addUserModal} action='add' shared={false} />
{/key}
{#key addSharedModalId}
    <CredentialsForm bind:open={addSharedModal} action='add' shared={true} />
{/key}
