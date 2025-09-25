#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"

cd "$(dirname "$0")/../docker"

source ./build_config.sh

read -r -p "Build version ${VERSION} as latest? [y/N] " -n 1

echo ''
echo "### CLEANUP ###"

if docker image ls | grep "$IMAGE_REPO" | grep -q "$VERSION"
then
  for img in $(docker image ls | egrep "^${IMAGE_REPO}" | awk '{print $1":"$2}')
  do
    docker image rm "$img" || true
  done
fi

function build() {
  set -u
  img="$1"
  dockerfile="$2"
  tag="$3"
  cache="$4"
  img_with_tag="${img}:${tag}"
  if [[ "$cache" == "1" ]]
  then
    cache=""
  else
    cache=" --no-cache"
  fi

  echo "##### BUILDING ${img_with_tag} #####"
  docker build -f "$dockerfile" -t "$img_with_tag" --network host --build-arg "AW_VERSION=${VERSION}" $cache .
}

echo ''
echo "### BUILDING FRONTEND ###"
docker build -f "Dockerfile_builder_frontend" -t "${IMAGE_REPO}-builder-fe:${VERSION}" --network host --build-arg "AW_VERSION=${VERSION}" --no-cache .

for img in "${IMAGES[@]}"
do
  echo ''
  echo "### BUILDING ${img} ###"

  set +u
  if [ -n "${DOCKERFILES_DEBIAN["$img"]+_}" ]
  then
    build "$img" "${DOCKERFILES_DEBIAN["$img"]}" "${VERSION}-debian" "0"
    if [[ "$REPLY" =~ ^[Yy]$ ]]
    then
      build "$img" "${DOCKERFILES_DEBIAN["$img"]}" "latest-debian" "1"
    fi
  fi

  set +u
  if [ -n "${DOCKERFILES_ALPINE["$img"]+_}" ]
  then
    build "$img" "${DOCKERFILES_ALPINE["$img"]}" "${VERSION}-alpine" "0"
    if [[ "$REPLY" =~ ^[Yy]$ ]]
    then
      build "$img" "${DOCKERFILES_ALPINE["$img"]}" "latest-alpine" "1"
    fi
  fi
  set -u

  if [[ "$REPLY" =~ ^[Yy]$ ]]
  then
    build "$img" "${DOCKERFILES_LATEST["$img"]}" "latest" "1"
  fi
done

echo ''
echo "### DONE - PLEASE TEST THAT THE IMAGES WORK BEFORE PUSHING THEM! ###"
