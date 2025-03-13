#!/usr/bin/env bash

set -euo pipefail

FORCE_UPDATE="${FORCE_UPDATE:-0}"

cd "$(dirname "$0")/"

REPO_BASE="$(pwd)/../.."
SRC_DIR="${REPO_BASE}/frontend/"
DST_DIR="${REPO_BASE}/src/oxl_ansible_webui/aw/static_dev/dist"
mkdir -p "$DST_DIR"

echo "$FORCE_UPDATE"
if [[ "$FORCE_UPDATE" == '1' ]]
then
  touch "${REPO_BASE}/frontend/src/.update_now"
fi

function check_src_changes() {
  recent_changes="$(find "${SRC_DIR}/src/" -type f -mmin -0.5 | wc -l)"
  if [[ "$recent_changes" == '0' ]]
  then
    exit 0
  fi
}

check_src_changes

bash build_tailwind.sh "$SRC_DIR" "$DST_DIR" &

cd "$SRC_DIR"
npm run build >/dev/null

APPS=(
  'Footer' 'Wrapper' 'DarkLightMode' 'Toggle' 'main' 'Spinner' 'Heading' 'Style'
  'index'
)

for app in "${APPS[@]}"
do
  cp "${SRC_DIR}/dist/${app}"-*css "${DST_DIR}/${app}.css" 2>/dev/null || true
  cp "${SRC_DIR}/dist/${app}"-*js "${DST_DIR}/${app}.js" 2>/dev/null || true

  for ref in "${APPS[@]}"
  do
    if [[ "$app" != "$ref" ]]
    then
      if [ -f "${DST_DIR}/${app}.js" ]
      then
        sed -i "s|from\"./${ref}-[^\.]*\.js\"|from\"./${ref}.js\"|g" "${DST_DIR}/${app}.js"
      fi
    fi
  done
done
echo "--- $(date +%H:%M:%S) FRONTEND UPDATED ---"
