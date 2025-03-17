<script lang="ts">
    import { Tabs, TabItem } from 'flowbite-svelte';
    import { CodeBranchSolid, CogSolid, BellActiveSolid, GridSolid, UsersSolid } from 'flowbite-svelte-icons'

    import { share } from './State.js';
    import { tq } from '../util/translate.js';

    import Jobs from './sub/Jobs.svelte';
    import Alerts from './sub/Alerts.svelte';
    import Dashboard from './sub/Dashboard.svelte';
    import Repositories from './sub/Repositories.svelte';
    import Credentials from './sub/Credentials.svelte';

    function t(code: string) {
      return tq($share, code);
    }
</script>

<!-- todo: add #<title> to url when tabs open/close so the user can reload the page and directly get to the last open tab -->
<div class="pl-5 pr-5 h-full">
  <Tabs tabStyle="underline" contentClass="p-4 rounded-lg mt-4 mb-10 h-full">
    <TabItem open divClass="h-full">
      <div slot="title" class="flex items-center gap-2">
        <GridSolid size="md" />
        {t('home.dashboard')}
      </div>
      <Dashboard/>
    </TabItem>

    <TabItem>
      <div slot="title" class="flex items-center gap-2">
        <CogSolid size="md" />
        {t('home.jobs')}
      </div>
      <Jobs/>
    </TabItem>

    <TabItem>
      <div slot="title" class="flex items-center gap-2">
        <CodeBranchSolid size="md" />
        {t('home.repos')}
      </div>
      <Repositories/>
    </TabItem>

    <TabItem>
      <div slot="title" class="flex items-center gap-2">
        <UsersSolid size="md" />
        {t('home.creds')}
      </div>
      <Credentials/>
    </TabItem>

    <TabItem>
      <div slot="title" class="flex items-center gap-2">
        <BellActiveSolid size="md" />
        {t('home.alerts')}
      </div>
      <Alerts/>
    </TabItem>
  </Tabs>
</div>
