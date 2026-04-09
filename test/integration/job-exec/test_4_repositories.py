from time import time
from pathlib import Path
from shutil import rmtree

from helpers import api_request, check_status_until_finished_or_timeout


def test_repo_git(jid: int = 4):
    path_repo_base = '/tmp/ansible-webui/repositories'

    print('\nREPO GIT | ADD REPO')
    repo = f'myRepo-{int(time())}'
    origin = 'https://github.com/O-X-L/ansible-webui.git'
    branch = 'latest'
    repo_id = 1
    path_repo = f'{path_repo_base}/{repo_id}_{repo}'

    api_request(
        'repository',
        'post',
        {
            'name': repo, 'rtype': 2, 'git_origin': origin, 'git_branch': branch, 'git_playbook_base': 'test',
            'git_isolate': False,
        }
    )

    print('REPO GIT | ADD JOB')
    api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
            'repository': repo_id,
        }
    )

    print('REPO GIT | EXECUTE')
    rmtree(path_repo, ignore_errors=True)  # clean pre-existing repo
    api_request(
        f'job/{jid}',
        'post',
    )

    print('REPO GIT | CHECK')
    e = check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['log_stdout_repo'] is not None
    assert Path(e['log_stdout_repo']).is_file()

    with open(e['log_stdout_repo'], 'r', encoding='utf-8') as f:
        log = f.read()
        assert log.find(f'git clone --branch {branch} {origin} {path_repo}') != -1

    # ISOLATED
    repo = f'myRepo-{int(time())}'
    repo_id = 2
    exec_id = e['id'] + 1
    path_repo = f"{path_repo_base}/isolated/{repo_id}_{repo}/{exec_id}"

    api_request(
        'repository',
        'post',
        {
            'name': repo, 'rtype': 2, 'git_origin': origin, 'git_branch': branch, 'git_playbook_base': 'test',
            'git_isolate': True,
        }
    )

    print('REPO GIT-ISOLATED | UPDATE JOB')
    api_request(
        f'job/{jid}',
        'put',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
            'repository': repo_id,
        }
    )

    print('REPO GIT-ISOLATED | EXECUTE')
    rmtree(path_repo, ignore_errors=True)  # clean pre-existing repo
    api_request(
        f'job/{jid}',
        'post',
    )

    print('REPO GIT-ISOLATED | CHECK')
    e = check_status_until_finished_or_timeout(jid, 2)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['log_stdout_repo'] is not None
    assert Path(e['log_stdout_repo']).is_file()

    with open(e['log_stdout_repo'], 'r', encoding='utf-8') as f:
        log = f.read()
        assert log.find(f"git clone --branch {branch} {origin} {path_repo}") != -1
