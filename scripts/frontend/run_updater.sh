#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

REPO_BASE="$(pwd)/../.."

PATH_STATIC_DEV="${REPO_BASE}/src/oxl_ansible_webui/aw/static_dev"
rm -f "${PATH_STATIC_DEV}/dist/"*.js
rm -f "${PATH_STATIC_DEV}/dist/"*.css
rm -f "${REPO_BASE}/frontend/vite.config.ts.time"*

mkdir -p "${PATH_STATIC_DEV}"
mkdir -p "${PATH_STATIC_DEV}/vendor"
mkdir -p "${PATH_STATIC_DEV}/dist"

echo '### RUNNING FRONTEND UPDATER ###'
touch "${REPO_BASE}/frontend/src/.update_now"
while true
do
  bash "$(pwd)/build.sh" || true
done
