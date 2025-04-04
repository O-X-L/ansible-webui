#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS WEB-UI AUTH-SAML'
echo ''

# shellcheck disable=SC2155
export AW_CONFIG="$(pwd)/test/integration/auth/saml.yml"

source ./scripts/test_base.sh

if ! python3 test/integration/auth/saml.py
then
  failure
fi

export AW_CONFIG=''

success
