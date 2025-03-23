import { Chart } from 'chart.js';

export function getDarkLightMode() : 'dark'|'light' {
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

    if (mode == 'dark') {
      Chart.defaults.color = "#ADBABD";
      Chart.defaults.borderColor = "rgba(255,255,255,0.1)";
      Chart.defaults.backgroundColor = "rgba(255,255,0,0.1)";
      Chart.defaults.elements.line.borderColor = "rgba(255,255,0,0.4)";
    }

    let h = doc.querySelector('html');
    if (!h) {
      return;
    }
    h.classList.add(mode);
}
