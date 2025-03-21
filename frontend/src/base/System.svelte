<script lang="ts">
    import { onMount } from 'svelte';

    import { Tabs, TabItem } from 'flowbite-svelte';
    import { AdjustmentsHorizontalSolid, RocketSolid, DatabaseSolid, BookSolid } from 'flowbite-svelte-icons'

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';

    import Settings from './system/Settings.svelte';
    import APIKeys from './system/APIKeys.svelte';

    const classIFrameDiv = 'w-full h-full';
    const classIFrame = 'w-full h-full overflow-y-auto overflow-x-hidden border-none';

    let loaded = $state(false);
    let openTab = $state({
      settings: false,
      api_keys: false,
      api_docs: false,
      admin: false,
    });
  
    $effect(() => {
      // save open tab to URL
      if (!loaded) {
        return;
      }

      let fragment = 'settings';
      if (openTab.api_keys) {
        fragment = 'api_keys';
      } else if (openTab.api_keys) {
        fragment = 'admin';
      } else if (openTab.api_keys) {
        fragment = 'api_docs';
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

      if (f == '#api_keys') {
        openTab.api_keys = true;
      } else if (f == '#admin') {
        openTab.api_keys = true;
      } else if (f == '#api_docs') {
        openTab.api_keys = true;
      } else {
        openTab.settings = true;
      }
      loaded = true;
    })
</script>

<div class="pl-5 pr-5 h-full">
  <Tabs tabStyle="underline" contentClass="p-4 rounded-lg mt-4 mb-10 h-full">
    <TabItem bind:open={openTab.settings} divClass="h-full">
      <div slot="title" class="flex items-center gap-2">
        <AdjustmentsHorizontalSolid size="md" /> {t('system.settings')}
      </div>
      <Settings bind:open={openTab.settings}/>
    </TabItem>

    <TabItem bind:open={openTab.admin} divClass={classIFrameDiv}>
      <div slot="title" class="flex items-center gap-2">
        <DatabaseSolid size="md" /> {t('system.admin')}
      </div>
      <iframe src="/_admin/" title="Admin" class={classIFrame}
        frameborder=0 marginheight=0 marginwidth=0></iframe>
    </TabItem>

    <TabItem bind:open={openTab.api_keys}>
      <div slot="title" class="flex items-center gap-2">
        <RocketSolid size="md" /> {t('system.api_keys')}
      </div>
      <APIKeys bind:open={openTab.api_keys}/>
    </TabItem>

    <TabItem bind:open={openTab.api_docs} divClass={classIFrameDiv}>
      <div slot="title" class="flex items-center gap-2">
        <BookSolid size="md" /> {t('system.api_docs')}
      </div>
      <iframe src="/api/_docs" title="API Docs" class={classIFrame}
        frameborder=0 marginheight=0 marginwidth=0></iframe>
    </TabItem>
  </Tabs>
</div>
