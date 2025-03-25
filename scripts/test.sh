#!/bin/bash

set -e

cd "$(dirname "$0")/.."

export PYTHONPATH=''

function failure() {
  echo ''
  echo '### FAILED ###'
  echo ''
  pkill -f oxl_ansible_webui
  exit 1
}

##############################

echo ''
echo 'BUILD FRONTEND'
echo ''

FORCE_UPDATE=1 bash scripts/frontend/build.sh

##############################

echo ''
echo 'UNIT TESTS'
echo ''

python3 -m pytest

##############################

if pgrep -f 'oxl-ansible-webui'
then
  echo 'An instance of Ansible-WebUI is already running! Stop it first (pkill -f oxl_ansible_webui)'
  exit 1
fi

echo 'Starting Ansible-WebUI..'
trap "pkill -f oxl_ansible_webui; exit" INT
export AW_ENV='dev'
# shellcheck disable=SC2155
export AW_DB="/tmp/$(date +%s).aw.db"
# shellcheck disable=SC2155
export AW_PATH_PLAY="$(pwd)/test"
export AW_ADMIN='tester'
export AW_ADMIN_PWD='someSecret!Pwd'
python3 src/oxl_ansible_webui/ >/dev/null 2>/dev/null &
echo ''
sleep 10
set +e

##############################

echo ''
echo 'INTEGRATION TESTS API'
echo ''

echo 'Create API key'
api_key="$(python3 src/oxl_ansible_webui/cli.py -a api-key.create -p "$AW_ADMIN" | grep 'Key=' | cut -d '=' -f2)"
export AW_API_KEY="$api_key"
sleep 1

if ! python3 test/integration/api/main.py
then
  failure
fi

sleep 1

##############################

echo ''
echo 'INTEGRATION TESTS WEB-UI'
echo ''

if ! python3 test/integration/webui/main.py
then
  failure
fi

sleep 1
pkill -f oxl_ansible_webui
sleep 5

##############################

echo ''
echo 'INTEGRATION TESTS SAML'
echo ''

echo 'Starting Ansible-WebUI with SAML enabled..'
# shellcheck disable=SC2155
export AW_DB="/tmp/$(date +%s).aw.db"
# shellcheck disable=SC2155
export AW_CONFIG="$(pwd)/test/integration/auth/saml.yml"
python3 src/oxl_ansible_webui/ >/dev/null 2>/dev/null &
echo ''
sleep 5

if ! python3 test/integration/auth/saml.py
then
  failure
fi

sleep 1
export AW_CONFIG=''
pkill -f oxl_ansible_webui

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
