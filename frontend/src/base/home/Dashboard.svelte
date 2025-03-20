<script lang="ts">
    import {
        Spinner, 
    } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';

    let { open = $bindable(false) } = $props();

    function t(code: string) : string {
      return tq($share, code);
    }
</script>

<div class="text-center mt-20">
    <Spinner/>
</div>

<!--
    IDEAS:
        * stats of failed jobs (for all readable - user can narrow it down to single jobs)
        * stats of changed items
        * stats per host (allow user to select single host)
          * changed items
          * when did which playbook target the host; who executed it
-->
