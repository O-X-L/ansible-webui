<script lang="ts">
    import { onMount } from 'svelte';

    import { Button, Alert } from 'flowbite-svelte';

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';
    import { classBtnLink, classFooterSpacing } from './Style.js';

    const LOGIN_URL_DEFAULT = '/a/login/';
    const LOGIN_URL_FALLBACK = '/a/login/fallback/';

    interface formAlertType {
        color: 'red'|'yellow'|'green',
        msg: string,
    }

    let alerts: formAlertType[] = $state([]);

    function t(code: string) : string {
        return tq($share, code);
    }

    function showBackendFormErrors() {
      let errors = document.querySelectorAll('.aw-backend-form-alert');
      if (errors) {
        for (let e of errors) {
          if (e.field) {
            alerts.push({
              color: 'red',
              msg: e.innerText,
            })
          } else {
            alerts.push({
              color: 'red',
              msg: e.innerText,
            })
          }
        }
      }
    }

    onMount(() => {
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
      <Alert color={alert.color||"red"} class="mx-20 mt-5">
        {#each alerts as alert}
          <div>{alert.msg}</div>
        {/each}
      </Alert>
  </div>
{/if}


<div class="flex justify-center w-full">
    <div>
      <Button href={LOGIN_URL_DEFAULT} class="mt-5 {classBtnLink}">{t('login.sso')}</Button>
    </div>
    <div>
      <Button href={LOGIN_URL_FALLBACK} class="ml-2 mt-5 {classBtnLink}">{t('login.localUser')}</Button>
    </div>
</div>

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
