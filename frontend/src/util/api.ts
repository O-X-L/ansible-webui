function getCookie(name: string) : string|null {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const CSRF_TOKEN = getCookie('csrftoken');
const API_HEADERS = {'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json'};
const API_RES_HEADER_HASH = 'X-Hash';

export async function apiGet(location: string, callback: CallableFunction) {
    const res = await fetch(`/api/${location}`, {method: 'GET', headers: API_HEADERS});
    if (res.status == 304) {
        callback(null, res.headers.get(API_RES_HEADER_HASH));
        return;
    }
    let data = null;
    try {
        data = await res.json();
    } catch {
        data = null;
    }
    callback(data, res.headers.get(API_RES_HEADER_HASH));
}

export async function apiGetMulti(locations: string[], callback: CallableFunction) {
    let fetches = [];
    for (let l of locations) {
        fetches.push(fetch(`/api/${l}`, {method: 'GET', headers: API_HEADERS}));
    }
    const res = await Promise.all(fetches);
    callback(await Promise.all(res.map(r => r.json())));
}

export async function apiEdit(method: string, location: string, payload: any, callback: CallableFunction) {
    let url = location;
    if (!url.includes('/api')) {
        url = `/api/${location}`
    }

    const res = await fetch(url, {
        method: method,
        headers: API_HEADERS,
        body: JSON.stringify(payload)
    });
    callback(res.status, await res.json());
}

export function getCSRFFormTokenHTML() : string {
    if (!CSRF_TOKEN) {
        console.log('WARNING: No CSRF Token available')
        return `<!-- no CSRF token (cookie) available -->`
    }
    return `<input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">`;
}

interface crsfTokenJSON {
    csrfmiddlewaretoken: string|null
}

export function getCSRFFormTokenJSON() : crsfTokenJSON {
    return {csrfmiddlewaretoken: CSRF_TOKEN};
}

export function formJSON(f: HTMLFormElement) : string {
    let raw = new FormData(f);
    let parsed = {};
    raw.forEach((value, key) => {
        parsed[key] = value;
    });
    return JSON.stringify(parsed);
}

export async function apiForm(e: SubmitEvent, callback: CallableFunction) : boolean {
    e.preventDefault();

    let payload = formJSON(e.target);
    let action = e.target.action;
    var method = e.target.method;

    apiEdit(method, action, payload, callback);
    return false;
}

// todo: fix that we are unable to pass a state (v).. maybe move it to a dedicated component?
export function showAPIErrors(status: number, json: any, v: string, scroll: boolean = false, element: string = '') {
    if (status != 200 || json.error !== undefined) {
        v = `${json.error} (${status})`;  // todo: pull language-code from api-error and show user the translation
        if (scroll) {
            let a = document.getElementById(element);
            if (a) {
                a.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
            }    
        }
    }
}