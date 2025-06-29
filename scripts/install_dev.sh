#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

if [[ "$(which python3)" == "/usr/bin/python3" ]]
then
  echo 'WARNING: You should use a Python-VENV!'
  exit 1
fi

echo ''
echo '####################'
echo '  BACKEND PACKAGES'
echo '####################'

python3 -m pip >/dev/null

python3 -m pip install -r ../requirements.txt
python3 -m pip install -r ../requirements_lint.txt
python3 -m pip install -r ../requirements_test_backend.txt
python3 -m pip install -r ../requirements_test_frontend.txt

echo ''
echo '####################'
echo '  FRONTEND PACKAGES'
echo '####################'

if ! which npm >/dev/null
then
  echo 'ERROR: You need to install NodeJS for frontend-development. See: https://nodejs.org/en/download'
  exit 1
fi

cd ../frontend
npm install
