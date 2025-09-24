#!/usr/bin/env bash

set -euo pipefail

if [ ! -d '/repo/frontend/src/' ]
then
  echo 'ERROR: Requires Repository-Root to be mounted docker-volume to /repo/'
  exit 1
fi

if [ ! -d '/repo/frontend/node_modules' ]
then
  cd /repo/frontend
  echo ''
  echo '### INSTALLING NPM MODULES ###'
  npm install
fi

echo ''
echo '### BUILDING ###'
bash /repo/scripts/frontend/build_base.sh /repo/frontend/ /repo/src/oxl_ansible_webui/aw/static_dev/dist/
ls /repo/src/oxl_ansible_webui/aw/static_dev/dist/
chmod 777 /repo/src/oxl_ansible_webui/aw/static_dev/dist/*

echo ''
echo '### VALIDATING ###'
bash /repo/scripts/frontend/validate_prod_build.sh 'dev'

echo ''
echo '### DONE ###'
