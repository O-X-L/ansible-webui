<script lang="ts">
    import {
      Footer, FooterCopyright, FooterLinkGroup, Spinner, Tooltip, Button,
    } from 'flowbite-svelte';
    import { GithubSolid, BugSolid, BookSolid } from 'flowbite-svelte-icons';

    import { share } from './State.svelte.ts';
    import { classLinkHover, navFooterClass } from './Style.ts';
</script>
  
<Footer class="fixed bottom-0 start-0 w-full flex flex-wrap items-center justify-between pt-2 pb-1 pl-5 pr-5 border-t {navFooterClass}">
  <FooterCopyright by="OXL" aClass={classLinkHover} copyrightMessage="" />
  <FooterLinkGroup class="sm:hidden">
    <Button size="xs" class="ml-2" href="https://webui.ansibleguy.net"><BookSolid /></Button>
    <Tooltip placement="bottom">Documentation</Tooltip>
    <Button size="xs" class="ml-2" href="https://github.com/O-X-L/ansible-webui"><GithubSolid /></Button>
    <Tooltip placement="top">Open Source Repository</Tooltip>
    <Button size="xs" class="ml-2" href="https://github.com/O-X-L/ansible-webui/issues"><BugSolid /></Button>
    <Tooltip placement="top">Report Bugs</Tooltip>
  </FooterLinkGroup>
  <FooterLinkGroup class="text-sm text-gray-900 dark:text-gray-400">
    <div>
      {#if $share.backend.length == 0}
        <Spinner size="xs" />
      {:else}
        {#if $share.backend.authenticated}
         User: {$share.backend.user} |
        {/if}
        Version: {$share.backend.version}
      {/if}
    </div>
  </FooterLinkGroup>
</Footer>
