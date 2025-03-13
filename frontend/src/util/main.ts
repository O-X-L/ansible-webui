// source: https://github.com/bryc/code/blob/master/jshash/experimental/cyrb53.js
export function hashString(str: string, seed: number = 0) {
  let h1 = 0xdeadbeef ^ seed,
    h2 = 0x41c6ce57 ^ seed;
  for (let i = 0, ch; i < str.length; i++) {
    ch = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
  h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
  h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);

  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
}
  
export async function apiGet(location: string, callback: CallableFunction) {
  const res = await fetch(`/api/${location}`, {method: 'GET'});
  callback(await res.json());
}

export async function apiGetMulti(locations: string[], callback: CallableFunction) {
  let fetches = [];
  for (let l of locations) {
    fetches.push(fetch(`/api/${l}`, {method: 'GET'}));
  }
  const res = await Promise.all(fetches);
  callback(await Promise.all(res.map(r => r.json())));
}

export async function apiEdit(method: string, location: string, payload: any, callback: CallableFunction) {
  const res = await fetch(`/api/${location}`, {
    method: method,
    body: JSON.stringify(payload)
  });
  callback(res.status, await res.json());
}


export function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}