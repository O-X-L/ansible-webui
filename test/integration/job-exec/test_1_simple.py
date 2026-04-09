from pathlib import Path

from config import API_USER, AW_EXECUTOR
from helpers import api_request, check_status_until_finished_or_timeout


def test_simple(jid: int = 1):
    print('SIMPLE | ADD JOB')
    api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/empty.yml', 'limit': 'srv1',
        }
    )

    print('SIMPLE | EXECUTE')
    api_request(f'job/{jid}', 'post')

    print('SIMPLE | CHECK')
    e = check_status_until_finished_or_timeout(jid, 1)

    assert e['user_name'] == API_USER
    assert e['status_name'] == 'Finished'
    assert e['time_fin'] is not None
    assert e['failed'] is False
    assert e['job_comment'] is None
    assert e['comment'] is None

    if AW_EXECUTOR == 'oxl-ansible-executor':
        assert e['command'] == 'ansible-playbook -i inv/empty.yml -l srv1 play1.yml'

    else:
        assert e['command'] == 'ansible-playbook -i inv/empty.yml --limit srv1 play1.yml'

    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()
