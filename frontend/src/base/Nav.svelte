<script lang="ts">
    import { onMount } from 'svelte';

    import {
      Navbar, NavBrand, Dropdown, Button, Tooltip, DarkMode, Spinner, Radio,
    } from 'flowbite-svelte';
    import {
      LockSolid, BookSolid, BugSolid, GithubSolid, GlobeSolid, ServerSolid, HomeSolid, UserSettingsSolid,
    } from 'flowbite-svelte-icons';

    import { share } from './Share.js';
    import { setDarkLightMode } from './DarkLightMode.js';
    import UserSettings from './system/UserSettings.svelte';
    import { apiGet, getCSRFFormTokenHTML, cacheKey } from '../util/api.js';
    import { classNavFooter, classBtnBase, classBtnLink } from './Style.js';
    import { tq, flagIcon, getTranslationStore } from '../util/translate.js';

    const DEFAULT_LANG = 'en';

    let loaded: boolean = $state(false);
    let language: string = $state(DEFAULT_LANG);
    let userSettingsOpen = $state(false);

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
    }

    function setTranslations(j: any) {
      $share.lang = j;
      let cache = {en: j[DEFAULT_LANG]};
      if (language != DEFAULT_LANG) {
        cache[language] = j[language];
      }
      localStorage.languageCache = JSON.stringify(cache);

      loaded = true;
    }

    function t(code: string) : string {
      return tq($share, code);
    }

    function fetchBackendInfos() {
      apiGet('frontend/info', setBackendStates);
    }

    function fetchTranslations() {
      apiGet(`frontend/lang?${cacheKey($share)}`, setTranslations);
      if (!getTranslationStore($share)) {
        setTimeout(location.reload, 2000);
      }
      if (localStorage.languageCache) {
        $share.lang = JSON.parse(localStorage.languageCache);
      }
      if (localStorage.language) {
        language = localStorage.language;
      } else {
        localStorage.language = language;
      }
    }

    onMount(() => {
      fetchBackendInfos();
      setTimeout(fetchTranslations, 500);  // wait to fetch version
      setDarkLightMode(document);
    });
</script>
  
<Navbar class="border-b rounded-b-lg {classNavFooter}" {navContainerClass}>
  {#key $share.backend.logo}
    <NavBrand href="/" class="max-sm:hidden">
      {#if !$share.backend}
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
    {#if $share.backend.authenticated}
      <div class="flex md:order-1 mr-5">
        <Button id="nav-btn-home" size="xs" class="ml-2 {classBtnLink}" href="/ui"
          disabled={window.location.pathname == '/ui'}>
          <HomeSolid/></Button>
        <Tooltip placement="bottom">{t('nav.home')}</Tooltip>

        <Button id="nav-btn-system" size="xs" class="ml-2 {classBtnLink}" href="/ui/system"
          disabled={window.location.pathname == '/ui/system'}>
          <ServerSolid/></Button>
        <Tooltip placement="bottom">{t('nav.system')}</Tooltip>
      </div>
    {/if}

    <div class="flex md:order-2">
    <Button size="xs" class="ml-2" id="nav-btn-lang"><GlobeSolid/></Button>
    <Dropdown class="w-48 p-3 space-y-1">
      <li class="rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600">
        <Radio id="nav-btn-lang-en" bind:group={language} value={'en'}>{@html flagIcon('gb')} English</Radio>
      </li>
      <li class="rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600">
        <Radio id="nav-btn-lang-de" bind:group={language} value={'de'}>{@html flagIcon('de')} Deutsch</Radio>
      </li>
      <li class="rounded-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-600">
        <Radio id="nav-btn-lang-es" bind:group={language} value={'es'}>{@html flagIcon('es')} Español</Radio>
      </li>
    </Dropdown>
    <Tooltip placement="bottom" triggeredBy="#nav-btn-lang">{t('nav.lang')}</Tooltip>

    <DarkMode id="nav-btn-darkmode" size="sm" btnClass="{classBtnBase} px-4 py-2 ml-1 sm:ml-2"></DarkMode>
    <Tooltip placement="bottom">{t('nav.darkLight')}</Tooltip>

    <Button id="nav-btn-docs" size="xs" class="ml-1 sm:ml-2 max-[390px]:hidden {classBtnLink}"
      href="https://ansible-webui.OXL.app"><BookSolid /></Button>
    <Tooltip placement="bottom">{t('nav.docs')}</Tooltip>
    <Button id="nav-btn-repo" size="xs" class="ml-1 sm:ml-2 max-sm:hidden {classBtnLink}"
      href="https://github.com/O-X-L/ansible-webui"><GithubSolid /></Button>
    <Tooltip placement="bottom">{t('nav.repo')}</Tooltip>
    <Button id="nav-btn-bugs" size="xs" class="ml-1 sm:ml-2 max-sm:hidden {classBtnLink}"
      href="https://github.com/O-X-L/ansible-webui/issues"><BugSolid /></Button>
    <Tooltip placement="bottom">{t('nav.bugs')}</Tooltip>

    {#if $share.backend.authenticated}
      <Button id="nav-btn-user-settings" size="xs" class="ml-1 sm:ml-2 {classBtnLink}"
        on:click={() => {userSettingsOpen=true}}><UserSettingsSolid/></Button>
      <Tooltip placement="bottom">{t('nav.user_settings')}</Tooltip>

      <form method="post" action="/o/">
        <Button id="nav-btn-logout" size="xs" class="ml-1 sm:ml-2 h-full" type="submit"><LockSolid /></Button>
        <Tooltip placement="bottom">{t('nav.logout')}</Tooltip>
        {@html getCSRFFormTokenHTML()}
      </form>
    {/if}
    <!--
    <NavHamburger />
    -->
  </div>
</Navbar>

<UserSettings bind:open={userSettingsOpen} />
