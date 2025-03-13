#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

# see: https://github.com/nodesource/distributions
if ! which npm > /dev/null
then
  echo ''
  echo '### INSTALLING NPM ###'
  curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh
  sudo -E bash nodesource_setup.sh
  sudo apt-get install -y nodejs
fi

if ! [ -d "$(pwd)/../../frontend/node_modules/@sveltejs" ]
then
  echo ''
  echo '### INSTALLING SVELTE ###'
  cd "$(pwd)"
  npm install
fi
