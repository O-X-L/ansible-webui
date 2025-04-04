#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS JOB-EXECUTION'
echo ''

source ./scripts/test_base.sh

echo 'Create API key'
api_key="$(python3 src/oxl_ansible_webui/cli.py -a api-key.create -p "$AW_ADMIN" | grep 'Key=' | cut -d '=' -f2)"
export AW_API_KEY="$api_key"
sleep 1

if ! python3 test/integration/job-exec/main.py
then
  failure
fi

success
