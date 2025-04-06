from os import system as shell
from functools import cache
from importlib import metadata

from aw.utils.debug import log_error

# pylint: disable=C0415

INSTALLED_MODULES = []
for p in metadata.packages_distributions().values():
    INSTALLED_MODULES.extend(p)


@cache
def saml_installed() -> bool:
    return 'grafana-django-saml2-auth' in INSTALLED_MODULES and shell('which xmlsec1 >/dev/null') == 0


@cache
def mysql_installed() -> bool:
    try:
        from MySQLdb import connect
        del connect
        return True

    except (ImportError, ModuleNotFoundError):
        return False


@cache
def psql_installed() -> bool:
    try:
        from psycopg import connect
        del connect
        return True

    except (ImportError, ModuleNotFoundError):
        return False


def log_dependency_error(m: str, i: str):
    log_error(
        f"Unable to import the required {m} module! "
        f"Maybe you need to install it: 'pip install oxl-ansible-webui[{i}]'"
    )
