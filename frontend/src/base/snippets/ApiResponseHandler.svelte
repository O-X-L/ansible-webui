<script lang="ts">
    import { slide } from 'svelte/transition';

    import { Alert } from 'flowbite-svelte';
    import { CloseCircleSolid, InfoCircleSolid, ExclamationCircleSolid } from 'flowbite-svelte-icons';

    import { share } from '../Share.js';
    import { tq, tqSub } from '../../util/translate.js';
    import { API_STATUS_CODES_OK } from '../Config.js';

    let {
        showError = $bindable(false),
        errorMsg = $bindable(''),
        showSuccess = $bindable(false),
        successMsg = $bindable(''),
        // showWarning = $bindable(false),
        warningMsgs = $bindable([]),
    } = $props();

    // const scrollToDiv = `api-response-${Date.now()}`;
    const classAlert = 'text-wrap mb-5 mt-2 absolute right-5 top-20 z-100 bg-opacity-70';
    const timeoutSuccess = 5000;
    const timeoutError = 15000;

    let errorMsgTranslated = $state('');
    let successMsgTranslated = $state('');
    let warningMsgsTranslated: string[] = $state([]);
    let showWarning = $derived(warningMsgsTranslated.length > 0);

    function t(code: string) : string {
        return tq($share, code);
    }

    function tSub(s: string) : string {
        return tqSub($share, s);
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
        // todo: api-error translations and show user the translation
        if (!errorMsg && !successMsg && !warningMsgs.length) {
            return;
        }

        errorMsgTranslated = tSub(t(errorMsg));
        successMsgTranslated = tSub(t(successMsg));
        let warnings = []
        for (let w of warningMsgs) {
            warnings.push(tSub(t(w)));
        }
        warningMsgsTranslated = warnings;
    })

    $effect(() => {
        if (!showError && !showSuccess && !showWarning) {
            return;
        }

        setTimeout(() => {
            if (showError && errorMsgTranslated) {
                console.log("ERROR:", errorMsgTranslated);
            }
            [showError, showSuccess] = [false, false];
            successMsg = '';
            errorMsg = '';
            warningMsgs = [];
            warningMsgsTranslated = [];
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
{#if showWarning}
    {#each warningMsgsTranslated as m}
        <div transition:slide>
            <Alert border color="yellow" class={classAlert} dismissable={true}>
                <ExclamationCircleSolid slot="icon" class="w-5 h-5" /> {m}
            </Alert>
        </div>
    {/each}
{/if}