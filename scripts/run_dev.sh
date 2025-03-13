#!/bin/bash

set -e

export TEST_QUIET=0
if [[ -n "$1" ]] && [[ "$1" == "q" ]]
then
  export TEST_QUIET=1
fi

cd "$(dirname "$0")"

trap "pkill -f frontend/run_updater.sh; pkill -f oxl_ansible_webui; exit" INT
bash ./frontend/run_updater.sh &
sleep 2

export AW_DEV=1
export AW_ENV='dev'
export AW_SECRET='asdfThisIsSuperSecret!12345678'  # keep sessions on auto-reload
source ./run_shared.sh
