from time import time
from pathlib import Path
from shutil import copy, move
from os import listdir, remove
from datetime import datetime
from sys import exit as sys_exit
from secrets import choice as random_choice
from string import digits, ascii_letters
from sqlite3 import connect as db_connect
from sqlite3 import OperationalError as SQLiteOperationalError
from sqlite3 import DatabaseError as SQLiteDatabaseError

from aw.config.main import VERSION
from aw.settings import DB_FILE
from aw.utils.subps import process
from aw.utils.debug import log, log_error, log_warn
from aw.utils.deployment import deployment_prod
from aw.config.hardcoded import FILE_TIME_FORMAT, GRP_MANAGER
from aw.config.environment import check_aw_env_var_true, get_aw_env_var, check_aw_env_var_is_set
from aw.dependencies import log_dependency_error

# pylint: disable=C0415

DB_BACKUP_EXT = '.auto.bak'
DB_BACKUP_RETENTION_DAYS = 7

if not deployment_prod():
    DB_BACKUP_RETENTION_DAYS = 1

DB_BACKUP_RETENTION = DB_BACKUP_RETENTION_DAYS * 24 * 60 * 60
DB_TYPE = get_aw_env_var('db_type')
if DB_TYPE is None or DB_TYPE not in ['mysql', 'psql', 'sqlite']:
    DB_TYPE = 'sqlite'


class DummyException(BaseException):
    pass


try:
    from MySQLdb import connect as mysql_connect
    from MySQLdb._exceptions import MySQLError

except (ImportError, ModuleNotFoundError):
    if DB_TYPE == 'mysql':
        log_dependency_error('MySQL', 'mysql')
        raise EnvironmentError('Database-client dependencies are missing!')

    MySQLError = DummyException

try:
    from psycopg import connect as psql_connect
    from psycopg.errors import Error as PSQLError

except (ImportError, ModuleNotFoundError):
    if DB_TYPE == 'psql':
        log_dependency_error('PostgreSQL', 'psql')
        raise EnvironmentError('Database-client dependencies are missing!')

    PSQLError = DummyException


class AbstractDBConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        if DB_TYPE == 'sqlite':
            self.connection = db_connect(DB_FILE)

        elif DB_TYPE == 'mysql':
            port = get_aw_env_var('db_port')
            if port is not None:
                port = int(port)

            # pylint: disable=I1101
            self.connection = mysql_connect(
                host=get_aw_env_var('db_host'),
                port=port,
                user=get_aw_env_var('db_user'),
                password=get_aw_env_var('db_pwd'),
                database=get_aw_env_var('db'),
            )
            self.cursor = self.connection.cursor()

        elif DB_TYPE == 'psql':
            self.connection = psql_connect(
                host=get_aw_env_var('db_host'),
                port=get_aw_env_var('db_port'),
                user=get_aw_env_var('db_user'),
                password=get_aw_env_var('db_pwd'),
                dbname=get_aw_env_var('db'),
            )
            self.cursor = self.connection.cursor()

        else:
            raise ValueError(f"Got unsupported DB-Type: '{DB_TYPE}'")

        return self

    def __exit__(self, a, b, c):
        del a, b, c
        if self.cursor is not None:
            self.cursor.close()

        self.connection.close()

    def execute(self, cmd: str) -> None:
        if DB_TYPE == 'sqlite':
            self.connection.execute(cmd)

        else:
            self.cursor.execute(cmd)

        self.connection.commit()

    def query(self, cmd: str) -> tuple:
        if DB_TYPE == 'sqlite':
            return self.connection.execute(cmd).fetchone()

        self.cursor.execute(cmd)
        return self.cursor.fetchone()


def _sqlite_check_if_writable():
    try:
        test_file = DB_FILE.parent / '.awtest'
        with open(test_file, 'w', encoding='utf-8') as _file:
            _file.write('TEST')

        remove(test_file)

    except PermissionError:
        log(msg=f"Error: DB directory is not writable: '{DB_FILE.parent}'")
        sys_exit(1)


def _schema_up_to_date_base() -> bool:
    with AbstractDBConnection() as db:
        try:
            return db.query('SELECT schema_version FROM aw_schemametadata')[0] == VERSION

        except (IndexError, TypeError, SQLiteOperationalError, MySQLError, PSQLError):
            return False


def _schema_up_to_date() -> bool:
    if DB_TYPE == 'sqlite' and not Path(DB_FILE).is_file():
        return False

    try:
        return _schema_up_to_date_base()

    except SQLiteDatabaseError as err:
        # this may happen if WAL or SHM got corrupted (p.e. connection was not closed gracefully)
        log_warn(msg=f"Trying to fix database error: '{err}'", _stderr=True)
        backup_ext = f".{datetime.now().strftime(FILE_TIME_FORMAT)}{DB_BACKUP_EXT}"
        db_shm = f'{DB_FILE}-shm'
        db_wal = f'{DB_FILE}-wal'

        if Path(db_shm).is_file():
            move(db_shm, f'{db_shm}{backup_ext}')

        if Path(db_wal).is_file():
            move(db_wal, f'{db_wal}{backup_ext}')

        return _schema_up_to_date_base()


# NOTE: we have to do this manually as django is not initialized yet
def _get_schema_insert() -> str:
    if DB_TYPE in ['mysql', 'psql']:
        return ("INSERT INTO aw_schemametadata (created, updated, schema_version) VALUES "
                f"(NOW(), NOW(), '{VERSION}')")

    return ("INSERT INTO aw_schemametadata (created, updated, schema_version) VALUES "
            f"(DATETIME('now'), DATETIME('now'), '{VERSION}')")


