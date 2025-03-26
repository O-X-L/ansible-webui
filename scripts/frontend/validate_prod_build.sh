#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/../.."

DST='src/oxl_ansible_webui/aw/static_prod/dist'

if [ ! -f "${DST}/tailwind.min.css" ]
then
  echo 'BUILD ERROR: MISSING TAILWIND'
  exit 1
fi

APPS=('main' 'login' 'home' 'system')
for app in $APPS
do
  if [ ! -f "${DST}/${app}.js" ]
  then
    echo "BUILD ERROR: MISSING MAIN JS-APP '${app}'"
    exit 1
  fi
done
