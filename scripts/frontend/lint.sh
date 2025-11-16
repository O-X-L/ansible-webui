#!/usr/bin/env bash

# todo: make work in container

if [ -z "$1" ]
then
  set -euo pipefail
else
  set -uo pipefail
fi

cd "$(dirname "$0")/../.."
BASE_DIR="$(pwd)"

echo ''
echo '### LINTING ###'
echo ''
cd "${BASE_DIR}/frontend"

npm run lint
