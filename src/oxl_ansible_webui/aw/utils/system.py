from os import environ
from pathlib import Path
from getpass import getuser

from ansibleguy_runner.interface import get_ansible_config

from aw.utils.subps import process_cache
from aw.utils.version import get_system_versions, parsed_ansible_version, parsed_python_modules, get_version


def _parsed_ansible_collections() -> dict:
    result = process_cache('ansible-galaxy collection list')
    if result['rc'] != 0:
        return {}

    collections = {}
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
        url = f"https://galaxy.ansible.com/ui/repo/published/{name.replace('.', '/')}"

        if name in collections:
            if name in col_counter:
                col_counter[name] += 1
            else:
                col_counter[name] = 2

            name = f'{name} ({col_counter[name]})'

        collections[name] = {'version': version, 'path': collection_path, 'url': url}

    return dict(sorted(collections.items()))


def _parsed_ansible_config() -> dict:
    environ['ANSIBLE_FORCE_COLOR'] = '0'
    ansible_config_raw = get_ansible_config(action='dump', quiet=True)[0].split('\n')
    environ['ANSIBLE_FORCE_COLOR'] = '1'
    ansible_config = {}

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

        url = ("https://docs.ansible.com/ansible/latest/reference_appendices/config.html#"
               f"{setting.lower().replace('_', '-')}")

        ansible_config[setting] = {'value': value, 'comment': comment, 'url': url}

    return dict(sorted(ansible_config.items()))


def _parsed_aws_versions() -> dict:
    versions = {}
    if Path('/usr/bin/session-manager-plugin').is_file():
        versions['session-manager-plugin'] = process_cache('/usr/bin/session-manager-plugin --version')['stdout']

    if Path('/usr/bin/aws').is_file():
        versions['aws-cli'] = process_cache('/usr/bin/aws --version')['stdout']

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
        'aw': get_version(),
        'user': getuser(),
        'aws': _parsed_aws_versions(),
        'ara': _parsed_ara_version(python_modules),
        'python_modules': python_modules,
        'ansible_config': _parsed_ansible_config(),
        'ansible_playbook': _parsed_ansible_playbook(),
        # 'ansible_roles': get_role_list(),
        'ansible_collections': _parsed_ansible_collections(),
    }
