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

export function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function rsplit(s: string, w: string) {
  if (s === null) {
    return [null, null];
  }
  let b = s.split(w);
  if (b.length == 1) {
    return [b[0], null];
  }
  return [b.slice(0, -1).join(w), b.slice(-1)[0]];
}

export function isSet(data: any) {
  if (typeof(data) != 'undefined' && data != null && data != "") {
      return true;
  }
  return false;
}

export function escapeQuotes(data: string) {
  if (!isSet(data)) {
      return data;
  }
  data = data.replaceAll('"', '\x22');
  data = data.replaceAll('&', '&amp;');
  return data;
}
