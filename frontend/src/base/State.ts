import { writable } from 'svelte/store';

interface shareObject {
    backend: any,
    lang: any,
}

export const share = writable({
    backend: {},
    lang: {},
} as shareObject);