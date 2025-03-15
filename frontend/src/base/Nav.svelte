<script lang="ts">
    import { onMount } from 'svelte';

    import {
      Navbar, NavBrand, Dropdown, Button, Tooltip, DarkMode, Spinner, Radio, Alert,
      // NavLi, NavUl, DropdownItem, DropdownDivider, NavHamburger
    } from 'flowbite-svelte';
    import {
      LockSolid, BookSolid, BugSolid, GithubSolid, GlobeSolid,
      // ChevronDownOutline, AdjustmentsHorizontalSolid,
    } from 'flowbite-svelte-icons';

    import { share } from './State.js';
    import { type formAlerts } from './Types.js';
    import { tq, flagIcon } from '../util/translate.js';
    import { setDarkLightMode } from './DarkLightMode.js';
    import { apiGet, getCSRFFormToken } from '../util/api.js';
    import { classNavFooter, classBtnBase } from './Style.js';

    let loaded: boolean = $state(false);
    let language: string = $state('en');
    let alerts: formAlerts[] = $state([]);

    $effect(() => {
      if (!loaded) {
        return;
      }
      if (localStorage.language != language) {
        localStorage.language = language;
        location.reload();
      }
    })

    // const navItemClass = 'font-bold lg:text-lg max-lg:text-base py-2 px-4 hover:bg-primary-200/20 dark:hover:bg-primary-100/10 hover:text-primary-600 dark:hover:text-primary-500';
    // const navItemSubClass = 'font-bold py-2 px-4 lg:text-base max-lg:text-sm hover:bg-gray-100 dark:hover:bg-gray-600 block';
    const navContainerClass = 'mx-auto flex flex-wrap justify-between items-center container overflow-hidden';
    // const navDropdownClass = 'w-44 z-20 border-b border-r border-l rounded-b';
    // const navDropdownDividerClass = 'my-1 h-px bg-primary-300 dark:bg-gray-600';

    function setBackendStates(j: any) {
      $share.backend = j;
      loaded = true;
    }

    function setTranslations(j: any) {
      $share.lang = j;
    }

    function showBackendFormErrors() {
      let errors = document.querySelectorAll('.aw-form-alert');
      if (errors) {
        for (let e of errors) {
          if (e.field) {
            alerts.push({
              color: 'red',
              title: `Input into field ${e.field} was invalid`,
              msg: e.innerText,
            })
          } else {
            alerts.push({
              color: 'red',
              title: 'Input was invalid',
              msg: e.innerText,
            })
          }
        }
      }
    }

    function t(code: string) {
      return tq($share, code);
    }

    onMount(() => {
      setDarkLightMode(document);
      if (localStorage.language) {
        language = localStorage.language;
      } else {
        localStorage.language = language;
      }
      apiGet('frontend/info', setBackendStates);
      apiGet('frontend/lang', setTranslations);
      showBackendFormErrors();
    });
</script>
  
<Navbar class="border-b rounded-b-lg {classNavFooter}" {navContainerClass}>
  {#key $share.backend.logo}
    <NavBrand href="/">
      {#if $share.backend.length == 0}
        <Spinner size="sm" />
      {:else}
        <img loading="lazy" src="{$share.backend.logo}" alt="HOME" class="aw-nav-icon" referrerpolicy="no-referrer">
      {/if}
    </NavBrand>
  {/key}
  <!--
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
  -->
  <div class="flex md:order-2">
    <Button size="xs" class="ml-2"><GlobeSolid/></Button>
    <Dropdown class="w-48 p-3 space-y-1">
      <li class="rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600">
        <Radio bind:group={language} value={'en'}>{@html flagIcon('gb')} English</Radio>
      </li>
      <li class="rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600">
        <Radio bind:group={language} value={'de'}>{@html flagIcon('de')} Deutsch</Radio>
      </li>
    </Dropdown>
    <Tooltip placement="bottom">{t('nav.lang')}</Tooltip>

    <DarkMode size="sm" btnClass="{classBtnBase} px-4 py-2 ml-2"></DarkMode>
    <Tooltip placement="bottom">{t('nav.darkLight')}</Tooltip>
    <!--
    {#if $share.backend.authenticated}
      <Button size="xs" class="ml-2"><AdjustmentsHorizontalSolid /></Button>
      <Tooltip placement="bottom">Settings</Tooltip>
    {/if}
    -->

    <Button size="xs" class="ml-2 max-sm:hidden" href="https://webui.ansibleguy.net"><BookSolid /></Button>
    <Tooltip placement="bottom">{t('nav.docs')}</Tooltip>
    <Button size="xs" class="ml-2 max-sm:hidden" href="https://github.com/O-X-L/ansible-webui"><GithubSolid /></Button>
    <Tooltip placement="bottom">{t('nav.repo')}</Tooltip>
    <Button size="xs" class="ml-2 max-sm:hidden" href="https://github.com/O-X-L/ansible-webui/issues"><BugSolid /></Button>
    <Tooltip placement="bottom">{t('nav.bugs')}</Tooltip>
    {#if $share.backend.authenticated}
      <form method="post" action="/o/">
        <Button size="xs" class="ml-2 h-full" type="submit"><LockSolid /></Button>
        <Tooltip placement="bottom">{t('nav.logout')}</Tooltip>
        {@html getCSRFFormToken()}
      </form>
    {/if}
    <!--
    <NavHamburger />
    -->
  </div>
</Navbar>

{#if alerts.length}
  <div class="my-5">
    {#each alerts as alert}
      <Alert color={alert.color||"red"} class="mx-20">
        <div class="font-bold">{alert.title}</div>
        <div>{alert.msg}</div>
      </Alert>
    {/each}
  </div>
{/if}
