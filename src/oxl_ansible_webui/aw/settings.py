from pathlib import Path
from os import environ

from yaml import safe_load as yaml_load
from yaml import YAMLError

try:
    from aw.config.main import config, VERSION

except ImportError:
    # pylint-django
    from aw.config.main import init_config
    init_config()
    from aw.config.main import config, VERSION


from aw.config.hardcoded import LOGIN_PATH, ENV_KEY_CONFIG, ENV_KEY_SAML
from aw.config.defaults import CONFIG_DEFAULTS, inside_docker, behind_proxy
from aw.utils.deployment import deployment_dev, deployment_prod
from aw.config.environment import get_aw_env_var_or_default, auth_mode_saml, get_aw_env_var
from aw.utils.debug import log
from aw.dependencies import saml_installed, mysql_installed, psql_installed, log_dependency_error
from aw.utils.db import AbstractDBConnection, SQLiteOperationalError, MySQLError, PSQLError

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [
    BASE_DIR / 'aw' / 'templates/'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = [
    'aw.apps.AwConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # api
    'rest_framework',
    'rest_framework_api_key',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'aw.apps.AwMiddleware',
]

# Database
DB_FILE = None
DB_TYPE = 'sqlite'
if config['db_type'] in ['mysql', 'psql']:
    DB_TYPE = config['db_type']
    if DB_TYPE == 'mysql' and not mysql_installed():
        log_dependency_error('MySQL', 'mysql')

    elif DB_TYPE == 'psql' and not psql_installed():
        log_dependency_error('PostgreSQL', 'psql')

if DB_TYPE == 'sqlite':
    if deployment_prod():
        DB_FILE = Path(get_aw_env_var_or_default('db'))

        if DB_FILE.name.find('.') == -1 and not DB_FILE.exists():
            try:
                DB_FILE.mkdir(mode=0o750, parents=True, exist_ok=True)

            except (OSError, FileNotFoundError):
                raise ValueError(f"Unable to created database directory: '{DB_FILE}'")

        if DB_FILE.is_dir():
            DB_FILE = DB_FILE / 'aw.db'

    else:
        dev_db_file = 'aw.dev.db' if deployment_dev() else 'aw.staging.db'
        if 'AW_DB' in environ:
            DB_FILE = Path(get_aw_env_var_or_default('db'))
            if DB_FILE.is_dir():
                DB_FILE = DB_FILE / dev_db_file

        else:
            DB_FILE = dev_db_file
            DB_FILE = BASE_DIR / DB_FILE


AW_DB_ENGINES = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_FILE,
        'OPTIONS': {
            'timeout': 3,  # kill long-running write-requests fast; do not block whole application
            'transaction_mode': 'IMMEDIATE',
            # see: https://github.com/django/django/commit/a0204ac183ad6bca71707676d994d5888cf966aa
        },
        'ATOMIC_REQUESTS': False,  # default
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_aw_env_var('db'),
        'USER': get_aw_env_var_or_default('db_user'),
        'PASSWORD': get_aw_env_var_or_default('db_pwd'),
        'HOST': get_aw_env_var_or_default('db_host'),
        'PORT': get_aw_env_var_or_default('db_port'),
        'CONN_HEALTH_CHECKS': True,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {},
    },
    'psql': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_aw_env_var('db'),
        'USER': get_aw_env_var_or_default('db_user'),
        'PASSWORD': get_aw_env_var_or_default('db_pwd'),
        'HOST': get_aw_env_var_or_default('db_host'),
        'PORT': get_aw_env_var_or_default('db_port'),
    },
}

DATABASES = {'default': AW_DB_ENGINES[DB_TYPE]}

if DB_TYPE == 'mysql':
    if get_aw_env_var('db_socket') is not None:
        DATABASES['default']['OPTIONS']['unix_socket'] = get_aw_env_var('db_socket')

    if not get_aw_env_var_or_default('debug'):
        DATABASES['default']['OPTIONS']['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES'"


def debug_mode() -> bool:
    # NOTE: only gets checked on startup
    if deployment_dev():
        return True

    if get_aw_env_var_or_default('debug'):
        return True

    with AbstractDBConnection(DB_FILE) as db:
        try:
            return db.query('SELECT debug FROM aw_systemconfig')[0] == 1

        except (IndexError, TypeError, SQLiteOperationalError, MySQLError, PSQLError):
            return False


DEBUG = debug_mode()

# WEB BASICS
PORT_WEB = get_aw_env_var_or_default('port')
LISTEN_ADDRESS = get_aw_env_var_or_default('address')
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    f'http://localhost:{PORT_WEB}',
    'http://127.0.0.1',
    f'http://127.0.0.1:{PORT_WEB}',
]
if LISTEN_ADDRESS != '127.0.0.1':
    CSRF_TRUSTED_ORIGINS.extend([
        f'http://{LISTEN_ADDRESS}'
        f'http://{LISTEN_ADDRESS}:{PORT_WEB}'
        f'https://{LISTEN_ADDRESS}'
        f'https://{LISTEN_ADDRESS}:{PORT_WEB}'
    ])


