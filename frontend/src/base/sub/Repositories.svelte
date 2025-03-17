<script lang="ts">
    import {
        Spinner, Button, Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';
    import {
        ChevronDownOutline, CodeBranchSolid, FolderOpenSolid,
    } from 'flowbite-svelte-icons'

    import { share } from '../State.js';
    import { tq } from '../../util/translate.js';

    let addGitModal = $state(false);
    let addLocalModal = $state(false);

    function t(code: string) {
      return tq($share, code);
    }
</script>

<div class="flex justify-between">
    <div></div>
    <div>
        <Button>{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem on:click={() => (addGitModal = true)}><CodeBranchSolid class="inline-block"/> {t('repos.git')}</DropdownItem>
            <DropdownItem on:click={() => (addLocalModal = true)}><FolderOpenSolid class="inline-block"/> {t('repos.local')}</DropdownItem>
        </Dropdown>
    </div>    
</div>

<div class="text-center mt-20">
    <Spinner/>
</div>

<Accordion>
    <AccordionItem>
        <span slot="header">{t('repos.git')}</span>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('repos.local')}</span>
    </AccordionItem>
</Accordion>
