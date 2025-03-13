import { mount } from 'svelte';

import Head from './base/Head.svelte';
//import Nav from './base/Nav.svelte';
//import Footer from './base/Footer.svelte';

import Index from './base/Index.svelte';

const head = mount(Head, {
  target: document.getElementsByTagName('head')[0],
  props: { title: 'Ansible WebUI' },
})
/*
const nav = mount(Nav, {
  target: document.getElementById('nav'),
})
*/
const index = mount(Index, {
  target: document.getElementById('main'),
})
/*
const footer = mount(Footer, {
  target: document.getElementById('footer'),
})
*/

export default index
