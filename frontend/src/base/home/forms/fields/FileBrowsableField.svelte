<script lang="ts">
    // autocomplete via api filesystem-browsing (playbook/inventory)
    // todo: inventory_file multi-input

    import { onDestroy } from 'svelte';

    import {
        FolderSolid, FileSolid,
    } from 'flowbite-svelte-icons';
    import {
        Input,
    } from 'flowbite-svelte';

    import { share } from '../../../Share.js';
    import { tq } from '../../../../util/translate.js';
    import { rsplit } from '../../../../util/main.js';
    import { apiGet } from '../../../../util/api.js';
    import type { inputColorType } from '../../../Types.js';
    import { inputBaseColor } from '../../../../util/form.js';
    import {
        classDynChoices, classDynChoicesItem, classDynChoicesRow,
    } from '../../../Style.js';

    let {
        elementID = '',
        required = false,
        browsableFieldInFocus = $bindable(''),
        value = $bindable(''),
        color = $bindable(inputBaseColor),
        repositoryID = $bindable(0),
    } : {
        browsableFieldInFocus: string,
        elementID: string,
        value: string,
        color: inputColorType,
        required: boolean,
        repositoryID: number|null,
    } = $props();

    let loaded = $state(false);

    function t(code: string) : string {
        return tq($share, code);
    }

    interface browseResponse {
        dirs: string[],
        files: string[],
    }

    const fsBrowseNone = {dirs: [], files: []};
    let fsBrowseCurrentBase: string = $state('');
    let fsBrowseChoices: browseResponse = $state(fsBrowseNone);  // cached full-list of dirs/files
    let fsBrowseChoicesActive: browseResponse = $state(fsBrowseNone);  // list we actually show to the user; to be manipulated

    function fsBrowseClick() {
        fsBrowseClearActive();
        fsBrowse();
    }

    function fsBrowse(event: Event|null = null) {
        // validate current input and query new contents if required
        browsableFieldInFocus = elementID;
        fsBrowseValidate();
        let requireQuery = false;

        // if we are new - no value was selected yet or we have not yet got an API response
        if (!value || (fsBrowseChoices.files.length == 0 && fsBrowseChoices.dirs.length == 0)) {
            requireQuery = true;
        }

        // autocorrect
        if (value && value.includes('//')) {
            value = value.replaceAll('//', '/');
        }

        let base = fsBrowseBase();

        // backspace - the user exited the child-directory; we need to re-query the parent-dir
        if (base != fsBrowseCurrentBase) {
            requireQuery = true;
            fsBrowseCurrentBase = base;
        }

        // if the current input is a valid directory - append a slash and query its content
        if (value != '' && base == value) {
            if (!value.endsWith('/')) {
                value += '/';
            }
            requireQuery = true;
        }

        if (requireQuery) {
            fsBrowseQueryNew(base);

        } else {
            fsBrowseSubstringFilter();
            if (event && event.data) {
                // ignore backspace
                fsBrowseAutoComplete();
                fsBrowseValidate();
            }
        }
    }

    function fsBrowseQueryNew(base: string|null = null) {
        if (!base) {
            base = fsBrowseBase();
        }

        apiGet(
            `fs/browse/${repositoryID||0}?base=${base}`,
            (j: any) => {fsBrowseUpdate(j)},
        );
    }

    function fsBrowseSubstringFilter() {
        // filter choices by sub-string
        let [_, current] = fsBrowseGetPathCurrent();
        if (!current) {
            fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseChoices));
            return;
        }

        let newChoices: browseResponse = JSON.parse(JSON.stringify(fsBrowseNone));
        for (let d of fsBrowseChoices.dirs) {
            if (d.includes(current)) {
                newChoices.dirs.push(d);
            }
        }
        for (let f of fsBrowseChoices.files) {
            if (f.includes(current)) {
                newChoices.files.push(f);
            }
        }
        fsBrowseChoicesActive = newChoices;
    }

    function fsBrowseAutoComplete() {
        // autocomplete if only one option is left
        if (fsBrowseChoicesActive.files.length == 0 && fsBrowseChoicesActive.dirs.length == 1) {
            fsBrowseSetCurrent(fsBrowseChoicesActive.dirs[0] + '/');
            fsBrowseQueryNew();

        } else if (fsBrowseChoicesActive.files.length == 1 && fsBrowseChoicesActive.dirs.length == 0) {
            fsBrowseSetCurrent(fsBrowseChoicesActive.files[0]);
            fsBrowseChoicesActive.files = [];
        }
    }

    function fsBrowseBase() : string {
        // get directory-path without (partial-) files
        let full = value;
        let base = '';
        let [path, current] = fsBrowseGetPathCurrent();

        if (current && fsBrowseChoices.dirs.includes(current)) {
            base = full;

        } else if (path && (path != full || fsBrowseChoices.dirs.includes(path))) {
            base = path;
        }
        return base;
    }

    function fsBrowseGetPathCurrent() : [string|null, string|null] {
        let full = value;
        if (!full) {
            return [null, null];
        }
        if (!full.includes('/')) {
            return [null, full];
        }

        let p = rsplit(full, '/');
        return [p[0], p[1]];
    }

    function fsBrowseSetCurrent(current: string) {
        let [path, _] = fsBrowseGetPathCurrent();
        if (path) {
            value = `${path}/${current}`;
        } else {
            value = current;
        }
    }

    function fsBrowseClearActive() {
        browsableFieldInFocus = '';
        fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseNone));
    }

    function fsBrowseClear() {
        fsBrowseClearActive();
        fsBrowseChoices = fsBrowseNone;
    }

    function fsBrowseValidate() {
        // checks if the current input (without base-path) is a valid choice
        let [path, current] = fsBrowseGetPathCurrent();

        if (fsBrowseChoices.files.length == 0 && fsBrowseChoices.dirs.length == 0) {
            return;
        }

        if ((path && fsBrowseChoices.files.includes(path)) || (current && fsBrowseChoices.files.includes(current))) {
            fsBrowseClearActive();
            color = 'green';
        } else if (value != '') {
            color = 'red';
        } else {
            color = inputBaseColor;
        }
    }

    function fsBrowseUpdate(j: any) {
        browsableFieldInFocus = elementID;
        if (j.error) {
            return;
        }
        fsBrowseChoices = j;
        fsBrowseChoicesActive = JSON.parse(JSON.stringify(fsBrowseChoices));
        fsBrowseValidate();
        loaded = true;
    }

    function fsBrowseSelect(c: string) {
        if (fsBrowseChoices.dirs.includes(c) && !c.endsWith('/')) {
            c += '/';
        }

        if (value && value.endsWith('/')) {
            value += c;
            fsBrowse();
            return;
        }

        let [path, _] = fsBrowseGetPathCurrent();
        if (!path) {
            value = c;
        } else {
            value = `${path}/${c}`;
        }
        fsBrowse();
    }

    onDestroy(()=>{
        fsBrowseClear();
    });
</script>

<Input id={elementID} bind:value={value} bind:color={color} required={required} autocomplete="off"
    on:blur={() => {fsBrowseValidate()}}
    on:input={(event) => {fsBrowse(event)}}
    on:click={() => {fsBrowseClick()}} />
{#if browsableFieldInFocus == elementID && loaded}
    <div class={classDynChoices}>
        {#each fsBrowseChoicesActive.files as c}
            <button type="button" class={classDynChoicesItem}
                onclick={(e) => {fsBrowseSelect(c)}}>
                <FileSolid class="inline-block" /> {c}
            </button>
        {/each}
        {#each fsBrowseChoicesActive.dirs as c}
            <button type="button" class={classDynChoicesItem}
                onclick={(e) => {fsBrowseSelect(c)}}>
                <FolderSolid class="inline-block" /> {c}
            </button>
        {/each}
        {#if !fsBrowseChoicesActive.dirs.length && !fsBrowseChoicesActive.files.length}
            <div class="{classDynChoicesRow} cursor-wait">
                - {t('jobs.form.file_browse.empty')} -
            </div>
        {/if}
    </div>
{/if}
