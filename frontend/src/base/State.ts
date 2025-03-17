import { writable } from 'svelte/store';

interface shareObject {
    backend: any,
    lang: any,
    updateInterval: number,
}

export const share = writable({
    backend: {},
    lang: {},
    updateInterval: 1000,
} as shareObject);