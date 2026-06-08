const DEFAULT_LANG = 'en'
export const TT = '%t%'

let localCache: any = null; 

export function getTranslationStore(share: any) : any|null {
  if (share.lang[DEFAULT_LANG]) {
    return share.lang;
  }
  if (localCache) {
    return localCache;
  }
  if (localStorage.languageCache) {
    localCache = JSON.parse(localStorage.languageCache);
    return localCache;
  }
  return null;
}

function getTranslations(share: any) : any|null {
  let userLang = localStorage.language;
  let store = getTranslationStore(share);
  if (!store) {
    return null
  }
  if (!userLang || !store[userLang]) {
    if (!store[DEFAULT_LANG]) {
      return null;
    } else {
      return store[DEFAULT_LANG];
    }
  }
  return store[userLang];
}

export function tq(share: any, code: string) : string {
  if (typeof(code) != 'string') {
    console.log("ERROR: Got non-string value to translate-tq:", code);
    return 'TRANSLATION ERROR';
  }

  if (code.includes(' ')) {
    return code;
  }

  let t = getTranslations(share);
  if (!t) {
    return code;
  }
  let c = t[code];
  if (!c) {
    c = getTranslationStore(share)[DEFAULT_LANG][code];
    if (!c) {
      return code;
    }
  }
  if (typeof(c) != 'string') {
    console.log("ERROR: Translation resulted in non-string value - possible store corruption");
    return code;
  }
  return c;
}

export function flagIcon(code: string) : string {
  return `<img src="/static/img/flag_${code}.svg" class="w-6 mx-2" />`
}

export function tqSub(share: any, s: string) : string {
  if (typeof(s) != 'string') {
    console.log("ERROR: Got non-string value to translate-tqSub:", s);
    return 'TRANSLATION ERROR';
  }
  let t = getTranslations(share);
  if (!t || !s.includes(TT)) {
    return s;
  }
  s = s.replaceAll(TT, '');
  // todo: refactor for better performance..
  for (let [lc, lv] of Object.entries(t)) {
    if (s.includes(lc)) {
      s = s.replaceAll(lc, lv);
    }
  }
  return s;
}
