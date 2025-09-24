#!/usr/bin/env bash

set -eo pipefail

ENV='prod'
if [ -n "$1" ]
then
  ENV="$1"
fi

cd "$(dirname "$0")/../.."


DST="src/oxl_ansible_webui/aw/static_${ENV}/dist"

if [ ! -f "${DST}/tailwind.min.css" ]
then
  echo 'BUILD ERROR: MISSING TAILWIND'
  exit 1
fi

APPS=('main' 'login' 'home' 'system' 'login_saml')
for app in $APPS
do
  if [ ! -f "${DST}/${app}.js" ]
  then
    echo "BUILD ERROR: MISSING MAIN JS-APP '${app}'"
    exit 1
  fi
done
