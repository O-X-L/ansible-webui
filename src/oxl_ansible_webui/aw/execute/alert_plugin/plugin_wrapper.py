from pathlib import Path
from time import time
from time import mktime as unix_timestamp
from json import dumps as json_dumps
from os import remove as remove_file

from django.core.exceptions import ObjectDoesNotExist

from aw.config.main import config
from aw.base import USERS
from aw.utils.debug import log
from aw.utils.subps import process
from aw.utils.util import datetime_from_db, write_file_0600
from aw.model.system import UserExtended
from aw.settings import get_main_web_address
from aw.model.job import JobExecution
from aw.model.alert import BaseAlert, AlertUser, AlertGroup
from aw.utils.db_handler import close_old_mysql_connections


def alert_plugin_wrapper(
        alert: BaseAlert, user: USERS, stats: dict, execution: JobExecution, failed: bool,
        error_msgs: dict,
):
    if not Path(alert.plugin.executable).is_file():
        log(
            msg=f"Alert plugin has an invalid executable configured: {alert.name} ({alert.plugin.executable})",
            level=3,
        )
        return

    url = get_main_web_address()

    data = {
        'alert': {
            'type': 'global',
            'condition': alert.condition_name.lower(),
        },
        'user': {
            'name': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': '',
            'description': '',
            'is_active': user.is_active,
            'last_login': int(unix_timestamp(datetime_from_db(user.last_login).timetuple())),
            'groups': [group.name for group in user.groups.all()],
        },
        'execution': {
            'failed': failed,
            'status': execution.status_name,
            'job_name': execution.job.name,
            'job_id': execution.job.id,
            'execution_id': execution.id,
            'user_name': execution.user_name,
            'time_start': int(unix_timestamp(execution.time_created_dt.timetuple())),
            'time_start_pretty': execution.time_created_str,
            'time_fin': None,
            'time_fin_pretty': None,
            'time_duration': None,
            'time_duration_pretty': None,
            'error_short': None,
            'error_med': None,
            'log_url': f"{url}/ui/jobs/log?job={execution.job.id}",
        },
        'errors': error_msgs,
        'stats': stats,
    }

    try:
        close_old_mysql_connections()
        user_extended = UserExtended.objects.get(user=user)
        data['user']['phone'] = user_extended.phone
        data['user']['description'] = user_extended.description

    except ObjectDoesNotExist:
        pass

    if isinstance(alert, AlertUser):
        data['alert']['type'] = 'user'

    elif isinstance(alert, AlertGroup):
        data['alert']['type'] = 'group'

    if execution.result is not None:
        data['execution']['time_fin'] = int(unix_timestamp(execution.result.time_fin_dt.timetuple()))
        data['execution']['time_fin_pretty'] = execution.result.time_fin_str
        data['execution']['time_duration'] = execution.result.time_duration_sec
        data['execution']['time_duration_pretty'] = execution.result.time_duration_str

        if execution.result.error is not None:
            data['execution']['error_short'] = execution.result.error.short
            data['execution']['error_med'] = execution.result.error.med

    for log_attr in JobExecution.log_file_fields:
        url_attr = f'{log_attr}_url'
        file = getattr(execution, log_attr)
        if Path(file).is_file():
            data['execution'][log_attr] = file
            data['execution'][url_attr] = f"{url}{getattr(execution, url_attr)}"

        else:
            data['execution'][log_attr] = None
            data['execution'][url_attr] = None

    tmp_file = f"{config['path_run']}/.aw_alert_{time()}.json"
    write_file_0600(
        file=tmp_file,
        content=json_dumps(data),
    )

    cmd = alert.plugin.executable.split(' ')
    cmd.append(tmp_file)
    result = process(cmd=cmd, timeout_sec=5)

    if result['rc'] != 0:
        log(f"Alert plugin failed! Output: '{result['stdout']}' | Error: '{result['stderr']}'")

    log(msg=f"Executed alert plugin '{alert.plugin.name}' targeting user: {user.username}", level=6)

    remove_file(tmp_file)
