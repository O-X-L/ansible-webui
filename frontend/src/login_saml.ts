import { mount } from 'svelte';

import Login from './base/LoginSAML.svelte';

const login = mount(Login, {
  target: document.getElementById('login-saml'),
})

export default login
