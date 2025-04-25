<script lang="ts">
    import { onMount } from 'svelte';

    import { Tabs, TabItem } from 'flowbite-svelte';
    import {
      CodeBranchSolid, CogSolid, BellActiveSolid, GridSolid, UsersSolid, BookOpenSolid,
    } from 'flowbite-svelte-icons'

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';
    import { getURLHashPage } from '../util/main.js';
    import { classTabButton, classTabTitle, classTab, classTabDiv, classTabButtonDiv } from './Style.js';

    import Jobs from './home/Jobs.svelte';
    import Logs from './home/Logs.svelte';
    import Alerts from './home/Alerts.svelte';
    import Dashboard from './home/Dashboard.svelte';
    import Repositories from './home/Repositories.svelte';
    import Credentials from './home/Credentials.svelte';

    let loaded = $state(false);
    let openTab = $state({
      dashboard: false,
      jobs: false,
      logs: false,
      repositories: false,
      credentials: false,
      alerts: false,
    });
  
    $effect(() => {
      // save open tab to URL
      if (!loaded) {
        return;
      }

      let f = 'dashboard';
      if (openTab.jobs) {
        f = 'jobs';
      } else if (openTab.logs) {
        f = 'logs';
      } else if (openTab.repositories) {
        f = 'repositories';
      } else if (openTab.credentials) {
        f = 'credentials';
      } else if (openTab.alerts) {
        f = 'alerts';
      }

      let fn = getURLHashPage();
      if (f != fn) {
        window.location.hash = f;
      }
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    onMount(() => {
      // restore open tab from URL
      let f = getURLHashPage();

      if (f == 'jobs') {
        openTab.jobs = true;
      } else if (f == 'logs') {
        openTab.logs = true;
      } else if (f == 'repositories') {
        openTab.repositories = true;
      } else if (f == 'credentials') {
        openTab.credentials = true;
      } else if (f == 'alerts') {
        openTab.alerts = true;
      } else {
        openTab.dashboard = true;
      }
      loaded = true;
    })
</script>

<div class={classTab}>
  <Tabs tabStyle="underline" contentClass={classTabDiv} defaultClass={classTabButtonDiv}>
    <TabItem bind:open={openTab.dashboard} divClass="h-full" defaultClass="{classTabButton} tab-dashboard">
      <div slot="title" class="flex items-center sm:gap-2">
        <GridSolid size="md" /> {t('home.dashboard')}
      </div>
      <Dashboard bind:open={openTab.dashboard}/>
    </TabItem>

    <TabItem bind:open={openTab.jobs} defaultClass="{classTabButton} tab-jobs">
      <div slot="title" class="{classTabTitle} gap-1">
        <CogSolid size="md" /> {t('home.jobs')}
      </div>
      <Jobs bind:open={openTab.jobs}/>
    </TabItem>

    <TabItem bind:open={openTab.logs} defaultClass="{classTabButton} tab-logs">
      <div slot="title" class={classTabTitle}>
        <BookOpenSolid size="md" /> {t('home.logs')}
      </div>
      <Logs bind:open={openTab.logs}/>
    </TabItem>

    <TabItem bind:open={openTab.repositories} defaultClass="{classTabButton} tab-repositories">
      <div slot="title" class={classTabTitle}>
        <CodeBranchSolid size="md" /> {t('home.repos')}
      </div>
      <Repositories bind:open={openTab.repositories}/>
    </TabItem>

    <TabItem bind:open={openTab.credentials} defaultClass="{classTabButton} tab-credentials">
      <div slot="title" class={classTabTitle}>
        <UsersSolid size="md" /> {t('home.creds')}
      </div>
      <Credentials bind:open={openTab.credentials}/>
    </TabItem>

    <TabItem bind:open={openTab.alerts} defaultClass="{classTabButton} tab-alerts">
      <div slot="title" class={classTabTitle}>
        <BellActiveSolid size="md" /> {t('home.alerts')}
      </div>
      <Alerts bind:open={openTab.alerts}/>
    </TabItem>
  </Tabs>
</div>
