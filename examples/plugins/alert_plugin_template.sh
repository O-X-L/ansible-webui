#!/usr/bin/env bash

# requires package 'jq' to parse JSON (apt install jq)

set -euo pipefail

file_in="$1"
data="$(cat "$file_in")"

failed="$(echo "$data" | jq -r '.execution.failed')"
hosts="$(echo "$data" | jq -r '.stats | keys[]')"

# echo "FAILED: $failed"
if [[ "$failed" == "true" ]]
then
  # failure action

  for host in "${hosts[@]}"
  do
    stats="$(echo "$data" | jq ".stats.${host}")"
    # echo "$host => $stats"

    unreachable="$(echo "$stats" | jq -r '.unreachable')"
    tasks_failed="$(echo "$stats" | jq -r '.tasks_failed')"
    if [[ "$unreachable" == "true" ]] || [[ "$tasks_failed" != "0" ]]
    then
      # hosts that failed
      # echo "FAILED: $host"
    fi

  done
fi
