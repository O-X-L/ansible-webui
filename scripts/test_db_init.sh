#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

# shellcheck disable=SC2155
TMP_DIR="/tmp/aw_$(date +%s)"
mkdir -p "$TMP_DIR"
cp -r ./* "$TMP_DIR"
cd "$TMP_DIR"
export AW_DB="${TMP_DIR}/aw.db"
timeout 10 python3 src/oxl_ansible_webui
ec="$?"
if [[ "$ec" != "124" ]]
then
  exit 1
fi
