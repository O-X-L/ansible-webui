<script lang="ts">
    import { onMount } from 'svelte';

    import { FileCloneSolid, FileCodeSolid, LayersSolid, CogSolid, FolderDuplicateSolid } from 'flowbite-svelte-icons';
    import {
        Spinner, Accordion, AccordionItem, Button, Tooltip,
        Table, TableHead, TableHeadCell, TableBody, TableBodyCell, TableBodyRow,
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { saveToClipboard } from '../../util/main.js';
    import { apiGet, cacheKey } from '../../util/api.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classSpinnerDiv, classListHeader, classListContent, classFooterSpacing, classSpoilerItem, classSpoilerPad,
    } from '../Style.js';
     
    let { open = $bindable(false) } = $props();

    const NESTED_ENV_KEYS = ['Python Modules', 'Ansible Config', 'Ansible Collections'];
    const URL_PYPI = 'https://pypi.org/project/';
    const URLS = {
        'Ansible Config': 'https://docs.ansible.com/ansible/latest/reference_appendices/config.html#',
        'Ansible Collection': 'https://galaxy.ansible.com/ui/repo/published/',
        'Ansible Core': 'https://github.com/ansible/ansible/releases/latest',
        'Ansible Runner': `${URL_PYPI}/ansible-runner/`,
        'Ansible WebUI (OXL)': 'https://github.com/O-X-L/ansible-webui',
        'Ansible Executor (OXL)': 'https://github.com/O-X-L/ansible-executor',
        'Django': `${URL_PYPI}/django/`,
        'Django API': `${URL_PYPI}/djangorestframework`,
        'Gunicorn': `${URL_PYPI}/gunicorn/`,
        'Ansible ARA': `${URL_PYPI}/ara/`,
        'AWS CLI': `${URL_PYPI}/awscli/`,
        'AWS Session-Manager-Plugin': 'https://github.com/aws/session-manager-plugin/releases/latest',
        'Git': 'https://github.com/git/git/tags',
        'Jinja': `${URL_PYPI}/Jinja2/`,
        'Python': 'https://devguide.python.org/versions/',
    }

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let loaded: boolean = $state(false);

    interface envInfoMainType {
        name: string,
        version: string,
    }
    interface envInfoAnsibleCnfType {
        setting: string,
        value: string,
        comment: string,
    }
    interface envInfoAnsibleColType {
        name: string,
        version: string,
        path: string,
    }
    interface envInfoType {
        'Ansible WebUI': string,
        'AW DB-Schema': string,
        Linux: string,
        Git: string,
        'Ansible Core': string,
        'Ansible Runner': string,
        Django: string,
        'Django API': string,
        Gunicorn: string,
        Jinja: string,
        LibYAML: string,
        Python: string,
        User: string,
        'AWS Session-Manager-Plugin': string,
        'AWS CLI': string,
        'Ansible ARA': string,
        'Ansible Playbook': string,
        'Python Modules': envInfoMainType[],
        'Ansible Config': envInfoAnsibleCnfType[],
        'Ansible Collections': envInfoAnsibleColType[],
    }
    let envInfos: envInfoType = $state({});

    let envInfosMain: envInfoMainType[] = $state([]);

    function t(code: string) : string {
        return tq($share, code);
    }

    function searchFilterMain(item: envInfoMainType, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let v = item.version ? item.version : '';
        return (
            item.name.toLowerCase().includes(s) ||
            v.toLowerCase().includes(s)
        )
    }

    function searchFilterAnsCnf(item: envInfoAnsibleCnfType, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let c = item.comment ? item.comment : '';
        return (
            item.setting.toLowerCase().includes(s) ||
            item.value.toLowerCase().includes(s) ||
            c.toLowerCase().includes(s)
        )
    }

    function searchFilterAnsCol(item: envInfoAnsibleColType, searchTerm: string) : boolean {
        let s = searchTerm.toLowerCase();
        let v = item.version ? item.version : '';
        return (
            item.name.toLowerCase().includes(s) ||
            v.toLowerCase().includes(s) ||
            item.path.toLowerCase().includes(s)
        )
    }

    function buildAnsCnfUrl(s: string) {
        return `${URLS['Ansible Config']}${s.toLowerCase().replaceAll('_', '-')}`
    }

    function buildAnsColUrl(c: string) {
        let n = c;
        if (n.includes(' (')) {
            n = n.split(' ')[0];
        }
        return `${URLS['Ansible Collection']}${n.replaceAll('.', '/')}`
    }

    function loadEnvInfos(j: any) {
        if (j === null) {
            return;
        }
        envInfos = j;
        buildMainEnvInfos();
        loaded = true;
    }

    function buildMainEnvInfos() {
        let d: envInfoMainType[] = [];

        for (let [k, v] of Object.entries(envInfos)) {
            if (!NESTED_ENV_KEYS.includes(k)) {
                d.push({name: k, version: v});
            }
        }

        envInfosMain = d;
    }

    function buildEnvInfos() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`environment?${cacheKey($share)}`, loadEnvInfos);
    }

    onMount(() => {
        setTimeout(buildEnvInfos, 500);  // wait to fetch version
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg} />

{#if !loaded}
    <div class={classSpinnerDiv}><Spinner/></div>
{:else}
    <Accordion>
        <AccordionItem open defaultClass="{classSpoilerItem} env-main" paddingDefault={classSpoilerPad}>
            <span slot="header">
                <LayersSolid class="inline-block"/> {t('env.main')}
            </span>

            <Table striped={true} bind:items={envInfosMain} hoverable={true} shadow
                placeholder={t('common.search')} filter={(item, searchTerm) => (searchFilterMain(item, searchTerm))}>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                        {t('common.name')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.version.localeCompare(b.version)}>
                        {t('common.version')}
                    </TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow slot="row" let:item>
                        {#if Object.keys(URLS).includes(item.name)}
                            <TableBodyCell tdClass={classListContent}>
                                <a href={URLS[item.name]}>{item.name}</a>
                            </TableBodyCell>
                        {:else}
                            <TableBodyCell tdClass={classListContent}>{item.name}</TableBodyCell>
                        {/if}
                        <TableBodyCell tdClass={classListContent}>{item.version ? item.version : '-'}</TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </AccordionItem>
        <AccordionItem defaultClass="{classSpoilerItem} env-anscnf" paddingDefault={classSpoilerPad}>
            <span slot="header">
                <CogSolid class="inline-block"/> {t('env.ansible.config')}
            </span>

            <Table striped={true} bind:items={envInfos['Ansible Config']} hoverable={true} shadow
                placeholder={t('common.search')} filter={(item, searchTerm) => (searchFilterAnsCnf(item, searchTerm))}>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell sort={(a, b) => a.setting.localeCompare(b.setting)} defaultSort>
                        {t('common.setting')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.value.localeCompare(b.value)}>
                        {t('common.value')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.comment.localeCompare(b.comment)}>
                        {t('common.comment')}
                    </TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow slot="row" let:item>
                        <TableBodyCell tdClass={classListContent}>
                            <a href={buildAnsCnfUrl(item.setting)}>{item.setting}</a>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>{item.value}</TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>{item.comment ? item.comment : '-'}</TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </AccordionItem>
        <AccordionItem defaultClass="{classSpoilerItem} env-anscol" paddingDefault={classSpoilerPad}>
            <span slot="header">
                <FolderDuplicateSolid class="inline-block"/> {t('env.ansible.collections')}
            </span>

            <Table striped={true} bind:items={envInfos['Ansible Collections']} hoverable={true} shadow
                placeholder={t('common.search')} filter={(item, searchTerm) => (searchFilterAnsCol(item, searchTerm))}>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                        {t('common.name')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.version.localeCompare(b.version)}>
                        {t('common.version')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.path.localeCompare(b.path)}>
                        {t('common.path')}
                    </TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow slot="row" let:item>
                        <TableBodyCell tdClass={classListContent}>
                            <a href={buildAnsColUrl(item.name)}>{item.name}</a>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>{item.version}</TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>{item.path}</TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </AccordionItem>
        <AccordionItem defaultClass="{classSpoilerItem} env-pymod" paddingDefault={classSpoilerPad}>
            <span slot="header">
                <FileCodeSolid class="inline-block"/> {t('env.python_modules')}
            </span>

            <Table striped={true} bind:items={envInfos['Python Modules']} hoverable={true} shadow
                placeholder={t('common.search')} filter={(item, searchTerm) => (searchFilterMain(item, searchTerm))}>
                <TableHead theadClass={classListHeader}>
                    <TableHeadCell sort={(a, b) => a.name.localeCompare(b.name)} defaultSort>
                        {t('common.name')}
                    </TableHeadCell>
                    <TableHeadCell sort={(a, b) => a.version.localeCompare(b.version)}>
                        {t('common.version')}
                    </TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow slot="row" let:item>
                        <TableBodyCell tdClass={classListContent}>
                            <a href="https://pypi.org/project/{item.name}/">{item.name}</a>
                        </TableBodyCell>
                        <TableBodyCell tdClass={classListContent}>{item.version ? item.version : '-'}</TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </AccordionItem>
    </Accordion>

    <Button size="xs" class="mt-5 ml-2" id="env-btn-copy" on:click={() => saveToClipboard(envInfos)}><FileCloneSolid/></Button>
    <Tooltip>{t('common.click_to_copy')}</Tooltip>
{/if}

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
