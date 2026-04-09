from pathlib import Path

from config import AW_EXECUTOR
from helpers import api_request, check_status_until_finished_or_timeout


def test_creds(jid: int = 3):
    print('\nCREDS | ADD JOB')
    api_request(
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
    api_request(
        'credentials/user',
        'post',
        {
            'name': 'myUser', 'become_user': become_user, 'become_pass': 'hup', 'connect_user': connect_user,
            'connect_pass': 'sdfk', 'vault_pass': 'secUry',
        }
    )

    print('CREDS | EXECUTE (connect, become & vault pass)')
    api_request(
        f'job/{jid}',
        'post',
        {'credentials_user': 1},
    )

    print('CREDS | CHECK (connect, become & vault pass)')
    e = check_status_until_finished_or_timeout(jid, 1)

    assert e['status_name'] == 'Finished'
    assert e['failed'] is False

    if AW_EXECUTOR == 'oxl-ansible-executor':
        # we have no way of knowing the random temporary credentials-paths here
        assert e['command'].startswith('ansible-playbook -i inv/empty.yml -u ')
        assert '--conn-pass-file' in e['command']
        assert '--become-pass-file' in e['command']
        assert '--vault-pass-file' in e['command']
        assert e['command'].endswith(' play1.yml')

    else:
        assert e['command'] == (f'ansible-playbook --ask-become-pass --become-user {become_user} --ask-pass '
                                f'--user {connect_user} --ask-vault-pass -i inv/empty.yml play1.yml')

    assert e['log_stdout'] is not None
    assert Path(e['log_stdout']).is_file()

    # todo: test more combinations to catch edge-cases in credential-handling
    # todo: create tmp-credentials and make sure they are removed/cleaned after execution
