from os import environ
from pathlib import Path
from getpass import getuser

from ansibleguy_runner.interface import get_ansible_config

from aw.utils.subps import process_cache
from aw.utils.version import get_system_versions, parsed_ansible_version, parsed_python_modules, get_version


def _parsed_ansible_collections() -> list[dict]:
    result = process_cache('ansible-galaxy collection list')
    if result['rc'] != 0:
        return []

    collections = []
    processed = []
    col_counter = {}
    collection_path = ''
    for line in result['stdout'].split('\n'):
        if line.startswith('#'):
            collection_path = line[1:]
            continue

        if line.find('.') == -1:
            continue

        name, version = line.split(' ', 1)
        name, version = name.strip(), version.strip()

        if name in processed:
            if name in col_counter:
                col_counter[name] += 1
            else:
                col_counter[name] = 2

            name = f'{name} ({col_counter[name]})'

        collections.append({'name': name, 'version': version, 'path': collection_path})
        processed.append(name)

    return collections


def _parsed_ansible_config() -> list[dict]:
    environ['ANSIBLE_FORCE_COLOR'] = '0'
    ansible_config_raw = get_ansible_config(action='dump', quiet=True)[0].split('\n')
    environ['ANSIBLE_FORCE_COLOR'] = '1'
    ansible_config = []

    for line in ansible_config_raw:
        try:
            setting_comment, value = line.split('=', 1)

        except ValueError:
            continue

        setting_comment, value = setting_comment.strip(), value.strip()
        try:
            setting, comment = setting_comment.rsplit('(', 1)
            comment = comment.replace(')', '')

        except ValueError:
            setting, comment = setting_comment, '-'

        ansible_config.append({'setting': setting, 'value': value, 'comment': comment})

    return ansible_config


def _parsed_aws_versions() -> dict:
    versions = {'AWS Session-Manager-Plugin': None, 'AWS CLI': None}
    if Path('/usr/bin/session-manager-plugin').is_file():
        versions['AWS Session-Manager-Plugin'] = process_cache('/usr/bin/session-manager-plugin --version')['stdout']

    if Path('/usr/bin/aws').is_file():
        versions['AWS CLI'] = process_cache('/usr/bin/aws --version')['stdout']

    return versions


def _parsed_ara_version(python_modules: dict) -> (str, None):
    if 'ara' not in python_modules:
        return None

    return python_modules['ara']['version']


def _parsed_ansible_playbook() -> str:
    ap = process_cache('which ansible-playbook')
    if ap['rc'] != 0:
        return 'Not Found'

    return ap['stdout']


def get_system_environment() -> dict:
    # todo: allow to check for updates (pypi, ansible-galaxy & github api)
    python_modules = parsed_python_modules()
    ansible_version = parsed_ansible_version(python_modules)
    env_system = get_system_versions(python_modules=python_modules, ansible_version=ansible_version)

    return {
        **env_system,
        **_parsed_aws_versions(),
        'Ansible WebUI': get_version(),
        'User': getuser(),
        'Ansible ARA': _parsed_ara_version(python_modules),
        'Ansible Playbook': _parsed_ansible_playbook(),
        # 'ansible_roles': get_role_list(),
        'Python Modules': list(python_modules.values()),
        'Ansible Config': _parsed_ansible_config(),
        'Ansible Collections': _parsed_ansible_collections(),
    }
