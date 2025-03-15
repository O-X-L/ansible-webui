<script lang="ts">
    import {
      Footer, FooterCopyright, FooterLinkGroup, Spinner, Tooltip, Button,
    } from 'flowbite-svelte';
    import { GithubSolid, BugSolid, BookSolid } from 'flowbite-svelte-icons';

    import { share } from './State.js';
    import { tq } from '../util/translate.js';
    import { classNavFooter } from './Style.js';

    function t(code: string) {
      return tq($share, code);
    }
</script>
  
<Footer class="fixed bottom-0 start-0 w-full flex flex-wrap items-center justify-between pt-2 pb-1 pl-5 pr-5 border-t {classNavFooter}">
  <FooterCopyright by="OXL" copyrightMessage="" />
  <FooterLinkGroup class="sm:hidden">
    <Button size="xs" class="ml-2" href="https://webui.ansibleguy.net"><BookSolid /></Button>
    <Tooltip placement="bottom">{t('nav.docs')}</Tooltip>
    <Button size="xs" class="ml-2" href="https://github.com/O-X-L/ansible-webui"><GithubSolid /></Button>
    <Tooltip placement="top">{t('nav.repo')}</Tooltip>
    <Button size="xs" class="ml-2" href="https://github.com/O-X-L/ansible-webui/issues"><BugSolid /></Button>
    <Tooltip placement="top">{t('nav.bugs')}</Tooltip>
  </FooterLinkGroup>
  <FooterLinkGroup class="text-sm text-gray-500 dark:text-gray-400">
    <div>
      {#if $share.backend.length == 0}
        <Spinner size="xs" />
      {:else}
        {#if $share.backend.authenticated}
        {t('footer.user')}: {$share.backend.user} |
        {/if}
        {t('footer.version')}: {$share.backend.version}
      {/if}
    </div>
  </FooterLinkGroup>
</Footer>
