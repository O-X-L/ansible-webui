<script lang="ts">
    import {
        Heading, Spinner, 
    } from 'flowbite-svelte';

    import { share } from '../State.js';
    import { tq } from '../../util/translate.ts';

    function t(code: string) {
      return tq($share, code);
    }
</script>

<div class="text-center mt-20">
    <Spinner/>
</div>
