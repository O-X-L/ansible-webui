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
        index: "./src/index.ts",
      },
    },
  },
})
