#!/usr/bin/env bash

# docker run --detach --name aw-mariadb --env MARIADB_ROOT_PASSWORD=test --env MARIADB_DATABASE=aw -p 3306:3306 mariadb:latest

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS DB MARIADB/MYSQL'
echo ''

export AW_DB_TYPE='mysql'
export AW_DB='aw'
export AW_DB_HOST="${AW_DB_HOST:-'127.0.0.1'}"
export AW_DB_PORT='3306'
export AW_DB_USER='root'
export AW_DB_PWD='test'

source ./scripts/test_db_base.sh

success
