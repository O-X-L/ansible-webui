<script lang="ts">
    import { slide } from 'svelte/transition';

    import { share } from '../State.js';
    import { Alert } from 'flowbite-svelte';
    import { tq } from '../../util/translate.js';
    import { API_STATUS_CODES_OK } from '../sub/Config.js';
    import { CloseCircleSolid, InfoCircleSolid } from 'flowbite-svelte-icons';

    let {
        showError = $bindable(false),
        errorMsg = $bindable(''),
        showSuccess = $bindable(false),
        successMsg = $bindable(''),
    } = $props();

    // const scrollToDiv = `api-response-${Date.now()}`;
    const classAlert = 'text-wrap mb-5 mt-2 absolute right-5 top-20 z-100 bg-opacity-70';
    const timeoutSuccess = 5000;
    const timeoutError = 15000;

    let errorMsgTranslated = $state('');
    let successMsgTranslated = $state('');

    function t(code: string) : string {
      return tq($share, code);
    }

    export function handleRes(s: number, j: any) {
        console.log("RESPONSE", s, j);
        if (!API_STATUS_CODES_OK.includes(s) || j.error !== undefined) {
            if (!errorMsg) {
                errorMsg = `${j.error} (${s})`;
            }
            showError = true;

        } else {
            if (!successMsg) {
                successMsg = t('common.success');
            }
            showSuccess = true;
        }
    }

    $effect(() => {
        // if we set a language-code as error/success message - we want to translate it
        // todo: pull language-code from api-error and show user the translation
        if (!errorMsg && !successMsg) {
            return;
        }

        errorMsgTranslated = t(errorMsg);
        successMsgTranslated = t(successMsg);
    })

    $effect(() => {
        if (!showError && !showSuccess) {
            return;
        }

        setTimeout(() => {
            if (showError && errorMsgTranslated) {
                console.log("ERROR:", errorMsgTranslated);
            }
            [showError, showSuccess] = [false, false];
            successMsg = '';
            errorMsg = '';
        }, showSuccess ? timeoutSuccess : timeoutError);
    })
</script>

{#if showError}
    <div transition:slide>
        <Alert border color="red" class={classAlert} dismissable={true}>
            <CloseCircleSolid slot="icon" class="w-5 h-5" /> {errorMsgTranslated}
        </Alert>
    </div>
{/if}
{#if showSuccess}
    <div transition:slide>
        <Alert border color="green" class={classAlert} dismissable={true}>
            <InfoCircleSolid slot="icon" class="w-5 h-5" /> {successMsgTranslated}
        </Alert>
    </div>
{/if}