def _get_schema_update(prev: str) -> str:
    if DB_TYPE in ['mysql', 'psql']:
        return ("UPDATE aw_schemametadata SET "
                f"schema_version = '{VERSION}', schema_version_prev = '{prev}', "
                "updated = NOW() WHERE id = 1")

    return ("UPDATE aw_schemametadata SET "
            f"schema_version = '{VERSION}', schema_version_prev = '{prev}', "
            "updated = DATETIME('now') WHERE id = 1")


def _update_schema_version() -> None:
    with AbstractDBConnection() as db:
        try:
            previous = db.query('SELECT schema_version FROM aw_schemametadata')[0]

        except (IndexError, TypeError, SQLiteOperationalError, MySQLError, PSQLError):
            previous = None

        try:
            if previous is not None:
                db.execute(_get_schema_update(previous))

            else:
                db.execute(_get_schema_insert())

        except (IndexError, SQLiteOperationalError, MySQLError, PSQLError) as err:
            log(msg=f"Unable to update database schema version: '{err}'", level=3)


def install_or_migrate_db():
    if DB_TYPE in ['mysql', 'psql']:
        return net_install_migrate()

    log(msg=f"Using DB: {DB_FILE}", level=4)
    _sqlite_check_if_writable()
    if not Path(DB_FILE).is_file():
        return sqlite_install()

    return sqlite_migrate()


def _manage_db(action: str, cmd: list, backup: str = None) -> dict:
    cmd2 = ['python3', 'manage.py']
    cmd2.extend(cmd)

    result = process(cmd=cmd2)

    if result['rc'] != 0:
        log_error(f'Database {action} failed!')
        log(msg=f"Error:\n{result['stderr']}", level=1)
        log(msg=f"Output:\n{result['stdout']}", level=3)

        if backup is not None:
            log_warn(
                msg=f"Trying to restore database from automatic backup: {backup} => {DB_FILE}",
                _stderr=True,
            )
            copy(src=DB_FILE, dst=f'{backup}.failed')
            copy(src=backup, dst=DB_FILE)

        else:
            sys_exit(1)

    return result


def _sqlite_clean_old_db_backups():
    possible_db_backup_files = listdir(DB_FILE.parent)
    for file in possible_db_backup_files:
        if file.startswith(DB_FILE.name) and file.endswith(DB_BACKUP_EXT):
            backup_file = DB_FILE.parent / file
            backup_age = time() - backup_file.stat().st_mtime
            if backup_age > DB_BACKUP_RETENTION:
                log(msg=f"Cleaning old backup file: '{backup_file}'", level=4)
                remove(backup_file)


def sqlite_install():
    log(msg=f"Initializing database {DB_FILE}..", level=3)
    _manage_db(action='initialization', cmd=['migrate'])
    _update_schema_version()


def sqlite_migrate():
    _sqlite_clean_old_db_backups()

    if not _schema_up_to_date() and check_aw_env_var_true(var='db_migrate', fallback=True):
        backup = f"{DB_FILE}.{datetime.now().strftime(FILE_TIME_FORMAT)}{DB_BACKUP_EXT}"
        log(msg=f"Creating database backup: '{backup}'", level=6)
        copy(src=DB_FILE, dst=backup)

        log(msg=f"Upgrading database {DB_FILE}", level=3)
        if _manage_db(action='migration', cmd=['migrate'], backup=backup)['rc'] == 0:
            _update_schema_version()


def net_install_migrate():
    # user@host:port/name
    db_host = get_aw_env_var('db_host')
    db_port = get_aw_env_var('db_port')
    db_name = get_aw_env_var('db')
    db_user = get_aw_env_var('db_user')
    db = ''

    if db_user is not None:
        db += f'{db_user}@'

    if db_host is not None:
        db += db_host

    if db_port is not None:
        db += f':{db_port}'

    if db_name is not None:
        if db == '':
            db = db_name
        else:
            db += f'/{db_name}'

    log(msg=f"Using DB: {db}", level=4)
    _manage_db(action='migration', cmd=['migrate'])
    _update_schema_version()


def _get_random_pwd() -> str:
    return ''.join(random_choice(ascii_letters + digits + '!.-+') for _ in range(14))


def create_first_superuser():
    from aw.base import USERS
    if len(USERS.objects.filter(is_superuser=True)) == 0:
        name = get_aw_env_var('init_admin')
        pwd = get_aw_env_var('init_admin_pwd')

        if name is None:
            name = 'ansible'

        if pwd is None:
            pwd = _get_random_pwd()

        USERS.objects.create_superuser(
            username=name,
            email=f"{name}@localhost",
            password=pwd
        )

        log_warn('No admin was found in the database!')
        if check_aw_env_var_is_set('init_admin_pwd'):
            log(msg=f"The user '{name}' was created!", level=4)

        else:
            log(msg=f"Generated user: '{name}'", level=3)
            log(msg=f"Generated pwd: '{pwd}'", level=3)
            log_warn('Make sure to change the password!')


def create_manager_groups():
    from django.contrib.auth.models import Group
    for grp in GRP_MANAGER.values():
        Group.objects.get_or_create(name=grp)


def create_schedule_user():
    # just to reserve the username as it is referenced internally
    from aw.base import USERS
    if len(USERS.objects.filter(username='schedule')) == 0:
        USERS.objects.create(
            username='schedule',
            email='schedule@localhost',
            password=_get_random_pwd(),
        )


def cleanup_executions():
    from aw.model.base import JOB_EXEC_STATI_ACTIVE, JOB_EXEC_STATUS_FAILED
    from aw.model.job import JobExecution
    from aw.model.job_credential import JobUserTMPCredentials

    JobExecution.objects.filter(status__in=JOB_EXEC_STATI_ACTIVE).update(status=JOB_EXEC_STATUS_FAILED)
    JobUserTMPCredentials.objects.all().delete()
