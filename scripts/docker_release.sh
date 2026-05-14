#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"
VERSION_IMAGE="$(echo "$VERSION" | cut -d '-' -f1)"
cd "$(dirname "$0")/../docker"

source ./build_config.sh

echo ''
read -r -p "Release version ${VERSION} as latest? [y/N] " -n 1

function push() {
  img="$1"
  tag="$2"
  img_with_tag="${img}:${tag}"
  echo "##### PUSHING ${img_with_tag} #####"
  docker push "$img_with_tag"
}

for img in "${IMAGES[@]}"
do
  echo ''
  echo "### BUILDING ${img} ###"

  set +u
  if [ -n "${DOCKERFILES_DEBIAN["$img"]+_}" ]
  then
    push "$img" "${VERSION_IMAGE}-debian"
    if [[ "$REPLY" =~ ^[Yy]$ ]]
    then
      push "$img" "latest-debian"
    fi
  fi

  set +u
  if [ -n "${DOCKERFILES_ALPINE["$img"]+_}" ]
  then
    push "$img" "${VERSION_IMAGE}-alpine"
    if [[ "$REPLY" =~ ^[Yy]$ ]]
    then
      push "$img" "latest-alpine"
    fi
  fi
  set -u

  if [[ "$REPLY" =~ ^[Yy]$ ]]
  then
    push "$img" "latest"
  fi
done
