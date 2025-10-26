#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"
PATH_SCRIPT="$(pwd)"

source "${PATH_SCRIPT}/docker_dev_fe.sh"
source "${PATH_SCRIPT}/docker_dev_be.sh"