def get_main_web_address() -> str:
    if 'AW_HOSTNAMES' not in environ:
        return f'http://localhost:{PORT_WEB}'

    _hostname = environ['AW_HOSTNAMES'].split(',', 1)[0]
    if behind_proxy() or inside_docker():
        # we will not know what port the proxy is serving this service - assume its 443
        return f'https://{_hostname}'

    return f'https://{_hostname}:{PORT_WEB}'


if behind_proxy():
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ['*']
if 'AW_HOSTNAMES' in environ:
    for hostname in environ['AW_HOSTNAMES'].split(','):
        ALLOWED_HOSTS.append(hostname)
        CSRF_TRUSTED_ORIGINS.extend([
            f'http://{hostname}',
            f'https://{hostname}',
            f'http://{hostname}:{PORT_WEB}',
            f'https://{hostname}:{PORT_WEB}',
        ])

CSRF_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
CORS_ORIGINS_WHITELIST = CSRF_TRUSTED_ORIGINS

ROOT_URLCONF = 'aw.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]
WSGI_APPLICATION = 'aw.main.app'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 10,
        },
    },
]

# Security
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = config['session_timeout']
SECRET_KEY = config['secret']
CSRF_COOKIE_AGE = None  # session-based
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = config.timezone_str

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'aw' / 'static']
if deployment_prod():
    STATICFILES_DIRS.append(BASE_DIR / 'aw' / 'static_prod')

else:
    STATICFILES_DIRS.append(BASE_DIR / 'aw' / 'static_dev')

LOGIN_REDIRECT_URL = '/ui'
LOGOUT_REDIRECT_URL = LOGIN_PATH
handler403 = 'aw.utils.handlers.handler403'
handler500 = 'aw.utils.handlers.handler500'

# api
API_KEY_CUSTOM_HEADER = 'HTTP_X_API_KEY'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    # 'TITLE': 'AW API',
    # 'DESCRIPTION': 'Your project description',
    'VERSION': VERSION,
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SWAGGER_UI_FAVICON_HREF': config['logo_url'],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'apiKey': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-Api-Key',
            },
            # 'session': {
            #     'type': 'apiKey',
            #     'in': 'cookie',
            #    'name': 'sessionid',
            # },
        },
    },
    'SECURITY': [
        {'apiKey': []},
        # {'session': []},
    ],
    'SWAGGER_UI_SETTINGS': {
        'displayOperationId': False,
    },
    'POSTPROCESSING_HOOKS': []
}

if deployment_dev():
    SPECTACULAR_SETTINGS['SWAGGER_UI_SETTINGS']['persistAuthorization'] = True


# Authentication
def _build_saml_config() -> dict:
    if not auth_mode_saml():
        return {}

    if not saml_installed():
        log_dependency_error('SAML', 'saml')

    try:
        with open(environ[ENV_KEY_CONFIG], 'r', encoding='utf-8') as _config:
            saml_cnf = yaml_load(_config.read())[environ[ENV_KEY_SAML]]

    except (YAMLError, KeyError) as err:
        log(msg=f"Failed to load SAML config: '{err}'", level=1)
        return {}

    try:
        # basic validation to help users find/fix their issues faster
        _ = saml_cnf['ASSERTION_URL']
        _ = saml_cnf['ENTITY_ID']
        _ = saml_cnf['ATTRIBUTES_MAP']
        _ = saml_cnf['ATTRIBUTES_MAP']['username']
        _ = saml_cnf['ATTRIBUTES_MAP']['email']
        if 'METADATA_AUTO_CONF_URL' not in saml_cnf and 'METADATA_LOCAL_FILE_PATH' not in saml_cnf:
            raise KeyError('METADATA_AUTO_CONF_URL or METADATA_LOCAL_FILE_PATH')

        if ('TOKEN_REQUIRED' not in saml_cnf or saml_cnf['TOKEN_REQUIRED']) and \
                'token' not in saml_cnf['ATTRIBUTES_MAP']:
            raise KeyError('TOKEN_REQUIRED but not configured in ATTRIBUTES_MAP')

        if 'JWT_ALGORITHM' not in saml_cnf:
            # for SSO-login page; internal communications
            saml_cnf['JWT_ALGORITHM'] = CONFIG_DEFAULTS['jwt_algo']
            saml_cnf['JWT_SECRET'] = CONFIG_DEFAULTS['jwt_secret']
            saml_cnf['JWT_EXP'] = 60

    except KeyError as err:
        log(msg=f"Invalid SAML config: '{err}'", level=1)
        return {}

    return saml_cnf


AUTH_MODE = get_aw_env_var_or_default('auth_mode')
SAML2_AUTH = _build_saml_config()
if len(SAML2_AUTH) > 0:
    INSTALLED_APPS.append('django_saml2_auth')
