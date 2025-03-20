import { mount } from 'svelte';

import System from './base/System.svelte';

const system = mount(System, {
  target: document.getElementById('system'),
})

export default system
