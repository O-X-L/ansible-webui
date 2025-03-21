#!/usr/bin/env bash

set -euo pipefail

SRC_DIR="$1"
DST_DIR="$2"

bash link_flowbite_custom.sh "$SRC_DIR"

mkdir -p "$DST_DIR"
bash build_tailwind.sh "$SRC_DIR" "$DST_DIR" &

cd "$SRC_DIR"
npm run build >/dev/null

APPS=$(ls "${SRC_DIR}/dist/"*.js | rev | cut -d '/' -f 1 | rev | cut -d '-' -f1)

for app in $APPS
do
  cp "${SRC_DIR}/dist/${app}"-*css "${DST_DIR}/${app}.css" 2>/dev/null || true
  cp "${SRC_DIR}/dist/${app}"-*js "${DST_DIR}/${app}.js" 2>/dev/null || true

  for ref in $APPS
  do
    if [[ "$app" != "$ref" ]]
    then
      if [ -f "${DST_DIR}/${app}.js" ]
      then
        sed -i "s|from\"./${ref}-[^\.]*\.js\"|from\"./${ref}.js\"|g" "${DST_DIR}/${app}.js"
        sed -i "s|import\"./${ref}-[^\.]*\.js\"|import\"./${ref}.js\"|g" "${DST_DIR}/${app}.js"
      fi
    fi
  done
done
