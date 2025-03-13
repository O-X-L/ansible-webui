export function getDarkLightMode() {
    let lastColorMode = localStorage.getItem('color-theme');
    if (lastColorMode && (lastColorMode == 'light' || lastColorMode == 'dark')) {
      return lastColorMode;

    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }

    return 'light';
}

export function setDarkLightMode(doc: HTMLDocument, mode: string = '') {
    if (mode == '') {
        mode = getDarkLightMode();
    }
    let h = doc.querySelector('html');
    if (!h) {
      return;
    }
    h.classList.add(mode);
}
