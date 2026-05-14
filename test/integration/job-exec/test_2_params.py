from pathlib import Path

from config import AW_EXECUTOR
from helpers import api_request, check_status_until_finished_or_timeout


def test_params(jid: int = 2):
    print('\nPARAMS | ADD JOB')
    api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml',
        }
    )

    print('PARAMS | EXECUTE (vars, modes, extra-vars & comment)')
    cmd_args = '-e test=run2'
    comment = 'Test XYZ'
    env_var = 'SomeRandomValue'
    extra_vars_json = '{"service":"apache2","port":8080}'
    api_request(
        f'job/{jid}',
        'post',
        {
            'cmd_args': cmd_args, 'comment': comment, 'mode_check': True, 'mode_diff': True,
            'environment_vars': f'TEST1_VAR2={env_var}', 'extra_vars': extra_vars_json,
        }
    )

    print('PARAMS | CHECK (vars, modes & comment)')
    e = check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False
    assert e['comment'] == comment

    if AW_EXECUTOR == 'oxl-ansible-executor':
        assert e['command'] == f'ansible-playbook -i inv/empty.yml -C -D -e {extra_vars_json} {cmd_args} play1.yml'

    else:
        assert e['command'] == (f'ansible-playbook {cmd_args} --check --diff -i inv/empty.yml -e {extra_vars_json} '
                                f'play1.yml')

    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()

    with open(e['log_stdout'], 'r', encoding='utf-8') as f:
        log = f.read()
        assert log.find(f'ENV VAR: {env_var}') != -1


    print('\nPARAMS | EXECUTE (limit & tags)')
    limit = 'srv2'
    tags = 'database'
    tags_skip = 'webserver'
    api_request(
        'job/2',
        'post',
        {'tags': tags, 'tags_skip': tags_skip, 'mode_check': True, 'limit': limit}
    )

    print('PARAMS | CHECK (limit & tags)')
    e = check_status_until_finished_or_timeout(2, 2)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False

    if AW_EXECUTOR == 'oxl-ansible-executor':
        assert e['command'] == (f'ansible-playbook -i inv/empty.yml -C -l {limit} -t {tags} '
                                f'--skip-tags {tags_skip} play1.yml')

    else:
        assert e['command'] == (f'ansible-playbook --check -i inv/empty.yml --limit {limit} --tags {tags} '
                                f'--skip-tags {tags_skip} play1.yml')
