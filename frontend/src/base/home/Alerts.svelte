<script lang="ts">
    import {
        Spinner, Button, Dropdown, DropdownItem, Accordion, AccordionItem,
    } from 'flowbite-svelte';
    import {
        ChevronDownOutline, UserSolid, MessagesSolid, UsersGroupSolid,
    } from 'flowbite-svelte-icons'

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { classSpinnerDiv } from '../Style.js';

    let { open = $bindable(false) } = $props();
    
    let addUserModal = $state(false);
    let addGroupModal = $state(false);
    let addGlobalModal = $state(false);
    let addPluginModal = $state(false);

    function t(code: string) : string {
      return tq($share, code);
    }
</script>

<div class="flex justify-between">
    <div></div>
    <div>
        <Button>{t('btn.add')}<ChevronDownOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
        <Dropdown>
            <DropdownItem on:click={() => (addUserModal = true)}>
                <UserSolid class="inline-block"/> {t('alerts.user')}
            </DropdownItem>
            <DropdownItem on:click={() => (addGroupModal = true)}>
                <UsersGroupSolid class="inline-block"/> {t('alerts.group')}
            </DropdownItem>
            <DropdownItem on:click={() => (addGlobalModal = true)}>
                <UsersGroupSolid class="inline-block"/> {t('alerts.global')}
            </DropdownItem>
            <DropdownItem on:click={() => (addPluginModal = true)}>
                <MessagesSolid class="inline-block"/> {t('alerts.plugin')}
            </DropdownItem>
        </Dropdown>
    </div>    
</div>

<Accordion>
    <AccordionItem>
        <span slot="header">{t('alerts.user')}</span>
        <div class={classSpinnerDiv}><Spinner/></div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('alerts.group')}</span>
        <div class={classSpinnerDiv}><Spinner/></div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('alerts.global')}</span>
        <div class={classSpinnerDiv}><Spinner/></div>
    </AccordionItem>
    <AccordionItem>
        <span slot="header">{t('alerts.plugin')}</span>
        <div class={classSpinnerDiv}><Spinner/></div>
    </AccordionItem>
</Accordion>
