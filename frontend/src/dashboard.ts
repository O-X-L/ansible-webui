import { mount } from 'svelte';

import Dashboard from './base/Dashboard.svelte';

const dashboard = mount(Dashboard, {
  target: document.getElementById('dashboard'),
})

export default dashboard
