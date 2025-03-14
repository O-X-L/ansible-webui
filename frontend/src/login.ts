import { mount } from 'svelte';

import Login from './base/Login.svelte';

const login = mount(Login, {
  target: document.getElementById('login'),
})

export default login
