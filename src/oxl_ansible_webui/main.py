from platform import uname
from os import environ, getpid

from django import setup as django_setup

from aw.config.main import init_config

# pylint: disable=C0413,C0415

environ['AW_INIT'] = '1'
init_config()

from aw.utils.debug import log


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw.settings')

    from aw.config.load_file import load_config_file, check_for_bad_config
    load_config_file()
    check_for_bad_config()

    from db import install_or_migrate_db

    environ['MAINPID'] = str(getpid())
    install_or_migrate_db()

    django_setup()
    environ['AW_INIT'] = '0'

    from db import create_first_superuser, create_manager_groups, cleanup_executions, create_schedule_user
    from handle_signals import handle_signals
    from webserver import init_webserver
    from aw.execute.scheduler import init_scheduler
    from aw.settings import AUTH_MODE

    log(msg=f"Using Auth-Mode: {AUTH_MODE}", level=4)

    create_first_superuser()
    create_manager_groups()
    create_schedule_user()
    cleanup_executions()
    init_scheduler(handle_signals)
    init_webserver()
