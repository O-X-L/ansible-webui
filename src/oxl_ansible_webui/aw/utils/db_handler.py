from django.db import close_old_connections

from aw.config.environment import get_aw_env_var_or_default


# handle error "MySQLdb.OperationalError: (2006, 'Server has gone away')"
def close_old_mysql_connections():
    if get_aw_env_var_or_default('db_type') != 'mysql':
        return

    close_old_connections()
