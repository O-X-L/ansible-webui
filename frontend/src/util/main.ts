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
  console.log("TEST", event);
  navigator.clipboard.writeText(event.target.innerText);
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

const TAILWIND_COLOR_CLASSES = [
  'red',
  'orange',
  'amber',
  'yellow',
  'lime',
  'green',
  'emerald',
  'teal',
  'cyan',
  'sky',
  'blue',
  'indigo',
  'violet',
  'purple',
  'fuchsia',
  'pink',
  'rose',
  'slate',
  'zinc',
  'neutral',
  'stone',
  // black
  // white
  // gray
];
const TAILWIND_COLOR_GRADES = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950'];

export function getRandomTailwindColorClass() {
  let c = TAILWIND_COLOR_CLASSES[Math.floor(Math.random()*TAILWIND_COLOR_CLASSES.length)];
  let g = TAILWIND_COLOR_GRADES[Math.floor(Math.random()*TAILWIND_COLOR_GRADES.length)];
  return `--color-${c}-${g}`;
}

const TAILWIND_COLORS = [
  'oklch(0.971 0.013 17.38)',
  'oklch(0.936 0.032 17.717)',
  'oklch(0.885 0.062 18.334)',
  'oklch(0.808 0.114 19.571)',
  'oklch(0.704 0.191 22.216)',
  'oklch(0.637 0.237 25.331)',
  'oklch(0.577 0.245 27.325)',
  'oklch(0.505 0.213 27.518)',
  'oklch(0.444 0.177 26.899)',
  'oklch(0.396 0.141 25.723)',
  'oklch(0.258 0.092 26.042)',
  'oklch(0.98 0.016 73.684)',
  'oklch(0.954 0.038 75.164)',
  'oklch(0.901 0.076 70.697)',
  'oklch(0.837 0.128 66.29)',
  'oklch(0.75 0.183 55.934)',
  'oklch(0.705 0.213 47.604)',
  'oklch(0.646 0.222 41.116)',
  'oklch(0.553 0.195 38.402)',
  'oklch(0.47 0.157 37.304)',
  'oklch(0.408 0.123 38.172)',
  'oklch(0.266 0.079 36.259)',
  'oklch(0.987 0.022 95.277)',
  'oklch(0.962 0.059 95.617)',
  'oklch(0.924 0.12 95.746)',
  'oklch(0.879 0.169 91.605)',
  'oklch(0.828 0.189 84.429)',
  'oklch(0.769 0.188 70.08)',
  'oklch(0.666 0.179 58.318)',
  'oklch(0.555 0.163 48.998)',
  'oklch(0.473 0.137 46.201)',
  'oklch(0.414 0.112 45.904)',
  'oklch(0.279 0.077 45.635)',
  'oklch(0.987 0.026 102.212)',
  'oklch(0.973 0.071 103.193)',
  'oklch(0.945 0.129 101.54)',
  'oklch(0.905 0.182 98.111)',
  'oklch(0.852 0.199 91.936)',
  'oklch(0.795 0.184 86.047)',
  'oklch(0.681 0.162 75.834)',
  'oklch(0.554 0.135 66.442)',
  'oklch(0.476 0.114 61.907)',
  'oklch(0.421 0.095 57.708)',
  'oklch(0.286 0.066 53.813)',
  'oklch(0.986 0.031 120.757)',
  'oklch(0.967 0.067 122.328)',
  'oklch(0.938 0.127 124.321)',
  'oklch(0.897 0.196 126.665)',
  'oklch(0.841 0.238 128.85)',
  'oklch(0.768 0.233 130.85)',
  'oklch(0.648 0.2 131.684)',
  'oklch(0.532 0.157 131.589)',
  'oklch(0.453 0.124 130.933)',
  'oklch(0.405 0.101 131.063)',
  'oklch(0.274 0.072 132.109)',
  'oklch(0.982 0.018 155.826)',
  'oklch(0.962 0.044 156.743)',
  'oklch(0.925 0.084 155.995)',
  'oklch(0.871 0.15 154.449)',
  'oklch(0.792 0.209 151.711)',
  'oklch(0.723 0.219 149.579)',
  'oklch(0.627 0.194 149.214)',
  'oklch(0.527 0.154 150.069)',
  'oklch(0.448 0.119 151.328)',
  'oklch(0.393 0.095 152.535)',
  'oklch(0.266 0.065 152.934)',
  'oklch(0.979 0.021 166.113)',
  'oklch(0.95 0.052 163.051)',
  'oklch(0.905 0.093 164.15)',
  'oklch(0.845 0.143 164.978)',
  'oklch(0.765 0.177 163.223)',
  'oklch(0.696 0.17 162.48)',
  'oklch(0.596 0.145 163.225)',
  'oklch(0.508 0.118 165.612)',
  'oklch(0.432 0.095 166.913)',
  'oklch(0.378 0.077 168.94)',
  'oklch(0.262 0.051 172.552)',
  'oklch(0.984 0.014 180.72)',
  'oklch(0.953 0.051 180.801)',
  'oklch(0.91 0.096 180.426)',
  'oklch(0.855 0.138 181.071)',
  'oklch(0.777 0.152 181.912)',
  'oklch(0.704 0.14 182.503)',
  'oklch(0.6 0.118 184.704)',
  'oklch(0.511 0.096 186.391)',
  'oklch(0.437 0.078 188.216)',
  'oklch(0.386 0.063 188.416)',
  'oklch(0.277 0.046 192.524)',
  'oklch(0.984 0.019 200.873)',
  'oklch(0.956 0.045 203.388)',
  'oklch(0.917 0.08 205.041)',
  'oklch(0.865 0.127 207.078)',
  'oklch(0.789 0.154 211.53)',
  'oklch(0.715 0.143 215.221)',
  'oklch(0.609 0.126 221.723)',
  'oklch(0.52 0.105 223.128)',
  'oklch(0.45 0.085 224.283)',
  'oklch(0.398 0.07 227.392)',
  'oklch(0.302 0.056 229.695)',
  'oklch(0.977 0.013 236.62)',
  'oklch(0.951 0.026 236.824)',
  'oklch(0.901 0.058 230.902)',
  'oklch(0.828 0.111 230.318)',
  'oklch(0.746 0.16 232.661)',
  'oklch(0.685 0.169 237.323)',
  'oklch(0.588 0.158 241.966)',
  'oklch(0.5 0.134 242.749)',
  'oklch(0.443 0.11 240.79)',
  'oklch(0.391 0.09 240.876)',
  'oklch(0.293 0.066 243.157)',
  'oklch(0.97 0.014 254.604)',
  'oklch(0.932 0.032 255.585)',
  'oklch(0.882 0.059 254.128)',
  'oklch(0.809 0.105 251.813)',
  'oklch(0.707 0.165 254.624)',
  'oklch(0.623 0.214 259.815)',
  'oklch(0.546 0.245 262.881)',
  'oklch(0.488 0.243 264.376)',
  'oklch(0.424 0.199 265.638)',
  'oklch(0.379 0.146 265.522)',
  'oklch(0.282 0.091 267.935)',
  'oklch(0.962 0.018 272.314)',
  'oklch(0.93 0.034 272.788)',
  'oklch(0.87 0.065 274.039)',
  'oklch(0.785 0.115 274.713)',
  'oklch(0.673 0.182 276.935)',
  'oklch(0.585 0.233 277.117)',
  'oklch(0.511 0.262 276.966)',
  'oklch(0.457 0.24 277.023)',
  'oklch(0.398 0.195 277.366)',
  'oklch(0.359 0.144 278.697)',
  'oklch(0.257 0.09 281.288)',
  'oklch(0.969 0.016 293.756)',
  'oklch(0.943 0.029 294.588)',
  'oklch(0.894 0.057 293.283)',
  'oklch(0.811 0.111 293.571)',
  'oklch(0.702 0.183 293.541)',
  'oklch(0.606 0.25 292.717)',
  'oklch(0.541 0.281 293.009)',
  'oklch(0.491 0.27 292.581)',
  'oklch(0.432 0.232 292.759)',
  'oklch(0.38 0.189 293.745)',
  'oklch(0.283 0.141 291.089)',
  'oklch(0.977 0.014 308.299)',
  'oklch(0.946 0.033 307.174)',
  'oklch(0.902 0.063 306.703)',
  'oklch(0.827 0.119 306.383)',
  'oklch(0.714 0.203 305.504)',
  'oklch(0.627 0.265 303.9)',
  'oklch(0.558 0.288 302.321)',
  'oklch(0.496 0.265 301.924)',
  'oklch(0.438 0.218 303.724)',
  'oklch(0.381 0.176 304.987)',
  'oklch(0.291 0.149 302.717)',
  'oklch(0.977 0.017 320.058)',
  'oklch(0.952 0.037 318.852)',
  'oklch(0.903 0.076 319.62)',
  'oklch(0.833 0.145 321.434)',
  'oklch(0.74 0.238 322.16)',
  'oklch(0.667 0.295 322.15)',
  'oklch(0.591 0.293 322.896)',
  'oklch(0.518 0.253 323.949)',
  'oklch(0.452 0.211 324.591)',
  'oklch(0.401 0.17 325.612)',
  'oklch(0.293 0.136 325.661)',
  'oklch(0.971 0.014 343.198)',
  'oklch(0.948 0.028 342.258)',
  'oklch(0.899 0.061 343.231)',
  'oklch(0.823 0.12 346.018)',
  'oklch(0.718 0.202 349.761)',
  'oklch(0.656 0.241 354.308)',
  'oklch(0.592 0.249 0.584)',
  'oklch(0.525 0.223 3.958)',
  'oklch(0.459 0.187 3.815)',
  'oklch(0.408 0.153 2.432)',
  'oklch(0.284 0.109 3.907)',
  'oklch(0.969 0.015 12.422)',
  'oklch(0.941 0.03 12.58)',
  'oklch(0.892 0.058 10.001)',
  'oklch(0.81 0.117 11.638)',
  'oklch(0.712 0.194 13.428)',
  'oklch(0.645 0.246 16.439)',
  'oklch(0.586 0.253 17.585)',
  'oklch(0.514 0.222 16.935)',
  'oklch(0.455 0.188 13.697)',
  'oklch(0.41 0.159 10.272)',
  'oklch(0.271 0.105 12.094)',
  'oklch(0.984 0.003 247.858)',
  'oklch(0.968 0.007 247.896)',
  'oklch(0.929 0.013 255.508)',
  'oklch(0.869 0.022 252.894)',
  'oklch(0.704 0.04 256.788)',
  'oklch(0.554 0.046 257.417)',
  'oklch(0.446 0.043 257.281)',
  'oklch(0.372 0.044 257.287)',
  'oklch(0.279 0.041 260.031)',
  'oklch(0.208 0.042 265.755)',
  'oklch(0.129 0.042 264.695)',
  'oklch(0.967 0.001 286.375)',
  'oklch(0.92 0.004 286.32)',
  'oklch(0.871 0.006 286.286)',
  'oklch(0.705 0.015 286.067)',
  'oklch(0.552 0.016 285.938)',
  'oklch(0.442 0.017 285.786)',
  'oklch(0.37 0.013 285.805)',
  'oklch(0.274 0.006 286.033)',
  'oklch(0.21 0.006 285.885)',
  'oklch(0.141 0.005 285.823)',
  'oklch(0.985 0.001 106.423)',
  'oklch(0.97 0.001 106.424)',
  'oklch(0.923 0.003 48.717)',
  'oklch(0.869 0.005 56.366)',
  'oklch(0.709 0.01 56.259)',
  'oklch(0.553 0.013 58.071)',
  'oklch(0.444 0.011 73.639)',
  'oklch(0.374 0.01 67.558)',
  'oklch(0.268 0.007 34.298)',
  'oklch(0.216 0.006 56.043)',
  'oklch(0.147 0.004 49.25)',
];

