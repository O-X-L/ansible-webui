# pylint: disable=C0415,W0611

from sqlite3 import connect as db_connect
from sqlite3 import OperationalError as SQLiteOperationalError
from sqlite3 import DatabaseError as SQLiteDatabaseError

from aw.config.environment import get_aw_env_var, get_aw_env_var_or_default, CONFIG_DEFAULTS
from aw.dependencies import log_dependency_error

DB_TYPE = get_aw_env_var_or_default('db_type')
if DB_TYPE is None or DB_TYPE not in ['mysql', 'psql', 'sqlite']:
    DB_TYPE = CONFIG_DEFAULTS['db_type']


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
    def __init__(self, db_file: str = None):
        self.connection = None
        self.cursor = None
        self.db_file = db_file

    def __enter__(self):
        if DB_TYPE == 'sqlite':
            self.connection = db_connect(self.db_file)

        elif DB_TYPE == 'mysql':
            port = get_aw_env_var_or_default('db_port')
            if port is not None:
                port = int(port)

            # pylint: disable=I1101
            self.connection = mysql_connect(
                host=get_aw_env_var_or_default('db_host'),
                port=port,
                user=get_aw_env_var('db_user'),
                password=get_aw_env_var_or_default('db_pwd'),
                database=get_aw_env_var('db'),
            )
            self.cursor = self.connection.cursor()

        elif DB_TYPE == 'psql':
            self.connection = psql_connect(
                host=get_aw_env_var_or_default('db_host'),
                port=get_aw_env_var_or_default('db_port'),
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
