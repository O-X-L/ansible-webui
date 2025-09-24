#!/usr/bin/env bash

set -euo pipefail

function log() {
  echo ''
  echo "### $1 ###"
  echo ''
}

if [ ! -d '/repo/src/oxl_ansible_webui/' ]
then
  echo 'ERROR: Requires Repository-Root to be mounted docker-volume to /repo/'
  exit 1
fi

TEST_MIGRATE=''
if [[ "$DEV_CLEAN" != '0' ]]
then
  log 'CLEANING DB'
  rm "$AW_DB"
  TEST_MIGRATE='clean'
fi

if [[ "$DEV_INIT" == '1' ]]
then
  log 'INSTALLING REQUIREMENTS'
  python3 -m pip install --upgrade -r /repo/requirements.txt >/dev/null

  log 'INITIALIZING DATABASE SCHEMA'
  bash /repo/scripts/migrate_db.sh "$TEST_MIGRATE"

  log 'CREATING USERS'
  python3 /repo/src/oxl_ansible_webui/manage.py createsuperuser --noinput || true
fi

log 'STARTING APP'
python3 /repo/src/oxl_ansible_webui