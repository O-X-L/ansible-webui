#!/usr/bin/env bash

set -euo pipefail

BASE="$1"

cd "${BASE}/node_modules/flowbite-svelte/dist/forms/"
if [ ! -f 'MultiInput.svelte' ] && [ ! -L 'MultiInput.svelte' ]
then
  ln -s ../../../../src/flowbite-custom/MultiInput.svelte MultiInput.svelte
  ln -s ../../../../src/flowbite-custom/MultiInput.svelte.d.ts MultiInput.svelte.d.ts

  # todo:
  #   index.js
  #     export { default as MultiInput } from './forms/MultiInput.svelte';
  #   index.d.ts
  #     export { default as MultiInput } from "./forms/MultiInput.svelte";
fi
