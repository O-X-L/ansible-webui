#!/usr/bin/env bash

set -euo pipefail

FORCE_UPDATE="${FORCE_UPDATE:-1}"

cd "$(dirname "$0")/"

REPO_BASE="$(pwd)/../.."
SRC_DIR="${REPO_BASE}/frontend"
DST_DIR="${REPO_BASE}/src/oxl_ansible_webui/aw/static_dev/dist"
UPDATE_NOW="${SRC_DIR}/src/.update_now"

if [[ "$FORCE_UPDATE" == '1' ]]
then
  touch "$UPDATE_NOW"
fi

function check_src_changes() {
  recent_changes="$(find "${SRC_DIR}/src/" -type f -mmin -0.3 | wc -l)"
  if [[ "$recent_changes" == '0' ]]
  then
    exit 0
  fi
}

check_src_changes

bash build_base.sh "$SRC_DIR" "$DST_DIR"

echo "--- $(date +%H:%M:%S) FRONTEND UPDATED ---"
rm -f "$UPDATE_NOW"
