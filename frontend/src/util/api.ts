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
const API_HEADERS = {'X-CSRFToken': CSRF_TOKEN};

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
    const res = await fetch(`/api/${location}`, {
        method: method,
        headers: API_HEADERS,
        body: JSON.stringify(payload)
    });
    callback(res.status, await res.json());
}

export function getCSRFFormToken() {
    return `<input type="hidden" name="csrfmiddlewaretoken" value="${CSRF_TOKEN}">`;
}