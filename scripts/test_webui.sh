#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS WEB-UI'
echo ''

source ./scripts/test_base.sh

if ! python3 test/integration/webui/main.py
then
  failure
fi

success
