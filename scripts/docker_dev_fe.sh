#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/../docker"

if docker image ls | grep -vq 'aw-dev-fe'
then
  echo '### BUILDING aw-dev-fe IMAGE ###'
  docker build -f Dockerfile_dev_frontend -t aw-dev-fe --network=host --no-cache .
fi

echo '### GENERATING FRONTEND BUNDLE ###'
docker run -it --rm --name aw-dev-fe --network=host --volume "$(pwd)/..:/repo" aw-dev-fe
