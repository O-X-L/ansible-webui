#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHONPATH=''

export DJANGO_SETTINGS_MODULE='aw.settings'
python3 -m pytest $@
