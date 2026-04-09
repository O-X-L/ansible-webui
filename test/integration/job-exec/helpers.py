from pathlib import Path
from time import time, sleep
from sys import exit as sys_exit

from requests import Session

from config import API_KEY, BASE_URL, SINGLE_TIMEOUT, SCHEDULED_TIMEOUT

api = Session()
api.headers['X-Api-Key'] = API_KEY
api.headers['accept'] = 'application/json'


def api_request(location: str, method: str = None, data: dict = None) -> dict:
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


def _check_job_status_until_not_status_or_timeout(job_id: int, exec_count: int, not_status: list[str]) -> (dict, None):
    time_start = time()
    e = None
    while time() - SINGLE_TIMEOUT < time_start:
        res = api_request(f'job/{job_id}?executions=true', 'get')
        assert 'executions' in res and len(res['executions']) == exec_count
        e = res['executions'][0]

        if e['status_name'] in not_status:
            sleep(1)
            continue

        print(' =>', e)
        return e

    raise TimeoutError(f"Last response: {e}")


def check_status_until_running_or_timeout(job_id: int, exec_count: int) -> (dict, None):
    return _check_job_status_until_not_status_or_timeout(
        job_id=job_id,
        exec_count=exec_count,
        not_status=['Waiting', 'Starting'],
    )


def check_status_until_canceled_or_timeout(job_id: int, exec_count: int) -> (dict, None):
    return _check_job_status_until_not_status_or_timeout(
        job_id=job_id,
        exec_count=exec_count,
        not_status=['Waiting', 'Starting', 'Running', 'Stopping'],
    )


def check_status_until_finished_or_timeout(job_id: int, exec_count: int) -> (dict, None):
    e = _check_job_status_until_not_status_or_timeout(
        job_id=job_id,
        exec_count=exec_count,
        not_status=['Waiting', 'Starting', 'Running'],
    )

    if e is not None:
        if e['failed']:
            # verbose output for troubleshooting
            for log_kind, log_key in {'STDOUT': 'log_stdout', 'STDERR': 'log_stderr'}.items():
                if e[log_key] is None or not Path(e[log_key]).is_file():
                    continue

                with open(e[log_key], 'r', encoding='utf-8') as f:
                    print(f' => {log_kind}:')
                    print(f.read())

        return e

    return None


def check_job_status_until_scheduled_finished_or_timeout(job_id: int, exec_nr: int) -> (dict, None):
    time_start = time()
    e = None
    while time() - SCHEDULED_TIMEOUT < time_start:
        res = api_request(f'job/{job_id}?executions=true', 'get')
        if len(res['executions']) < (exec_nr + 1):
            # wait for execution to be started/created
            sleep(1)
            continue

        e = res['executions'][exec_nr]

        if e['status_name'] in ['Waiting', 'Starting', 'Running']:
            # wait for execution to finish
            sleep(1)
            continue

        print(' =>', e)
        return e

    raise TimeoutError(f"Last response: {e}")
