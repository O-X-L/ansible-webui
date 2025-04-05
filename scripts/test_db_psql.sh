#!/usr/bin/env bash

# docker run --detach --name aw-psql --env POSTGRES_USER=aw --env POSTGRES_PASSWORD=test --env POSTGRES_DB=aw -p 5432:5432 postgres:latest
# docker exec -u postgres -it aw-psql /usr/bin/psql

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS DB POSTGRESQL'
echo ''

export AW_DB_TYPE='psql'
export AW_DB='aw'
export AW_DB_HOST="${AW_DB_HOST:-127.0.0.1}"
export AW_DB_PORT='5432'
export AW_DB_USER='postgres'
export AW_DB_PWD='test'

source ./scripts/test_db_base.sh

success
