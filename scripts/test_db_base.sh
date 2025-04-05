export AW_TEST_DB=1
source ./scripts/test_base.sh

echo 'Create API key'
api_key="$(python3 src/oxl_ansible_webui/cli.py -a api-key.create -p "$AW_ADMIN" | grep 'Key=' | cut -d '=' -f2)"
export AW_API_KEY="$api_key"
sleep 1

if ! python3 test/integration/api/minimal.py
then
  failure
fi

export AW_CONFIG=''
