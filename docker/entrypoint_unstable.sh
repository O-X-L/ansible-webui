#!/bin/sh

. /entrypoint_requirements.sh

echo 'INSTALLING/UPGRADING latest..'
pip install --no-warn-script-location --upgrade --force-reinstall --no-cache-dir --root-user-action=ignore --no-warn-script-location "git+https://github.com/O-X-L/ansible-webui.git@latest" >/dev/null

oxl-ansible-webui
