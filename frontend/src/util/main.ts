// source: https://github.com/bryc/code/blob/master/jshash/experimental/cyrb53.js
export function hashString(str: string, seed: number = 0) : number {
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

export function capitalize(s: string) : string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function rsplit(s: string, w: string) : [string|null, string|null] {
  if (s === null) {
    return [null, null];
  }
  let b = s.split(w);
  if (b.length == 1) {
    return [b[0], null];
  }
  return [b.slice(0, -1).join(w), b.slice(-1)[0]];
}

export function isSet(data: any) : boolean {
  if (typeof(data) != 'undefined' && data != null && data != "" && String(data).trim() != "") {
      return true;
  }
  return false;
}

export function escapeQuotes(data: string) : string {
  if (!isSet(data)) {
      return data;
  }
  data = data.replaceAll('"', '\x22');
  data = data.replaceAll('&', '&amp;');
  return data;
}

export function redirectTo(url: string) {
  window.location.replace(url);
  location.reload();
}

export function clickToCopy(event: MouseEvent) {
  navigator.clipboard.writeText(event.target.innerText);
}

export function saveToClipboard(o: any) {
  navigator.clipboard.writeText(JSON.stringify(o, null, 2));
}

export function getURLHash() : string {
  let f = window.location.hash;
  if (f.includes('?')) {
    f = f.split('?')[0];
  }
  f = f.trim();
  f = f.replace('#', '');
  return f;
}

export function getURLHashPage() : string {
  let f = getURLHash();
  return f.split('-')[0];
}

export function getURLHashParams() : any {
  let params = {};
  let f = getURLHash();
  let params_arr = f.split('-');
  if (params_arr.length > 1) {
    params_arr = params_arr.slice(1);
  }
  for (let p of params_arr) {
    if (p.includes('=')) {
      let pp = p.split('=');
      params[pp[0]] = pp[1];
    }
  }
  return params;
}

export function arraysEqual(a: any[], b: any[]) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length !== b.length) return false;

  // If you don't care about the order of the elements inside
  // the array, you should sort both arrays here.
  // Please note that calling sort on an array will modify that array.
  // you might want to clone your array first.

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}
