#!/usr/bin/env bash

if [ -z "$1" ]
then
  DEV_INIT=1
else
  DEV_INIT="$1"
fi

set -euo pipefail

cd "$(dirname "$0")/../docker"

if docker image ls | grep -vq 'aw-dev-be'
then
  echo '### BUILDING aw-dev-be IMAGE ###'
  docker build -f Dockerfile_dev_backend -t aw-dev-be --network=host --no-cache --build-arg "UID=$(id -u)" ..
fi

echo '### STARTING WEB SERVICE ###'
docker run -it --rm --name aw-dev-be --network=host --volume "$(pwd)/..:/repo" --env DEV_INIT="$DEV_INIT" aw-dev-be
