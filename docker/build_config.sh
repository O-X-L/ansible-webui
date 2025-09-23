#!/usr/bin/env bash

IMAGE_REPO="oxlorg/ansible-webui"
IMAGE_REPO_UNPRIV="${IMAGE_REPO}-unprivileged"
IMAGE_REPO_AWS="${IMAGE_REPO}-aws"
IMAGE_REPO_MYSQL="${IMAGE_REPO}-mysql"
IMAGE_REPO_PSQL="${IMAGE_REPO}-psql"

IMAGES=(
  "$IMAGE_REPO"
  "$IMAGE_REPO_UNPRIV"
  "$IMAGE_REPO_AWS"
  "$IMAGE_REPO_MYSQL"
  "$IMAGE_REPO_PSQL"
)

# todo: allow for multi-platform builds
# RELEASE_ARCHS="linux/arm/v7,linux/arm64/v8,linux/amd64"

declare -A DOCKERFILES_DEBIAN
DOCKERFILES_DEBIAN["$IMAGE_REPO"]='Dockerfile_production_debian'
DOCKERFILES_DEBIAN["$IMAGE_REPO_UNPRIV"]='Dockerfile_production_unprivileged_debian'
DOCKERFILES_DEBIAN["$IMAGE_REPO_MYSQL"]='Dockerfile_production_mysql_debian'
DOCKERFILES_DEBIAN["$IMAGE_REPO_PSQL"]='Dockerfile_production_psql_debian'

declare -A DOCKERFILES_ALPINE
DOCKERFILES_ALPINE["$IMAGE_REPO"]='Dockerfile_production_alpine'
DOCKERFILES_ALPINE["$IMAGE_REPO_UNPRIV"]='Dockerfile_production_unprivileged_alpine'
DOCKERFILES_ALPINE["$IMAGE_REPO_MYSQL"]='Dockerfile_production_mysql_alpine'
DOCKERFILES_ALPINE["$IMAGE_REPO_AWS"]='Dockerfile_production_aws_alpine'
DOCKERFILES_ALPINE["$IMAGE_REPO_PSQL"]='Dockerfile_production_psql_alpine'

declare -A DOCKERFILES_LATEST
DOCKERFILES_LATEST["$IMAGE_REPO"]='Dockerfile_production_alpine'
DOCKERFILES_LATEST["$IMAGE_REPO_UNPRIV"]='Dockerfile_production_unprivileged_alpine'
DOCKERFILES_LATEST["$IMAGE_REPO_MYSQL"]='Dockerfile_production_mysql_debian'
DOCKERFILES_LATEST["$IMAGE_REPO_AWS"]='Dockerfile_production_aws_alpine'
DOCKERFILES_LATEST["$IMAGE_REPO_PSQL"]='Dockerfile_production_psql_alpine'
