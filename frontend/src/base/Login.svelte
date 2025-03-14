<script lang="ts">
    import { onMount } from 'svelte';

    import { Input, Label, Button, Spinner, Toggle } from 'flowbite-svelte';

    import { share } from './State.svelte.ts';
    import { getCSRFFormToken } from '../util/api.ts';

    let loaded = $state(false);
    let loginTarget = $derived($share.backend.sso ? '/a/saml/init/' : '/a/login/')
    let rememberUsername = $state(false);

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

    onMount(() => {
        restoreUsername();
    });
</script>

<div class="flex justify-center w-full">
    <div class="w-52 h-52 mt-6 mb-14">
        <img loading="lazy" src="{$share.backend.logo}" alt="LOGO" referrerpolicy="no-referrer">
    </div>
</div>

<div class="flex justify-center w-full">
    <div>
        {#if $share.backend.length == 0}
            <Spinner />
        {:else}
            <form method="post" action="{loginTarget}">
                {@html getCSRFFormToken()}

                <Label for="id_username">Username</Label>
                <Input type="text" id="id_username" name="username" oninput={saveUsername}/>

                {#if !($share.backend.sso) || window.location.includes('fallback')}
                    <Label for="id_password" class="mt-2">Password</Label>
                    <Input type="password" name="password" id="id_password"/>
                {/if}

                <Toggle bind:checked={rememberUsername} class="mt-2">Save Username</Toggle>

                <div class="flex justify-center w-full">
                    <div>
                        <Button type="submit" class="mt-5">Login</Button>
                    </div>
                    {#if $share.backend.sso}
                        <div>
                            {#if window.location.includes('fallback')}
                                <Button href="/a/login/" class="mt-2">SSO</Button>
                            {:else}
                                <Button href="/a/login/fallback/" class="mt-2">Local User</Button>
                            {/if}
                        </div>
                    {/if}
                </div>
            </form>
        {/if}
    </div>
</div>

<!--
<div align="center" style="display: block;">
    <img loading="lazy" src="{% get_logo %}" alt="LOGO" onerror="this.style.display='none'" class="aw-img-float" referrerpolicy="no-referrer">
</div>

    <form class="aw-login-form" method="post" action="{% url 'login' %}">
        {% csrf_token %}
        <label for="id_username" class="aw-login-fields">
            Username:
            <input class="aw-login-fields form-control" type="text" name="username" autofocus="" autocapitalize="none" autocomplete="username" maxlength="150" required="" id="id_username">
        </label>
        <br>
        <label for="id_password" class="aw-login-fields">
            Password:
            <input class="aw-login-fields form-control" type="password" name="password" autocomplete="current-password" required="" id="id_password">
        </label>
        <div class="form-check">
        <input class="form-check-input" type='checkbox' id="aw-login-remember">
        <label class="form-check-label" for="aw-login-remember">
            Save Username
        </label>
        </div>
        <div class="aw-login-btn">
            <button type="submit" value="login" class="btn btn-secondary">Login</button>
            {% if ''|auth_sso %}
                <a href="{% url 'login_sso' %}">
                    <button type="button" class="btn btn-primary">SSO</button>
                </a>
            {% endif %}
        </div>
    </form>
-->