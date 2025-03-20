<script lang="ts">
    import { onMount } from 'svelte';

    import { Tabs, TabItem } from 'flowbite-svelte';
    import {
      CodeBranchSolid, CogSolid, BellActiveSolid, GridSolid, UsersSolid, BookOpenSolid,
    } from 'flowbite-svelte-icons'

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';

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

      let fragment = 'dashboard';
      if (openTab.jobs) {
        fragment = 'jobs';
      } else if (openTab.logs) {
        fragment = 'logs';
      } else if (openTab.repositories) {
        fragment = 'repositories';
      } else if (openTab.credentials) {
        fragment = 'credentials';
      } else if (openTab.alerts) {
        fragment = 'alerts';
      }

      window.location.hash = fragment;
    });

    function t(code: string) : string {
      return tq($share, code);
    }

    onMount(() => {
      // restore open tab from URL
      let f = window.location.hash;
      if (f.includes('?')) {
        f = f.split('?')[0];
      }

      if (f == '#jobs') {
        openTab.jobs = true;
      } else if (f == '#logs') {
        openTab.logs = true;
      } else if (f == '#repositories') {
        openTab.repositories = true;
      } else if (f == '#credentials') {
        openTab.credentials = true;
      } else if (f == '#alerts') {
        openTab.alerts = true;
      } else {
        openTab.dashboard = true;
      }
      loaded = true;
    })
</script>

<div class="pl-5 pr-5 h-full">
  <Tabs tabStyle="underline" contentClass="p-4 rounded-lg mt-4 mb-10 h-full">
    <TabItem bind:open={openTab.dashboard} divClass="h-full">
      <div slot="title" class="flex items-center gap-2">
        <GridSolid size="md" />
        {t('home.dashboard')}
      </div>
      <Dashboard bind:open={openTab.dashboard}/>
    </TabItem>

    <TabItem bind:open={openTab.jobs}>
      <div slot="title" class="flex items-center gap-2">
        <CogSolid size="md" />
        {t('home.jobs')}
      </div>
      <Jobs bind:open={openTab.jobs}/>
    </TabItem>

    <TabItem bind:open={openTab.logs}>
      <div slot="title" class="flex items-center gap-2">
        <BookOpenSolid size="md" />
        {t('home.logs')}
      </div>
      <Logs bind:open={openTab.logs}/>
    </TabItem>

    <TabItem bind:open={openTab.repositories}>
      <div slot="title" class="flex items-center gap-2">
        <CodeBranchSolid size="md" />
        {t('home.repos')}
      </div>
      <Repositories bind:open={openTab.repositories}/>
    </TabItem>

    <TabItem bind:open={openTab.credentials}>
      <div slot="title" class="flex items-center gap-2">
        <UsersSolid size="md" />
        {t('home.creds')}
      </div>
      <Credentials bind:open={openTab.credentials}/>
    </TabItem>

    <TabItem bind:open={openTab.alerts}>
      <div slot="title" class="flex items-center gap-2">
        <BellActiveSolid size="md" />
        {t('home.alerts')}
      </div>
      <Alerts bind:open={openTab.alerts}/>
    </TabItem>
  </Tabs>
</div>
