from django.contrib.admin.models import LogEntry, ADDITION

from aw.base import USERS
from aw.config.main import config
from aw.utils.debug import log
from aw.utils.db_handler import close_old_mysql_connections


def log_audit(user: USERS, title: str, msg: str):
    # todo: add model change-diff (of non-secret parameters) to log-message

    if not config['audit_log']:
        return

    log(f"AUDIT: Action: '{title}' | User: '{user.username}' | {msg}", level=4)

    close_old_mysql_connections()
    LogEntry(
        user=user,
        object_repr=title,
        change_message=msg,
        action_flag=ADDITION,
    ).save()
