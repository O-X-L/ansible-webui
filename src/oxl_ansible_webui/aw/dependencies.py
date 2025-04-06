from aw.utils.debug import log_error

# pylint: disable=C0415


def saml_installed() -> bool:
    try:
        from django_saml2_auth.user import create_jwt_token
        del create_jwt_token
        return True

    except (ImportError, ModuleNotFoundError):
        return False


def mysql_installed() -> bool:
    try:
        from MySQLdb import connect
        del connect
        return True

    except (ImportError, ModuleNotFoundError):
        return False


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
