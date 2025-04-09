export PYTHONPATH=''

function failure() {
  echo ''
  echo '### FAILED ###'
  echo ''
  pkill -f oxl_ansible_webui
  exit 1
}

function success() {
  echo ''
  echo '### SUCCESS ###'
  echo ''
  pkill -f oxl_ansible_webui
  sleep 3
  exit 0
}

sleep 1
if pgrep -f 'oxl-ansible-webui'
then
  echo 'Stopping Ansible-WebUI..'
  pkill -f oxl_ansible_webui
  sleep 5
fi

echo 'Starting Ansible-WebUI..'
trap "pkill -f oxl_ansible_webui; exit" INT

# shellcheck disable=SC2155
export AW_PATH_PLAY="$(pwd)/test"
export AW_ADMIN='tester'
export AW_ADMIN_PWD='someSecret!Pwd'

if [ -z "$AW_TEST_DB" ]
then
  export AW_ENV='dev'
  # shellcheck disable=SC2155
  export AW_DB="/tmp/$(date +%s).aw.db"

  bash scripts/migrate_db.sh >/dev/null
  python3 src/oxl_ansible_webui/ 2>&1 | grep -E 'ERROR|FATAL|Warning: operationId|Except'  &
else
  export AW_ENV='staging'
  bash scripts/migrate_db.sh
  python3 src/oxl_ansible_webui/ &
fi

echo ''
sleep 10
