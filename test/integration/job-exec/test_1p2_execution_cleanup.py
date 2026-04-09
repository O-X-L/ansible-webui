from time import sleep

from helpers import api_request


def test_execution_cleanup(jid: int = 1, exec_id: int = 1):
    print('\nEXEC CLEANUP | DELETE')
    api_request(f'job/{jid}/{exec_id}/cleanup', 'delete')

    print('EXEC CLEANUP | CHECK')
    sleep(1)
    res = api_request(f'job/{jid}?executions=true', 'get')
    assert 'executions' in res
    e = res['executions']
    print(' =>', e)
    assert len(e) == 0
