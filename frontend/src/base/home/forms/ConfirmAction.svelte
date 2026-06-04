<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        CloseCircleSolid, TrashBinSolid, StopSolid,
    } from 'flowbite-svelte-icons';
    import {
        Button, Tooltip, Heading,
    } from 'flowbite-svelte';

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import {
        classModalBackdrop, classModalBody, classModalForm, classModalBtns, classModalDialog,
    } from '../../Style.js';
 
    let componentRoot;
    let {
        open = $bindable(false),
        action = $bindable('btn.delete'),
        confirmed = $bindable(false),
        confirmText = $bindable(''),
    } : {
        open: boolean,
        action: string,
        confirmed: boolean,
        confirmText: string,
    } = $props();

    function t(code: string) : string {
        return tq($share, code);
    }

    function confirm() {
        confirmed = true;
        open = false;
    }

    function cancel() {
        confirmed = false;
        open = false;
    }

    function reset() {
        confirmed = false;
    }

    $effect(() => {
        if (open) {
            reset();
        }
    });

    function handleKeyDown(e: KeyboardEvent) {
        switch (e.key) {
        case 'Enter':
            confirm();
        default:
            return;
        }
    }

    $effect(() => {
        if (open && componentRoot) {
            componentRoot.focus();
        }
    });

    onMount(() => {
        if (componentRoot) {
            componentRoot.addEventListener('keydown', handleKeyDown);
        }
    });

    onDestroy(()=>{
        if (componentRoot) {
            componentRoot.removeEventListener('keydown', handleKeyDown);
        }
    });

</script>

<div bind:this={componentRoot} tabindex="-1" class="inline-block"></div>
<Modal bind:open={open} size="xs" autoclose={false} placement="middle-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('prompt.confirm')} {t(action)}</Heading>
        <div class="font-bold my-5">
            {t(action)}: {confirmText}
        </div>
        <div class={classModalBtns}>
            <Button id="confirm-prompt-btn-confirm" on:click={confirm} class="inline-block ml-2">
                {#if action == 'btn.stop'}
                    <StopSolid />
                {:else}
                    <TrashBinSolid/>
                {/if}
            </Button>
            <Tooltip>{t(action)}</Tooltip>

            <Button id="confirm-prompt-btn-cancel" on:click={cancel} class="inline-block ml-2">
                <CloseCircleSolid/>
            </Button>
            <Tooltip>{t('btn.close')}</Tooltip>
        </div>
    </div>
</Modal>