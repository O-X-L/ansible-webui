from pathlib import Path

from helpers import api_request, check_job_status_until_scheduled_finished_or_timeout


def test_scheduled_execution(jid: int = 6):
    print('\nSCHEDULED EXECUTION | ADD JOB')
    api_request(
        'job',
        'post',
        {
            'name': f'job{jid}', 'playbook_file': 'play1.yml', 'schedule': '* * * * *', 'enabled': True,
        }
    )

    print('SCHEDULED EXECUTION | WAIT FOR IT')
    e = check_job_status_until_scheduled_finished_or_timeout(jid, 0)

    assert e['user_name'] == 'schedule'
    assert e['status_name'] == 'Finished'
    assert e['time_fin'] is not None
    assert e['failed'] is False
    assert e['job_comment'] is None
    assert e['comment'] == 'Scheduled'
    assert e['command'] == 'ansible-playbook play1.yml'
    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()
