<script lang="ts">
    import { onDestroy } from 'svelte';

    import {
        FolderSolid, ServerSolid, InfoCircleSolid,
    } from 'flowbite-svelte-icons';
    import {
        Input, Spinner, Popover,
    } from 'flowbite-svelte';

    import { share } from '../../../Share.js';
    import { tq } from '../../../../util/translate.js';
    import { apiGet } from '../../../../util/api.js';
    import type { inputColorType } from '../../../Types.js';
    import { inputBaseColor } from '../../../../util/form.js';
    import {
        classSpinnerDiv, classPopover, classPopoverTitle,
        classDynChoices, classDynChoicesItem,
    } from '../../../Style.js';

    let {
        elementID = '',
        required = false,
        inventoryListFieldInFocus = $bindable(''),
        value = $bindable(''),
        color = $bindable(inputBaseColor),
        repositoryID = $bindable(0),
        inventoryFile = $bindable(''),
    } : {
        inventoryListFieldInFocus: string,
        elementID: string,
        value: string,
        color: inputColorType,
        required: boolean,
        repositoryID: number|null,
        inventoryFile: string|null,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }

    // autocomplete via api inventory-listing (limit)
    interface inventoryListResponse {
        hosts: string[],
        groups: string[],
        members: any,
        ansible_hosts: any,
    }

    const inventoryListNone = {hosts: [], groups: [], members: {}, ansible_hosts: {}};
    let loaded: boolean = $state(false);
    let loading: boolean = $state(false);
    let listChoices: inventoryListResponse = $state(inventoryListNone);
    let listChoicesActive: inventoryListResponse = $state(inventoryListNone);
    let queriedRepo: number = $state(0);
    let queriedInventory: string|null = $state('');

    function inventoryListClick(_: Event|null = null) {
        inventoryListFieldInFocus = elementID;
        listChoicesActive = listChoices;
        inventoryListQueryNewIfRequired();
    }

    function inventoryListInput(event: Event|null = null) {
        inventoryListFieldInFocus = elementID;

        inventoryListValidate();

        // autocorrect
        if (value && value.includes(',,')) {
            value = value.replaceAll(',,', ',');
        }

        inventoryListSubstringFilter();
        if (event && event.data) {
            // ignore backspace
            inventoryListAutoComplete();
        }
        inventoryListQueryNewIfRequired();
    }

    function inventoryListSubstringFilter() {
        // filter choices by sub-string
        let choices = inventoryListGet();
        if (choices.length == 0 || value.endsWith(',')) {
            listChoicesActive = JSON.parse(JSON.stringify(listChoices));
            return;
        }
        let current = choices.pop();
        if (!current) {
            return;
        }

        let newChoices: inventoryListResponse = JSON.parse(JSON.stringify(inventoryListNone));
        for (let g of listChoices.groups) {
            if (g.includes(current) && !choices.includes(g)) {
                newChoices.groups.push(g);
            }
        }
        for (let h of listChoices.hosts) {
            if (h.includes(current) && !choices.includes(h)) {
                newChoices.hosts.push(h);
            }
        }
        listChoicesActive = newChoices;
    }

    function inventoryListAutoComplete() {
        // autocomplete if only one option is left
        if (listChoicesActive.hosts.length == 0 && listChoicesActive.groups.length == 1) {
            inventoryListSetCurrentByKeyboard(listChoicesActive.groups[0]);
            listChoicesActive.groups = [];

        } else if (listChoicesActive.hosts.length == 1 && listChoicesActive.groups.length == 0) {
            inventoryListSetCurrentByKeyboard(listChoicesActive.hosts[0]);
            listChoicesActive.hosts = [];
        }
    }

    function inventoryListQueryNewIfRequired() {
        // we do not have to re-query the same inventory
        let requireQuery = !loaded;

        // inventory has changed
        if (inventoryFile === null) {
            // dynamic inventory
            requireQuery = true;
        } else if (inventoryFile != queriedInventory) {
            requireQuery = true;
            queriedInventory = inventoryFile;
        }
        // repo has changed
        if (!repositoryID) {
            queriedRepo = 0;
        } else if (repositoryID != queriedRepo) {
            requireQuery = true;
            queriedRepo = repositoryID;
        }

        if (!requireQuery) {
            return;
        }
   
        loading = true;
        apiGet(
            `inventory/list?limit=all&inventory=${encodeURIComponent(inventoryFile||'')}&repository=${repositoryID||0}`,
            (j: any) => {inventoryListLoadNew(j)},
        );
    }

    function inventoryListLoadNew(j: any) {
        if (j.error) {
            return;
        }

        listChoices = j
        listChoicesActive = JSON.parse(JSON.stringify(listChoices))

        loading = false;
        loaded = true;
        inventoryListValidate();
    }

    function inventoryListGet() : string[] {
        if (!value) {
            return [];
        }
        return value.split(',').filter(e => e.trim() !== '');
    }

    function inventoryListSelectCurrentBase(current: string) : [boolean, string[]] {
        let limits = inventoryListGet();
        if (limits.length == 0) {
            value = current;
            inventoryListValidate();
            return [true, []];
        }
        if (limits.includes(current)) {
            return [true, []];
        }
        return [false, limits];
    }

    function inventoryListSelectCurrentByClick(current: string) {
        const [done, limits] = inventoryListSelectCurrentBase(current);
        if (done) {
            return;
        }
        value = `${limits.join(',')},${current}`;
        inventoryListValidate();
    }

    function inventoryListSetCurrentByKeyboard(current: string) {
        const [done, limits] = inventoryListSelectCurrentBase(current);
        if (done) {
            return;
        }
        let last = limits.pop();
        if (last && (listChoices.hosts.includes(last) || listChoices.groups.includes(last))) {
            current = `${last},${current}`;
        }
        if (limits.length == 0) {
            value = current;
        } else {
            value = `${limits.join(',')},${current}`;
        }
        inventoryListValidate();
    }

    function inventoryListValidate() {
        if (!value || value == '' || value.endsWith(',')) {
            color = inputBaseColor;
            return;
        }
        let results = [];
        for (let v of inventoryListGet()) {
            results.push(
                listChoices.hosts.includes(v) || listChoices.groups.includes(v)
            )
        }

        if (results.every(v => v === true)) {
            color = 'green';
        } else {
            color = 'red';
        }
    }

    function inventoryListGroupMembers(group: string) : string[] {
        let members = listChoices.members[group];
        if (!members) {
            return [];
        }
        return members;
    }

    function inventoryListHostTarget(host: string) : string|null {
        let ansible_host = listChoices.ansible_hosts[host];
        if (!ansible_host || String(ansible_host).includes('{{')) {
            return null;
        }
        return ansible_host;
    }

    function inventoryListHostTargetStr(host: string) : string {
        let target = inventoryListHostTarget(host);
        if (!target) {
            return '';
        }
        return ` (${target})`;
    }
