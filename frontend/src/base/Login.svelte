<script lang="ts">
    import { onMount } from 'svelte';

    import { Input, Label, Button, Spinner, Toggle, Alert } from 'flowbite-svelte';

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';
    import { getCSRFFormTokenHTML } from '../util/api.js';

    let loaded = $state(false);
    let loginTarget = $derived($share.backend.sso ? '/a/saml/init/' : '/a/login/')
    let rememberUsername = $state(false);

    interface formAlertType {
        color: 'red'|'yellow'|'green',
        title: string,
        msg: string,
    }

    let alerts: formAlertType[] = $state([]);

    function t(code: string) : string {
      return tq($share, code);
    }

    function saveUsername() {
        if (!rememberUsername) {
            return;
        }
        let usernameField = document.getElementById('id_username');
        if (usernameField) {
            localStorage.login_username = usernameField.value;
        }
    }

    $effect(() => {
        if (!loaded) {
            return;
        }
        localStorage.login_remember = rememberUsername ? '1' : '0';
        if (!rememberUsername) {
            localStorage.login_username = '';
        } else {
            saveUsername();
        }
    });

    function restoreUsername() {
        if (localStorage.login_remember == '1') {
            rememberUsername = true;
            let usernameField = document.getElementById("id_username");
            if (usernameField && localStorage.login_username) {
                usernameField.value = localStorage.login_username;
            }
        }
        loaded = true;
    }

    function showBackendFormErrors() {
      let errors = document.querySelectorAll('.aw-backend-form-alert');
      if (errors) {
        for (let e of errors) {
          if (e.field) {
            alerts.push({
              color: 'red',
              title: `${t('common.invalid_value')}: "${e.field}"`,
              msg: e.innerText,
            })
          } else {
            alerts.push({
              color: 'red',
              title: t('common.invalid_form'),
              msg: e.innerText,
            })
          }
        }
      }
    }

    onMount(() => {
        restoreUsername();
        showBackendFormErrors();
    });
</script>

<div class="flex justify-center w-full">
    <div class="w-52 h-52 mt-6 mb-14">
        <img loading="lazy" src="{$share.backend.logo}" alt="LOGO" referrerpolicy="no-referrer">
    </div>
</div>

{#if alerts.length}
  <div class="my-5">
    {#each alerts as alert}
      <Alert color={alert.color||"red"} class="mx-20">
        <div class="font-bold">{alert.title}</div>
        <div>{alert.msg}</div>
      </Alert>
    {/each}
  </div>
{/if}


<div class="flex justify-center w-full">
    <div>
        {#if !$share.backend}
            <Spinner />
        {:else}
            <form method="post" action="{loginTarget}">
                {@html getCSRFFormTokenHTML()}

                <Label for="id_username">{t('login.user')}</Label>
                <Input type="text" id="id_username" name="username" oninput={saveUsername}/>

                {#if !$share.backend.sso || window.location.pathname.includes('fallback')}
                    <Label for="id_password" class="mt-2">{t('login.pwd')}</Label>
                    <Input type="password" name="password" id="id_password"/>
                {/if}

                <Toggle bind:checked={rememberUsername} class="mt-2">{t('login.saveUser')}</Toggle>

                <div class="flex justify-center w-full">
                    <div>
                        <Button type="submit" class="mt-5">{t('login.btn')}</Button>
                    </div>
                    {#if $share.backend.sso}
                        <div>
                            {#if window.location.pathname.includes('fallback')}
                                <Button href="/a/login/" class="mt-2">{t('login.sso')}</Button>
                            {:else}
                                <Button href="/a/login/fallback/" class="mt-2">{t('login.localUser')}</Button>
                            {/if}
                        </div>
                    {/if}
                </div>
            </form>
        {/if}
    </div>
</div>
