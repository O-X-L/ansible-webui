#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

export PYTHONPATH=''

REPO_BASE="$(pwd)"
cd /tmp
export AW_DB="${REPO_BASE}/src/oxl_ansible_webui/aw.dev.db"
python3 "${REPO_BASE}/src/oxl_ansible_webui/cli.py" --version
python3 "${REPO_BASE}/src/oxl_ansible_webui/manage.py"
cd "$REPO_BASE"
