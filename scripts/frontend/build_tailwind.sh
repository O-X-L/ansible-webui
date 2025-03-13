#!/usr/bin/env bash

set -euo pipefail

SRC_DIR="$1"
DST_DIR="$2"

SRC_TW="${SRC_DIR}/dist/tailwind.min.css"

cd "$SRC_DIR"
npx tailwindcss -i "${SRC_DIR}/src/tailwind.css" -o "$SRC_TW" --minify 2>/dev/null

# v4
# npx @tailwindcss/cli -i "${SRC_DIR}/src/tailwind.css" -o "${SRC_DIR}/dist/tailwind.min.css" --minify 2>/dev/null

if [ -f "$SRC_TW" ]
then
  cp "$SRC_TW" "${DST_DIR}/tailwind.min.css"
fi
