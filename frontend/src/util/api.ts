function getCookie(name: string) {
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

export async function apiGet(location: string, callback: CallableFunction) {
    const res = await fetch(`/api/${location}`, {method: 'GET', headers: API_HEADERS});
    callback(await res.json());
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
    if (!url.includes('/')) {
        url = `/api/${location}`
    }

    const res = await fetch(url, {
        method: method,
        headers: API_HEADERS,
        body: JSON.stringify(payload)
    });
    callback(res.status, await res.json());
}

export function getCSRFFormToken() {
    return `<input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">`;
}

export function formJSON(f: HTMLFormElement) {
    let raw = new FormData(f);
    let parsed = {};
    raw.forEach((value, key) => {
        parsed[key] = value;
    });
    return JSON.stringify(parsed);
}

export async function apiForm(e: SubmitEvent, callback: CallableFunction) {
    e.preventDefault();

    let payload = formJSON(e.target);
    let action = e.target.action;
    var method = e.target.method;

    apiEdit(method, action, payload, callback);
    return false;
}