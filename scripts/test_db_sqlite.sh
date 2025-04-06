#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS DB SQLITE'
echo ''

export AW_DB_TYPE='sqlite'
export AW_DB="/tmp/$(date +%s).aw.db"

source ./scripts/test_db_base.sh

success
