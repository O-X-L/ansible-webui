import { writable } from 'svelte/store';

interface shareObject {
    backend: any,
}

export const share = writable({
    backend: {},
} as shareObject);