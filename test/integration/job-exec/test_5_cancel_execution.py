from time import sleep
from pathlib import Path

from config import API_USER
from helpers import api_request, check_status_until_canceled_or_timeout, check_status_until_running_or_timeout


def test_user_cancels(jid: int = 5):
    print('\nUSER CANCELS | ADD JOB')
    cmd_args = '-e test=run3'  # just waits until it can be stopped
    api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'cmd_args': cmd_args,
        }
    )

    print('USER CANCELS | EXECUTE')
    create_response = api_request(f'job/{jid}', 'post')
    exec_id = create_response['id']

    print('USER CANCELS | WAIT FOR IT TO START')
    check_status_until_running_or_timeout(jid, 1)
    sleep(1)

    print('USER CANCELS | STOPPING JOB')
    api_request(f'job/{jid}/{exec_id}', 'delete')

    print('USER CANCELS | CHECK')
    e = check_status_until_canceled_or_timeout(jid, 1)

    assert e['user_name'] == API_USER
    assert e['status_name'] == 'Stopped'
    assert e['time_fin'] is not None
    assert e['failed'] is False
    assert e['command'] == f'ansible-playbook {cmd_args} play1.yml'
    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()