export function getRandomTailwindColor() {
  return TAILWIND_COLORS[Math.floor(Math.random()*TAILWIND_COLORS.length)];
}

const TAILWIND_COLORS_NEGATIVE = [
  'oklch(0.885 0.062 18.334)',
  'oklch(0.808 0.114 19.571)',
  'oklch(0.704 0.191 22.216)',
  'oklch(0.637 0.237 25.331)',
  'oklch(0.577 0.245 27.325)',
  'oklch(0.505 0.213 27.518)',
  'oklch(0.444 0.177 26.899)',
  'oklch(0.396 0.141 25.723)',
  'oklch(0.258 0.092 26.042)',
  'oklch(0.901 0.076 70.697)',
  'oklch(0.837 0.128 66.29)',
  'oklch(0.75 0.183 55.934)',
  'oklch(0.705 0.213 47.604)',
  'oklch(0.646 0.222 41.116)',
  'oklch(0.553 0.195 38.402)',
  'oklch(0.47 0.157 37.304)',
  'oklch(0.408 0.123 38.172)',
  'oklch(0.266 0.079 36.259)',
  'oklch(0.924 0.12 95.746)',
  'oklch(0.879 0.169 91.605)',
  'oklch(0.828 0.189 84.429)',
  'oklch(0.769 0.188 70.08)',
  'oklch(0.666 0.179 58.318)',
  'oklch(0.555 0.163 48.998)',
  'oklch(0.473 0.137 46.201)',
  'oklch(0.414 0.112 45.904)',
  'oklch(0.279 0.077 45.635)',
  'oklch(0.945 0.129 101.54)',
  'oklch(0.905 0.182 98.111)',
  'oklch(0.852 0.199 91.936)',
  'oklch(0.795 0.184 86.047)',
  'oklch(0.681 0.162 75.834)',
  'oklch(0.554 0.135 66.442)',
  'oklch(0.476 0.114 61.907)',
  'oklch(0.421 0.095 57.708)',
  'oklch(0.286 0.066 53.813)',
  'oklch(0.899 0.061 343.231)',
  'oklch(0.823 0.12 346.018)',
  'oklch(0.718 0.202 349.761)',
  'oklch(0.656 0.241 354.308)',
  'oklch(0.592 0.249 0.584)',
  'oklch(0.525 0.223 3.958)',
  'oklch(0.459 0.187 3.815)',
  'oklch(0.408 0.153 2.432)',
  'oklch(0.284 0.109 3.907)',
];

