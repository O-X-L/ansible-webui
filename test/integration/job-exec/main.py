from os import environ
from pathlib import Path
from shutil import rmtree
from time import sleep, time
from sys import exit as sys_exit

from requests import Session

# pylint: disable=R0801

BASE_URL = 'http://127.0.0.1:8000/api'
API_USER = environ['AW_ADMIN']
API_KEY = environ['AW_API_KEY']
SINGLE_TIMEOUT = 10

api = Session()
api.headers['X-Api-Key'] = API_KEY
api.headers['accept'] = 'application/json'


def _api_request(location: str, method: str = None, data: dict = None) -> dict:
    url = f'{BASE_URL}/{location}'

    if method is None:
        method = 'get'

    print(f' > {method.upper()} {location}')

    res = None
    if method == 'get':
        res = api.get(url)

    if method == 'post':
        res = api.post(url=url, data=data)

    if method == 'put':
        res = api.put(url=url, data=data)

    if method == 'delete':
        res = api.delete(url)

    if res is None:
        print('ERROR: Empty response')
        sys_exit(1)

    if not res.ok:
        # pylint: disable=W0212
        print('ERROR: BAD RESPONSE', res._content)
        sys_exit(1)

    return res.json()


def _check_status_until_finished_or_timeout(job_id: int, exec_count: int):
    time_start = time()
    e = None
    while time() - SINGLE_TIMEOUT < time_start:
        res = _api_request(f'job/{job_id}?executions=true', 'get')
        assert 'executions' in res and len(res['executions']) == exec_count
        e = res['executions'][0]

        if e['status_name'] in ['Waiting', 'Running']:
            sleep(1)
            continue

        print(' =>', e)
        return e

    print(' =>', e)
    raise TimeoutError()


def test_simple(jid: int = 1):
    print('SIMPLE | ADD JOB')
    _api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml', 'limit': 'srv1',
        }
    )

    print('SIMPLE | EXECUTE')
    _api_request(f'job/{jid}', 'post')

    print('SIMPLE | CHECK')
    e = _check_status_until_finished_or_timeout(jid, 1)

    assert e['user_name'] == API_USER
    assert e['status_name'] == 'Finished'
    assert e['time_fin'] is not None
    assert e['failed'] is False
    assert e['job_comment'] is None
    assert e['comment'] is None
    assert e['command'] == 'ansible-playbook -i inv/empty.yml --limit srv1 play1.yml'
    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()


def test_params(jid: int = 2):
    print('\nPARAMS | ADD JOB')
    _api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
        }
    )

    print('PARAMS | EXECUTE (vars, modes & comment)')
    cmd_args = '-e test=run2'
    comment = 'Test XYZ'
    env_var = 'SomeRandomValue'
    _api_request(
        f'job/{jid}',
        'post',
        {
            'cmd_args': cmd_args, 'comment': comment, 'mode_check': True, 'mode_diff': True,
            'environment_vars': f'TEST1_VAR2={env_var}',
        }
    )

    print('PARAMS | CHECK (vars, modes & comment)')
    e = _check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['comment'] == comment
    assert e['command'] == f'ansible-playbook {cmd_args} --check --diff -i inv/empty.yml play1.yml'
    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()

    with open(e['log_stdout'], 'r', encoding='utf-8') as f:
        log = f.read()
        assert log.find(f'ENV VAR: {env_var}') != -1


    print('\nPARAMS | EXECUTE (limit & tags)')
    limit = 'srv2'
    tags = 'database'
    tags_skip = 'webserver'
    _api_request(
        'job/2',
        'post',
        {'tags': tags, 'tags_skip': tags_skip, 'mode_check': True, 'limit': limit}
    )

    print('PARAMS | CHECK (limit & tags)')
    e = _check_status_until_finished_or_timeout(2, 2)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['command'] == (f'ansible-playbook --check -i inv/empty.yml --limit {limit} --tags {tags} '
                            f'--skip-tags {tags_skip} play1.yml')


def test_creds(jid: int = 3):
    print('\nCREDS | ADD JOB')
    _api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
            'credentials_needed': True,
        }
    )

    print('CREDS | ADD CREDS')
    become_user = 'admin'
    connect_user = 'tester'
    _api_request(
        'credentials/user',
        'post',
        {
            'name': 'myUser', 'become_user': become_user, 'become_pass': 'hup', 'connect_user': connect_user,
            'connect_pass': 'sdfk', 'vault_pass': 'secUry',
        }
    )

    print('CREDS | EXECUTE (connect, become & vault pass)')
    _api_request(
        f'job/{jid}',
        'post',
        {'credentials_user': 1},
    )

    print('CREDS | CHECK (connect, become & vault pass)')
    e = _check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['command'] == (f'ansible-playbook --ask-become-pass --become-user {become_user} --ask-pass '
                            f'--user {connect_user} --ask-vault-pass -i inv/empty.yml play1.yml')

    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()

    # todo: test more combinations to catch edge-cases in credential-handling
    # todo: create tmp-credentials and make sure they are removed/cleaned after execution


def test_repo_git(jid: int = 4):
    print('\nREPO GIT | ADD REPO')
    repo = f'myRepo-{int(time())}'
    origin = 'https://github.com/O-X-L/ansible-webui.git'
    branch = 'latest'
    _api_request(
        'repository',
        'post',
        {
            'name': repo, 'rtype': 2, 'git_origin': origin, 'git_branch': branch, 'git_playbook_base': 'test',
            'isolate': False,
        }
    )

    print('REPO GIT | ADD JOB')
    _api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
            'repository': 1,
        }
    )

    print('REPO GIT | EXECUTE (not isolated)')
    rmtree(f'/tmp/ansible-webui/repositories/{repo}', ignore_errors=True)  # clean auto-downloaded repo
    _api_request(
        f'job/{jid}',
        'post',
    )

    print('REPO GIT | CHECK (not isolated)')
    e = _check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['log_stdout_repo'] is not None
    assert Path(e['log_stdout_repo']).is_file()

    with open(e['log_stdout_repo'], 'r', encoding='utf-8') as f:
        log = f.read()
        assert log.find(f'git clone --branch {branch} {origin} /tmp/ansible-webui/repositories/{repo}') != -1

    # todo: execute with isolation


def test_execution_cleanup(jid: int = 1, exec_id: int = 1):
    print('EXEC CLEANUP | DELETE')
    _api_request(f'job/{jid}/{exec_id}/cleanup', 'delete')

    print('EXEC CLEANUP | CHECK')
    sleep(1)
    res = _api_request(f'job/{jid}?executions=true', 'get')
    assert 'executions' in res
    e = res['executions']
    print(' =>', e)
    assert len(e) == 0



def main():
    test_simple()
    test_params()
    test_creds()
    test_repo_git()
    test_execution_cleanup()


if __name__ == '__main__':
    main()
