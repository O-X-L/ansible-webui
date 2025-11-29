import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    svelte(),
  ],
  css: {},
  root: resolve("./src"),
  base: '/static/',
  resolve: {
    extensions: ['.js', '.json', '.ts'],
  },
  build: {
    manifest: false,
    assetsDir: "",
    emptyOutDir: true,
    outDir: resolve("./dist/"),
    rollupOptions: {
      input: {
        main: "./src/main.ts",
        home: "./src/home.ts",
        login: "./src/login.ts",
        system: "./src/system.ts",
        login_saml: "./src/login_saml.ts",
      },
    },
    chunkSizeWarningLimit: 1500,
  },
})
