import { writable } from 'svelte/store';

interface backendInfos {
    authenticated: boolean,
    sso: boolean,
    user: null|string,
    user_id: null|number,
    version: string,
    logo: string,
}

interface shareObject {
    backend: backendInfos,
    lang: any,
    updateInterval: number,
}

export const share = writable({
    backend: {},
    lang: {},
    updateInterval: 1000,
} as shareObject);
