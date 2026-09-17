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

bash ./scripts/test_cli_tools.sh
sleep 1

##############################

echo ''
echo 'TESTING TO INITIALIZE AW-DB'
echo ''

bash ./scripts/test_db_init.sh
sleep 1

##############################

echo ''
echo '### FINISHED ###'
echo ''
