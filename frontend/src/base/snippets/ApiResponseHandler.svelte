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

    const scrollToDiv = `api-response-${Date.now()}`;
    const timeoutSuccess = 5000;
    const timeoutError = 15000;

    let errorMsgTranslated = $state('');
    let successMsgTranslated = $state('');

    function t(code: string) {
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
        errorMsgTranslated = t(errorMsg);
        successMsgTranslated = t(successMsg);
    })

    $effect(() => {
        if (!showError && !showSuccess) {
            return;
        }

        let a = document.getElementById(scrollToDiv);
        if (a) {
            a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            setTimeout(() => {
                [showError, showSuccess] = [false, false];
                successMsg = '';
                errorMsg = '';
            }, showSuccess ? timeoutSuccess : timeoutError);
        }
    })
</script>


<div id={scrollToDiv} class="h-0"></div>
{#if showError}
    <div transition:slide>
        <Alert border color="red" class="text-wrap mb-5 mt-2">
            <CloseCircleSolid slot="icon" class="w-5 h-5" /> {errorMsgTranslated}
        </Alert>
    </div>
{/if}
{#if showSuccess}
    <div transition:slide>
        <Alert border color="green" class="text-wrap mb-5 mt-2">
            <InfoCircleSolid slot="icon" class="w-5 h-5" /> {successMsgTranslated}
        </Alert>
    </div>
{/if}
