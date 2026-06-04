<script lang="ts">
    import { FloppyDiskSolid } from 'flowbite-svelte-icons';
    import {
        Button, Tooltip, Heading, Label, Input,  // Modal
    } from 'flowbite-svelte';

    import Modal from '../../flowbite-custom/Modal.svelte';

    import { share } from '../Share.js';
    import { apiEdit } from '../../util/api.js';
    import { tq } from '../../util/translate.js';
    import APIResponseHandler from '../snippets/ApiResponseHandler.svelte';
    import {
        classModalBackdrop, classModalLabel, classModalForm, classModalInput, classModalBtns,
        classModalBody, classModalDialog,
     } from '../Style.js';
 
    let { open = $bindable(false) } = $props();

    const REGEX_SPECIAL_CHARS = /^.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?].*$/
    const REGEX_LETTERS = /^.*[a-zA-Z].*$/
    const REGEX_DIGITS = /^.*[0-9].*$/

    let apiResponseHandler: APIResponseHandler = $state();
    let apiSuccessMsg = $state('');
    let apiErrorMsg = $state('');
    let showError = $state(false);
    let settings = $state({
        password: '',
        password_valid: true,
    });

    function t(code: string) : string {
        return tq($share, code);
    }

    function handleSubmitResponse(s: number, j: any) {
        if (s == 200 && j.error === undefined) {
            setTimeout(logoutUser, 3500);
            open = false;
        }
        apiResponseHandler.handleRes(s, j);
    }

    function logoutUser() {
        apiEdit('post', '/o/', null, handleSubmitResponse);
        location.replace('/a/login');
    }

    function changePassword() {
        let p = settings.password;
        if (p.trim() == '' || p.length < 10 ||
            !REGEX_SPECIAL_CHARS.test(p) || !REGEX_LETTERS.test(p) || !REGEX_DIGITS.test(p)) {
            settings.password_valid = false;
            apiErrorMsg = t('common.invalid_form');
            showError = true;
            return;
        }
        settings.password_valid = true;
        showError = false;
        apiErrorMsg = '';
        apiSuccessMsg = 'user_settings.action.pwd_change';
        apiEdit('put', 'user/password', {password: p}, handleSubmitResponse);
    }
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg}
    bind:errorMsg={apiErrorMsg} bind:showError={showError} />

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center"
    backdropClass={classModalBackdrop} bodyClass={classModalBody} dialogClass={classModalDialog}>
    <div class={classModalForm}>
        <Heading tag="h2">{t('nav.user_settings')}</Heading>


        <div class={classModalInput}>
            <Label for="user_pwd" class={classModalLabel}>{t('user_settings.form.pwd')}</Label>
            <Input id="user_pwd" bind:value={settings.password} type="password"
                color={settings.password_valid ? 'base' : 'red'}/>
            <Tooltip>{t('user_settings.form.help.pwd')}</Tooltip>
        </div>
        <div class={classModalBtns}>
            <Button type="button" on:click={changePassword}><FloppyDiskSolid/></Button>
            <Tooltip>{t('user_settings.btn.change_pwd')}</Tooltip>
        </div>
    </div>
</Modal>
