<script lang="ts">
    import { onMount } from 'svelte';

    import {
      Navbar, NavBrand, NavLi, NavUl, NavHamburger,
      Dropdown, DropdownItem, DropdownDivider, 
      Button, Tooltip, DarkMode, Spinner,
    } from 'flowbite-svelte';
    import {
      ChevronDownOutline, UserSettingsSolid, LockSolid, BookSolid, BugSolid, GithubSolid,
    } from 'flowbite-svelte-icons';

    import { share } from './State.svelte.ts';
    import { setDarkLightMode } from './DarkLightMode.ts';
    import { apiGet, getCSRFFormToken } from '../util/api.ts';
    import { navFooterClass, classBtnBase } from './Style.ts';

    let loaded: boolean = $state(false);

    const navItemClass = 'font-bold lg:text-lg max-lg:text-base py-2 px-4 hover:bg-primary-200/20 dark:hover:bg-primary-100/10 hover:text-primary-600 dark:hover:text-primary-500';
    const navItemSubClass = 'font-bold py-2 px-4 lg:text-base max-lg:text-sm hover:bg-gray-100 dark:hover:bg-gray-600 block';
    const navContainerClass = 'mx-auto flex flex-wrap justify-between items-center container overflow-hidden';
    const navDropdownClass = 'w-44 z-20 border-b border-r border-l rounded-b';
    const navDropdownDividerClass = 'my-1 h-px bg-primary-300 dark:bg-gray-600';

    function setBackendStates(j: any) {
      $share.backend = j;
      loaded = true;
    }

    onMount(() => {
      setDarkLightMode(document);
      apiGet('frontend/info', setBackendStates);
    });
</script>
  
<Navbar class="border-b rounded-b-lg {navFooterClass}" {navContainerClass}>
  {#key $share.backend.logo}
    <NavBrand href="/">
      {#if $share.backend.length == 0}
        <Spinner size="sm" />
      {:else}
        <img loading="lazy" src="{$share.backend.logo}" alt="HOME" class="aw-nav-icon" referrerpolicy="no-referrer">
      {/if}
    </NavBrand>
  {/key}
  {#if $share.backend.authenticated}
    <NavUl class="order-1" activeClass={navItemClass} nonActiveClass={navItemClass}>
      <NavLi href="/">Dashboard</NavLi>
      <NavLi class="cursor-pointer">
        Configure<ChevronDownOutline class="w-6 h-6 ms-2 text-primary-800 dark:text-white inline" />
      </NavLi>
      <Dropdown class="{navDropdownClass} {navFooterClass}">
        <DropdownItem href="/config/system.html" defaultClass={navItemSubClass}>System</DropdownItem>
        <DropdownDivider divClass={navDropdownDividerClass} />
      </Dropdown>
    </NavUl>
  {/if}
  <div class="flex md:order-2">
    <DarkMode size="sm" btnClass="{classBtnBase} px-4 py-2"></DarkMode>
    <Tooltip placement="bottom">Dark/Light Mode Switch</Tooltip>
    {#if $share.backend.authenticated}
      <Button size="xs" class="ml-2"><UserSettingsSolid /></Button>
      <Tooltip placement="bottom">Settings</Tooltip>
    {/if}

    <Button size="xs" class="ml-2 max-sm:hidden" href="https://webui.ansibleguy.net"><BookSolid /></Button>
    <Tooltip placement="bottom">Documentation</Tooltip>
    <Button size="xs" class="ml-2 max-sm:hidden" href="https://github.com/O-X-L/ansible-webui"><GithubSolid /></Button>
    <Tooltip placement="top">Open Source Repository</Tooltip>
    <Button size="xs" class="ml-2 max-sm:hidden" href="https://github.com/O-X-L/ansible-webui/issues"><BugSolid /></Button>
    <Tooltip placement="top">Report Bugs</Tooltip>
    {#if $share.backend.authenticated}
      <form method="post" action="/o/">
        <Button size="xs" class="ml-2 h-full" type="submit"><LockSolid /></Button>
        <Tooltip placement="bottom">Log out</Tooltip>
        {@html getCSRFFormToken()}
      </form>
    {/if}
    <NavHamburger />
  </div>
</Navbar>