</script>

<Input id={elementID} required={required} autocomplete="off"
    bind:value={value} bind:color={color}
    on:blur={() => {inventoryListValidate()}}
    on:input={(event) => {inventoryListInput(event)}}
    on:click={() => {inventoryListClick()}} />
{#if inventoryListFieldInFocus == elementID && (listChoicesActive.groups.length > 0 || listChoicesActive.hosts.length > 0) }
    <div class={classDynChoices}>
        {#each listChoicesActive.groups as c}
            <button type="button" class={classDynChoicesItem}
                onclick={(e) => {inventoryListSelectCurrentByClick(c)}}>
                <FolderSolid class="inline-block" /> {c}
                <span id="{elementID}-group-members-{c}" class="ml-1">
                    <InfoCircleSolid class="inline-block" size="sm"/>
                    <span class="sr-only">{t('alerts.group')} {t('permission.members')}</span>
                </span>
                <Popover triggeredBy="#{elementID}-group-members-{c}" class="{classPopover} max-h-60 overflow-y-scroll" placement="bottom-start">
                    <div class="p-3 space-y-2">
                        <h3 class={classPopoverTitle}>{t('alerts.group')} {t('permission.members')}</h3>
                    </div>
                    <div class="font-bold">{t('permission.members')}: {inventoryListGroupMembers(c).length}</div>
                    {#each inventoryListGroupMembers(c) as host}
                        <div><ServerSolid class="inline-block" /> {host}{inventoryListHostTargetStr(host)}</div>
                    {/each}
                </Popover>
            </button>
        {/each}
        {#each listChoicesActive.hosts as c}
            <button type="button" class={classDynChoicesItem}
                onclick={(e) => {inventoryListSelectCurrentByClick(c)}}>
                <ServerSolid class="inline-block" /> {c}
                {#if inventoryListHostTarget(c)}
                    <span id="{elementID}-host-ip-{c}" class="ml-1">
                        <InfoCircleSolid class="inline-block" size="sm"/>
                        <span class="sr-only">{t('alerts.group')} {t('permission.members')}</span>
                    </span>
                    <Popover triggeredBy="#{elementID}-host-ip-{c}" class="{classPopover} max-h-60 overflow-y-scroll" placement="bottom-start">
                        <div class="p-3 space-y-2">
                            <h3 class={classPopoverTitle}>Ansible Host</h3>
                        </div>
                        <div class="font-bold">{inventoryListHostTarget(c)}</div>
                    </Popover>
                {/if}
            </button>
        {/each}
    </div>
{:else if loading}
    <div class={classSpinnerDiv}><Spinner/></div>
{/if}
