#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

REPO_BASE="$(pwd)/../.."

SRC_DIR="${REPO_BASE}/frontend"
DST_DIR="${REPO_BASE}/src/oxl_ansible_webui/aw/static_dev/dist"

mkdir -p "${DST_DIR}"
rm -f "${DST_DIR}/"*.js
rm -f "${DST_DIR}/"*.css
rm -f "${SRC_DIR}/vite.config.ts.time"*

echo '### RUNNING FRONTEND UPDATER ###'
touch "${SRC_DIR}/src/.update_now"
while true
do
  bash "$(pwd)/build.sh" || true
done
