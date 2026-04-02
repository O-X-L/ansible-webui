<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        InfoCircleSolid, UserSolid, UsersGroupSolid, ChevronDownOutline, TrashBinSolid,
        EditSolid, FileCloneSolid, LockSolid, CloseCircleSolid, PlaySolid,
    } from 'flowbite-svelte-icons';
    import {
        Spinner, Button, Tooltip, Popover, Radio,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
        Dropdown, DropdownItem, Accordion, AccordionItem,
        Heading, Label, Input, Helper,
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { clickToCopy } from '../../util/main.js';
    import { apiEdit, apiGet } from '../../util/api.js';
    import CredentialsForm from './forms/Credentials.svelte';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import { type credentialsUserType, type credentialsSharedType} from './Types.js';
    import {
        classSpinnerDiv, classPopoverColumn1, classListHeader, classListContent,
        classPopover, classPopoverColumn2Div, classPopoverColumn2Text, classPopoverTitle, classFooterSpacing,
        classSpoilerItem, classSpoilerPad, classSpoilerBtn,
        classModalBackdrop, classModalBody, classModalForm, classModalInput, classModalHelp, classModalBtns,
        classModalLabel, classModalDialog,
    } from '../Style.js';
 
    const credentialsKind = ['user', 'shared'];

    let { open = $bindable(false) } = $props();

    let apiResponseHandler: APIResponseHandler = $state();
    let addUserModal = $state(false);
    let addSharedModal = $state(false);
    let addUserModalId = $state(Date.now());
    let addSharedModalId = $state(Date.now());
    let apiErrorMsg = $state('');
    let apiSuccessMsg = $state('');
    let apiSuccess = $state(false);
    let apiDataHash = $state('');
    let entryActions = $state({'shared': {}, 'user': {}});
    let updateLoop: number = $state(0);
    let updatedAt = $state(0);
    let searchedAt = $state(0);
    let newVaultCredentialsID = $state(0);
    let newVaultCredentialsKind = $state('');
    let newVaultPlaintext = $state('');
    let newVaultCiphertext = $state('');
    let newVaultLoad = $state(false);
    let newVaultModal = $state(false);

    interface credentialsFullType {
        shared: credentialsSharedType[],
        user: credentialsUserType[],
    }

    let entryList: credentialsFullType = $state({'shared': [], 'user': []});

    function t(code: string) : string {
      return tq($share, code);
    }

    function loadCredentialsList(j: any, h: string) {
        if (j === null || h == apiDataHash) {
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
        updatedAt = Date.now();
    }

    function searchFilter(item: credentialsSharedType|credentialsUserType, searchTerm: string) : boolean {
        searchedAt = Date.now();
        let s = searchTerm.toLowerCase();
        let c = '';
        if (item.category) {
            c = item.category;
        }

        let uc = item.connect_user ? item.connect_user : '';
        let ub = item.become_user ? item.become_user : '';
        let vf = item.vault_file ? item.vault_file : '';
        let vi = item.vault_id ? item.vault_id : '';
        return (
            item.name.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s) ||
            uc.toLowerCase().includes(s) ||
            ub.toLowerCase().includes(s) ||
            vf.toLowerCase().includes(s) ||
            vi.toLowerCase().includes(s)
        )
    }

    function deleteCredentials(credentialsID: number, kind: string) {
        if (!credentialsID) {
            return;
        }
        apiSuccessMsg = 'creds.action.delete';
        apiEdit('delete', `credentials/${kind}/${credentialsID}`, null, apiResponseHandler.handleRes);
    }

    function buildUpdateCredsList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`credentials?hash=${apiDataHash}`, loadCredentialsList);
    }

    function handleVaultEncryptSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            newVaultCiphertext = j.ciphertext;
            newVaultLoad = false;
        }
        apiResponseHandler.handleRes(s, j);
    }

    function vaultEncryptPlaintext() {
        newVaultLoad = true;
        apiSuccessMsg = 'creds.action.vault_encrypt';
        apiEdit(
            'post',
            `credentials/${newVaultCredentialsKind}/${newVaultCredentialsID}/vault_encrypt`,
            {plaintext: newVaultPlaintext},
            handleVaultEncryptSubmitResponse,
        );
    }

    function showVaultEncryptModal(credentialsID: number, kind: string) {
        newVaultCredentialsKind = kind;
        newVaultCredentialsID = credentialsID;
        newVaultModal = true;
    }

    function clearVaultEncryptModal(_: boolean) {
        newVaultCiphertext = '';
        newVaultPlaintext = '';
    }

    $effect(() => {
        clearVaultEncryptModal(newVaultModal);
    });

    onMount(() => {
        buildUpdateCredsList();

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateCredsList();
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
        {#each credentialsKind as credsKind (credsKind) }
            <AccordionItem defaultClass="{classSpoilerItem} creds-kind-{credsKind}" paddingDefault={classSpoilerPad}
                borderBottomClass={classSpoilerBtn}>
                <span slot="header">
                    {#if credsKind == 'user'}
                        <UserSolid class="inline-block"/>
                    {:else}
                        <UsersGroupSolid class="inline-block"/>
                    {/if}
                    {t(`creds.${credsKind}`)}
                </span>
        
                <div>
                  <Table striped={true} bind:items={entryList[credsKind]} hoverable={true} shadow
                    placeholder={t('common.search')} filter={(item, searchTerm) => {return searchFilter(item, searchTerm)}}>
                    <TableHead theadClass={classListHeader}>
                        <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                            {t('common.name')}
                        </TableHeadCell>
                        <TableHeadCell class="max-sm:hidden" sort={(a, b) => {
                            let [aU, bU] = ['', ''];
                            if (a.connect_user) {
                                aU += a.connect_user;
                            }
                            if (b.connect_user) {
                                bU += b.connect_user;
                            }
                            if (a.become_user) {
                                aU += a.become_user;
                            }
                            if (b.become_user) {
                                bU += b.become_user;
                            }
                            if (!aU) {
                                aU = 'z';
                            }
                            if (!bU) {
                                bU = 'z';
                            }

                            return aU.localeCompare(bU);
                        }}>
                            {t('creds.form.accounts')}
                        </TableHeadCell>
                        <TableHeadCell class="max-lg:hidden" sort={(a, b) => {
                            let [aV, bV] = ['', ''];
                            if (a.vault_file) {
                                aV += a.vault_file;
                            }
                            if (b.vault_file) {
                                bV += b.vault_file;
                            }
                            if (a.vault_id) {
                                aU += a.vault_id;
                            }
                            if (b.vault_id) {
                                bU += b.vault_id;
                            }
                            if (!aU) {
                                aU = 'z';
                            }
                            if (!bU) {
                                bU = 'z';
                            }

                            return aV.localeCompare(bV);
                        }}>
                            {t('creds.form.vault')}
                        </TableHeadCell>
                        <TableHeadCell class="max-lg:hidden">{t('creds.form.secrets')}</TableHeadCell>
                        <TableHeadCell>{t('common.actions')}</TableHeadCell>
                    </TableHead>
                    {#key updatedAt}
                    <TableBody tableBodyClass="divide-y">
                        <TableBodyRow slot="row" let:item>
                            <TableBodyCell tdClass={classListContent}>
                                {item.name}
                                {#key item.id}
                                    <button id="creds-name-{credsKind}-{item.id}" class="ml-1">
                                        <InfoCircleSolid size="sm"/>
                                        <span class="sr-only">{t('creds.info')}</span>
                                    </button>
                                {/key}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} max-sm:hidden">
                                {#if item.connect_user}
                                    <div>
                                        <b>{t('creds.form.connect_user')}</b>: {item.connect_user}
                                    </div>
                                {/if}
                                {#if item.become_user}
                                    <div>
                                        <b>{t('creds.form.become_user')}</b>: {item.become_user}
                                    </div>
                                {/if}
                                {#if !item.connect_user && !item.become_user}
                                    -
                                {/if}
                            </TableBodyCell>
                            <TableBodyCell class="{classListContent} max-lg:hidden">
                                {#if item.vault_pass_is_set}
                                    <div>
                                        <b>{t('creds.form.vault_pwd')}</b>
                                    </div>
                                {/if}
                                {#if item.vault_file}
                                    <div>
                                        <b>{t('creds.form.vault_file')}</b>
                                    </div>
                                {/if}
                                {#if item.vault_id}
                                    <div>
                                        <b>{t('creds.form.vault_id')}</b>: {item.vault_id}
                                    </div>
                                {/if}
                                {#if !item.vault_pass_is_set && !item.vault_file && !item.vault_id}
                                    -
                                {/if}
                            </TableBodyCell>
                            <TableBodyCell class="{classListContent} font-bold max-lg:hidden">
                                {#if item.ssh_key_is_set}
                                    <div>
                                        {t('creds.form.ssh_key')}
                                    </div>
                                {/if}
                                {#if item.connect_pass_is_set}
                                    <div>
                                        {t('creds.form.connect_pwd')}
                                    </div>
                                {/if}
                                {#if item.become_pass_is_set}
                                    <div>
                                        {t('creds.form.become_pwd')}
                                    </div>
                                {/if}
                                {#if !item.ssh_key_is_set && !item.connect_pass_is_set && !item.become_pass_is_set}
                                    -
                                {/if}
                            </TableBodyCell>
                            <TableBodyCell tdClass="{classListContent} action-btns">
                                <Button size="xs" on:click={() => {showVaultEncryptModal(item.id, credsKind)}}
                                    id="creds-btn-vaultencrypt-{credsKind}-{item.id}"
                                    disabled={!item.vault_pass_is_set && !item.vault_file && !item.vault_id}>
                                    <LockSolid/>
                                </Button>
                                <Tooltip>{t('btn.encrypt')}</Tooltip>

                                <Button size="xs" on:click={() => {entryActions[credsKind][item.id].edit = true}}
                                    id="creds-btn-edit-{credsKind}-{item.id}">
                                    <EditSolid/>
                                </Button>
                                <Tooltip>{t('btn.edit')}</Tooltip>
            
                                <Button size="xs" on:click={() => {entryActions[credsKind][item.id].clone = true}}
                                    id="creds-btn-clone-{credsKind}-{item.id}">
                                    <FileCloneSolid/>
                                </Button>
                                <Tooltip>{t('btn.clone')}</Tooltip>
            
                                <Button size="xs" on:click={() => {deleteCredentials(item.id, credsKind)}}
                                    id="creds-btn-delete-{credsKind}-{item.id}">
                                    <TrashBinSolid/>
                                </Button>
                                <Tooltip>{t('btn.delete')}</Tooltip>

                                <div class="w-0 h-0 inline">
                                    {#key item.id}
                                        <CredentialsForm bind:open={entryActions[credsKind][item.id].edit} action='edit'
                                            existingID={item.id} kind={credsKind}
                                            bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />

                                        <CredentialsForm bind:open={entryActions[credsKind][item.id].clone} action='clone'
                                            existingID={item.id} kind={credsKind}
                                            bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
                                    {/key}
                                </div>
                            </TableBodyCell>
                        </TableBodyRow>
                    </TableBody>
                    {/key}
                  </Table>
                  {#if !entryList[credsKind].length}
                      <div class={classSpinnerDiv}><Spinner/></div>
                  {/if}
                </div>
                <div>
                    {#each entryList[credsKind] as creds (creds.id)}
                        {#key searchedAt}
                        <div id="creds-infos-{credsKind}-{creds.id}">
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
                        </div>
                        {/key}
                    {/each}
                </div>
            </AccordionItem>
        {/each}
    </Accordion>    
</div>

<div class="flex justify-between">
    <div></div>
    <div class="mr-5 mt-10">
        <Button id="creds-btn-add-dd">{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem id="creds-btn-add-user" on:click={() => {addUserModalId = Date.now(); addUserModal = true}}>
                <UserSolid class="inline-block"/> {t('creds.user')}
            </DropdownItem>
            <DropdownItem id="creds-btn-add-shared" on:click={() => {addSharedModalId = Date.now(); addSharedModal = true}}>
                <UsersGroupSolid class="inline-block"/> {t('creds.shared')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>

{#key addUserModalId}
    <CredentialsForm bind:open={addUserModal} action='add' kind='user'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}
{#key addSharedModalId}
    <CredentialsForm bind:open={addSharedModal} action='add' kind='shared'
        bind:successMsg={apiSuccessMsg} bind:success={apiSuccess} />
{/key}

<Modal bind:open={newVaultModal} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('creds.vault_encrypt')}</Heading>

        {#if newVaultLoad}
            <div class={classSpinnerDiv}><Spinner/></div>
        {:else if !newVaultCiphertext}
            <div class={classModalInput}>
                <Label for="creds_vaultencrypt_plaintext" class={classModalLabel}>{t('creds.form.vault_encrypt')}</Label>
                <Input id="creds_vaultencrypt_plaintext" bind:value={newVaultPlaintext} />
                <Helper class={classModalHelp}>{@html t('creds.form.help.vault_encrypt')}</Helper>
            </div>
            <div class={classModalBtns}>
                <Button id="creds-btn-vaultencrypt-submit" on:click={() => {vaultEncryptPlaintext()}}><PlaySolid/></Button>
                <Tooltip>{t('btn.encrypt')}</Tooltip>

                <Button id="creds-btn-vaultencrypt-close" on:click={() => (newVaultModal = false)} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {:else}
            <Label class={classModalLabel}>{t('api_keys.token')}</Label>
            <button onclick={clickToCopy} class="mr-10">
<pre class="whitespace-pre-wrap break-normal text-xs">
{newVaultCiphertext}
</pre>
            </button>
            <Tooltip>{t('common.click_to_copy')}</Tooltip>

            <div class={classModalBtns}>
                <Button id="creds-btn-vaultencrypt-close" on:click={() => (newVaultModal = false)} class="inline-block ml-2">
                    <CloseCircleSolid/>
                </Button>
                <Tooltip>{t('btn.close')}</Tooltip>
            </div>
        {/if}
    </div>
</Modal>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