export function getRandomTailwindColorNegative() {
  return TAILWIND_COLORS_NEGATIVE[Math.floor(Math.random()*TAILWIND_COLORS_NEGATIVE.length)];
}

const TAILWIND_COLORS_POSITIVE = [
  'oklch(0.938 0.127 124.321)',
  'oklch(0.897 0.196 126.665)',
  'oklch(0.841 0.238 128.85)',
  'oklch(0.768 0.233 130.85)',
  'oklch(0.648 0.2 131.684)',
  'oklch(0.532 0.157 131.589)',
  'oklch(0.453 0.124 130.933)',
  'oklch(0.405 0.101 131.063)',
  'oklch(0.274 0.072 132.109)',
  'oklch(0.925 0.084 155.995)',
  'oklch(0.871 0.15 154.449)',
  'oklch(0.792 0.209 151.711)',
  'oklch(0.723 0.219 149.579)',
  'oklch(0.627 0.194 149.214)',
  'oklch(0.527 0.154 150.069)',
  'oklch(0.448 0.119 151.328)',
  'oklch(0.393 0.095 152.535)',
  'oklch(0.266 0.065 152.934)',
  'oklch(0.905 0.093 164.15)',
  'oklch(0.845 0.143 164.978)',
  'oklch(0.765 0.177 163.223)',
  'oklch(0.696 0.17 162.48)',
  'oklch(0.596 0.145 163.225)',
  'oklch(0.508 0.118 165.612)',
  'oklch(0.432 0.095 166.913)',
  'oklch(0.378 0.077 168.94)',
  'oklch(0.262 0.051 172.552)',
  'oklch(0.91 0.096 180.426)',
  'oklch(0.855 0.138 181.071)',
  'oklch(0.777 0.152 181.912)',
  'oklch(0.704 0.14 182.503)',
  'oklch(0.6 0.118 184.704)',
  'oklch(0.511 0.096 186.391)',
  'oklch(0.437 0.078 188.216)',
  'oklch(0.386 0.063 188.416)',
  'oklch(0.277 0.046 192.524)',
  'oklch(0.917 0.08 205.041)',
  'oklch(0.865 0.127 207.078)',
  'oklch(0.789 0.154 211.53)',
  'oklch(0.715 0.143 215.221)',
  'oklch(0.609 0.126 221.723)',
  'oklch(0.52 0.105 223.128)',
  'oklch(0.45 0.085 224.283)',
  'oklch(0.398 0.07 227.392)',
  'oklch(0.302 0.056 229.695)',
  'oklch(0.901 0.058 230.902)',
  'oklch(0.828 0.111 230.318)',
  'oklch(0.746 0.16 232.661)',
  'oklch(0.685 0.169 237.323)',
  'oklch(0.588 0.158 241.966)',
  'oklch(0.5 0.134 242.749)',
  'oklch(0.443 0.11 240.79)',
  'oklch(0.391 0.09 240.876)',
  'oklch(0.293 0.066 243.157)',
  'oklch(0.882 0.059 254.128)',
  'oklch(0.809 0.105 251.813)',
  'oklch(0.707 0.165 254.624)',
  'oklch(0.623 0.214 259.815)',
  'oklch(0.546 0.245 262.881)',
  'oklch(0.488 0.243 264.376)',
  'oklch(0.424 0.199 265.638)',
  'oklch(0.379 0.146 265.522)',
  'oklch(0.282 0.091 267.935)',
  'oklch(0.87 0.065 274.039)',
  'oklch(0.785 0.115 274.713)',
  'oklch(0.673 0.182 276.935)',
  'oklch(0.585 0.233 277.117)',
  'oklch(0.511 0.262 276.966)',
  'oklch(0.457 0.24 277.023)',
  'oklch(0.398 0.195 277.366)',
  'oklch(0.359 0.144 278.697)',
  'oklch(0.257 0.09 281.288)',
];

export function getRandomTailwindColorPositive() {
  return TAILWIND_COLORS_POSITIVE[Math.floor(Math.random()*TAILWIND_COLORS_POSITIVE.length)];
}
