const DEFAULT_LANG = 'en'

export function tq(share: any, code: string) {
  let userLang = localStorage.language;

  if (!userLang || !share.lang[userLang] || !share.lang[userLang][code]) {
    if (!share.lang[DEFAULT_LANG] || !share.lang[DEFAULT_LANG][code]) {
      return code;
    } else {
      return share.lang[DEFAULT_LANG][code];
    }
  }

  return share.lang[userLang][code];
}

export function flagIcon(code: string) {
  return `<img src="/static/img/flag_${code}.svg" class="w-6 mx-2" />`
}