<script lang="ts">
    import { Spinner, Button } from 'flowbite-svelte';

    import { share } from '../State.js';
    import JobForm from './JobForm.svelte';
    import { tq } from '../../util/translate.js';

    let addModal = $state(false);
    let addModalId = $state(Date.now());

    function t(code: string) {
      return tq($share, code);
    }
</script>

<div class="flex justify-between">
    <div></div>
    <div>
        <Button on:click={() => {addModalId = Date.now(); addModal = true}}>{t('btn.add')}</Button>
    </div>    
</div>

<div class="text-center mt-20">
    <Spinner/>
</div>

{#key addModalId}
    <JobForm bind:open={addModal} action='add' ></JobForm>
{/key}
