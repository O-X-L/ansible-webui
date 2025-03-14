import { mount } from 'svelte';

import Home from './base/Home.svelte';

const home = mount(Home, {
  target: document.getElementById('home'),
})

export default home
