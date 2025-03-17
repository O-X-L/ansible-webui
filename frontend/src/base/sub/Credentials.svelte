<script lang="ts">
    import { onMount } from 'svelte';
    import { fade } from 'svelte/transition';

    import {
        InfoCircleSolid, CloseCircleSolid, UserSolid, UsersGroupSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Popover, Radio, Alert, Tooltip, Modal, Heading,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Input, Toggle, Label, Select, Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import CredentialsForm from './forms/Credentials.svelte';
    import { classModalLabel } from '../Style.js';
    import { tq } from '../../util/translate.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import { choicesFromArray } from '../../util/form.js';
    import { type executionPromptsType, API_STATUS_CODES_OK } from './Config.js';
    import {
        classModalBackdrop, classModalBtns, classPopover, classPopoverTitle, classPopoverColumn1,
        classPopoverColumn2Text, classPopoverColumn2Div, classCenterChildDiv, classSpinnerDiv,
    } from '../Style.js';

    const apiErrorAlert = 'api-job-alert';
    const credentialsKind = ['user', 'global'];

    let addUserModal = $state(false);
    let addGlobalModal = $state(false);
    let apiError = $state('');
    let apiSuccess = $state('');
    let loaded = $state(false);
    let apiDataHash = $state('');
    let entryActions = $state({'global': {}, 'user': {}});

    interface credentialsGlobalInfos {
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
    interface credentialsUserInfos extends credentialsGlobalInfos {
        category: string,
    }
    interface credentialsFullType {
        shared: credentialsGlobalInfos[],
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
        if (!loaded) {
            for (let c of j.user) {
                entryActions['user'][c.id] = {edit: false, clone: false};
            }
            for (let c of j.shared) {
                entryActions['global'][c.id] = {edit: false, clone: false};
            }
            loaded = true;
        }
        entryList = j;
        apiDataHash = h;
    }

    function showAPIErrors(s: number, j: any) {
        if (!API_STATUS_CODES_OK.includes(s) || j.error !== undefined) {
            apiError = `${j.error} (${s})`;  // todo: pull language-code from api-error and show user the translation
            let a = document.getElementById(apiErrorAlert);
            if (a) {
                a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            }
        } else {
            apiSuccess = t('common.success');
            setTimeout(() => {apiSuccess = ''}, 6000);
        }
    }

    function deleteCredentials(credentialsID: number, global: boolean) {
        if (!credentialsID) {
            return;
        }
        apiEdit('delete', `credentials/${credentialsID}?global=${global}`, null, showAPIErrors);
    }

    function buildUpdateJobList() {
        if (typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`credentials&hash=${apiDataHash}`, loadCredentialsList);
    }

    // todo: refresh data over websockets
    setInterval(() => {
        buildUpdateJobList();
    }, $share.updateInterval)

    onMount(() => {
        buildUpdateJobList();
    })
</script>

<div id={apiErrorAlert} class="h-0"></div>
{#if apiError}
    <div transition:fade>
        <Alert border color="red" class="text-wrap">
            <CloseCircleSolid slot="icon" class="w-5 h-5" /> {apiError}
        </Alert>
    </div>
{/if}
{#if apiSuccess}
    <div transition:fade>
        <Alert border color="green" class="text-wrap">
            <InfoCircleSolid slot="icon" class="w-5 h-5" /> {apiSuccess}
        </Alert>
    </div>
{/if}

<Accordion>
    {#each credentialsKind as credsKind (credsKind) }
    <AccordionItem>
        <span slot="header">{t(`creds.${credsKind}`)}</span>

        <div>
            <Table striped={true}>
              <TableHead theadClass="text-base font-bold uppercase">
                  <TableHeadCell>{t('common.name')}</TableHeadCell>
                  <TableHeadCell>Users</TableHeadCell>
                  <TableHeadCell class="max-lg:hidden">Vault</TableHeadCell>
                  <TableHeadCell class="max-lg:hidden">Secrets</TableHeadCell>
                  <TableHeadCell>{t('common.actions')}</TableHeadCell>
              </TableHead>
              <TableBody tableBodyClass="divide-y">
                  {#each entryList.user as creds (creds.id)}
                      <TableBodyRow>
                          <TableBodyCell>
                              {creds.name}
                              <button id="creds-user-name-{creds.id}" class="ml-1">
                                  <InfoCircleSolid size="sm"/>
                                  <span class="sr-only">Credentials Information</span>
                              </button>
                          </TableBodyCell>
                          <TableBodyCell>
                            {#if creds.connect_user}
                                <div>
                                    <b>Connect User</b>: {creds.connect_user}
                                </div>
                            {/if}
                            {#if creds.become_user}
                                <div>
                                    <b>Become User</b>: {creds.become_user}
                                </div>
                            {/if}
                        </TableBodyCell>
                          <TableBodyCell class="max-lg:hidden">
                            {#if creds.vault_file}
                                <div>
                                    <b>Vault File</b>: {creds.vault_file}
                                </div>
                            {/if}
                            {#if creds.vault_id}
                                <div>
                                    <b>Vault ID</b>: {creds.vault_id}
                                </div>
                            {/if}
                        </TableBodyCell>
                          <TableBodyCell class="font-bold max-lg:hidden">
                            {#if creds.ssh_key_is_set}
                                <div>
                                    SSH private key
                                </div>
                            {/if}
                            {#if creds.connect_pass_is_set}
                                <div>
                                    Connect password
                                </div>
                            {/if}
                            {#if creds.become_pass_is_set}
                                <div>
                                    Become password
                                </div>
                            {/if}
                            {#if creds.vault_pass_is_set}
                                <div>
                                    Vault password
                                </div>
                            {/if}
                          </TableBodyCell>
                          <TableBodyCell>
                            <CredentialsForm bind:open={entryActions[credsKind][creds.id].edit} action='edit'
                            existingID={creds.id} global={credsKind == 'global'} />
                            <Button size="xs" on:click={() => {entryActions[credsKind][creds.id].edit = true}}><EditSolid/></Button>
                            <Tooltip>{t('btn.edit')}</Tooltip>
        
                            <CredentialsForm bind:open={entryActions[credsKind][creds.id].clone} action='clone'
                            existingID={creds.id} global={credsKind == 'global'} />
                            <Button size="xs" on:click={() => {entryActions[credsKind][creds.id].clone = true}}><FileCloneSolid/></Button>
                            <Tooltip>{t('btn.clone')}</Tooltip>
        
                            <Button size="xs" on:click={() => {deleteCredentials(creds.id, credsKind == 'global')}}><TrashBinSolid/></Button>
                            <Tooltip>{t('btn.delete')}</Tooltip>
                          </TableBodyCell>
                      </TableBodyRow>
                  {/each}
              </TableBody>
            </Table>
            {#if !entryList.user.length}
                <div class={classSpinnerDiv}><Spinner/></div>
            {/if}
        </div>
    </AccordionItem>        
    {/each}
</Accordion>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button>{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem on:click={() => (addUserModal = true)}>
                <UserSolid class="inline-block"/> {t('alerts.user')}
            </DropdownItem>
            <DropdownItem on:click={() => (addGlobalModal = true)}>
                <UsersGroupSolid class="inline-block"/> {t('alerts.global')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>
