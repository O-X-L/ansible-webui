#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

export PYTHONPATH=''

##############################

echo ''
echo 'BUILD FRONTEND'
echo ''

bash scripts/frontend/build.sh

##############################

echo ''
echo 'UNIT TESTS'
echo ''

python3 -m pytest

##############################

bash ./scripts/test_api.sh
sleep 1

##############################

bash ./scripts/test_job_exec.sh
sleep 1

##############################

bash ./scripts/test_webui.sh
sleep 1

##############################

bash ./scripts/test_auth_saml.sh
sleep 1

##############################

echo ''
echo 'TESTING CLI TOOLS'
echo ''

REPO_BASE="$(pwd)"
cd /tmp
export AW_DB="${REPO_BASE}/src/oxl_ansible_webui/aw.dev.db"
python3 "${REPO_BASE}/src/oxl_ansible_webui/cli.py" --version
python3 "${REPO_BASE}/src/oxl_ansible_webui/manage.py"
cd "$REPO_BASE"

##############################

echo ''
echo 'TESTING TO INITIALIZE AW-DB'
echo ''

# shellcheck disable=SC2155
TMP_DIR="/tmp/aw_$(date +%s)"
mkdir -p "$TMP_DIR"
cp -r ./* "$TMP_DIR"
cd "$TMP_DIR"
rm -rf ./src/oxl_ansible_webui/aw/migrations/*
export AW_DB="${TMP_DIR}/aw.db"
timeout 10 python3 src/oxl_ansible_webui
ec="$?"
if [[ "$ec" != "124" ]]
then
  exit 1
fi

echo ''
echo '### FINISHED ###'
echo ''
