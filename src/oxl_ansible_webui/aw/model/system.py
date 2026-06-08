from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from aw.base import USERS
from aw.model.base import BaseModel, CHOICES_BOOL, DEFAULT_NONE
from aw.config.defaults import CONFIG_DEFAULTS
from aw.config.environment import check_aw_env_var_is_set, AW_ENV_VARS, AW_ENV_VARS_SECRET
from aw.config.main import VERSION
from aw.utils.util import is_null, is_set
from aw.utils.crypto import decrypt, encrypt
from aw.utils.db_handler import close_old_mysql_connections
from aw.config.language import LANGUAGE_CHOICES

MAIL_TRANSPORT_TYPE_PLAIN = 0
MAIL_TRANSPORT_TYPE_SSL = 1
MAIL_TRANSPORT_TYPE_STARTTLS = 2

MAIL_TRANSPORT_TYPE_CHOICES = [
    (MAIL_TRANSPORT_TYPE_PLAIN, 'Unencrypted'),
    (MAIL_TRANSPORT_TYPE_SSL, 'SSL'),
    (MAIL_TRANSPORT_TYPE_STARTTLS, 'StartTLS'),
]

ANSIBLE_EXECUTOR_OFFICIAL = 0  # github.com/ansible/ansible-runner
ANSIBLE_EXECUTOR_OXL = 1  # github.com/O-X-L/ansible-executor
ANSIBLE_EXECUTOR_CHOICES = [
    (ANSIBLE_EXECUTOR_OFFICIAL, 'ansible-runner (official)'),
    (ANSIBLE_EXECUTOR_OXL, 'oxl-ansible-executor (community)'),
]
ANSIBLE_EXECUTOR_ENGINE_LOCAL = 0
ANSIBLE_EXECUTOR_ENGINE_DOCKER = 1
ANSIBLE_EXECUTOR_ENGINE_PODMAN = 2
ANSIBLE_EXECUTOR_ENGINE_CONTAINERS = {
    ANSIBLE_EXECUTOR_ENGINE_DOCKER: 'docker',
    ANSIBLE_EXECUTOR_ENGINE_PODMAN: 'podman',
}
ANSIBLE_EXECUTOR_ENGINE_CHOICES = [
    (ANSIBLE_EXECUTOR_ENGINE_LOCAL, 'Local'),
    (ANSIBLE_EXECUTOR_ENGINE_DOCKER, 'Docker container'),
    (ANSIBLE_EXECUTOR_ENGINE_PODMAN, 'Podman container'),
]

# NOTE: add default-values to config.defaults.CONFIG_DEFAULTS
class SystemConfig(BaseModel):
    SECRET_ATTRS = ['mail_pass']
    EMPTY_ATTRS = [
        'path_ansible_config', 'path_ssh_known_hosts', 'logo_url', 'ara_server', 'global_environment_vars',
        'mail_server', 'mail_sender', 'mail_user', 'mail_pass',
    ]
    api_fields_read = [
        'path_run', 'path_play', 'path_log', 'path_template', 'timezone', 'run_timeout', 'session_timeout',
        'path_ansible_config', 'path_ssh_known_hosts', 'debug', 'logo_url', 'ara_server', 'global_environment_vars',
        'mail_server', 'mail_transport', 'mail_ssl_verify', 'mail_sender', 'mail_user', 'audit_log',
        'ansible_executor', 'ansible_executor_engine', 'ansible_executor_container_image',
        'session_expire_at_browser_close',
    ]

    # NOTE: 'AW_DB' is needed to get this config from DB and 'AW_SECRET' cannot be saved because of security breach
    api_fields_write = api_fields_read.copy()
    api_fields_write.extend(SECRET_ATTRS)
    form_fields = api_fields_read.copy()
    api_fields_read_only = ['db', 'db_migrate', 'serve_static', 'deployment', 'version']

    path_run = models.TextField(max_length=500, default='/tmp/ansible-webui')
    path_play = models.TextField(max_length=500, default=None)
    path_log = models.TextField(max_length=500, default=None)
    path_template = models.TextField(max_length=500, **DEFAULT_NONE)
    timezone = models.TextField(max_length=300, default='UTC')  # UTC to keep model migrations static
    run_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['run_timeout'])
    session_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['session_timeout'])
    session_expire_at_browser_close = models.BooleanField(default=CONFIG_DEFAULTS['session_expire_at_browser_close'])
    path_ansible_config = models.TextField(max_length=500, **DEFAULT_NONE)
    path_ssh_known_hosts = models.TextField(max_length=500, **DEFAULT_NONE)
    debug = models.BooleanField(default=False, choices=CHOICES_BOOL)
    audit_log = models.BooleanField(default=True, choices=CHOICES_BOOL)
    logo_url = models.TextField(max_length=500, **DEFAULT_NONE)
    ara_server = models.TextField(max_length=300, **DEFAULT_NONE)
    global_environment_vars = models.TextField(max_length=1000, **DEFAULT_NONE)
    mail_server = models.TextField(max_length=300, default='127.0.0.1:25', blank=True, null=True)
    mail_transport = models.PositiveSmallIntegerField(
        choices=MAIL_TRANSPORT_TYPE_CHOICES, default=MAIL_TRANSPORT_TYPE_PLAIN,
    )
    mail_ssl_verify = models.BooleanField(default=True, choices=CHOICES_BOOL)
    mail_sender = models.TextField(max_length=300, **DEFAULT_NONE)
    mail_user = models.TextField(max_length=300, **DEFAULT_NONE)
    _enc_mail_pass = models.TextField(max_length=500, **DEFAULT_NONE)
    ansible_executor = models.PositiveSmallIntegerField(
        default=ANSIBLE_EXECUTOR_OFFICIAL,
        choices=ANSIBLE_EXECUTOR_CHOICES,
    )
    ansible_executor_engine = models.PositiveSmallIntegerField(
        default=ANSIBLE_EXECUTOR_ENGINE_LOCAL,
        choices=ANSIBLE_EXECUTOR_ENGINE_CHOICES,
    )
    ansible_executor_container_image = models.CharField(max_length=255, **DEFAULT_NONE)

    @classmethod
    def get_set_public_env_vars(cls) -> list:
        # grey-out settings in web-ui
        e = []

        for k in AW_ENV_VARS:
            if k in AW_ENV_VARS_SECRET:
                continue

            if not check_aw_env_var_is_set(k):
                continue

            e.append(k)

        return e

    @property
    def mail_pass(self) -> str:
        if is_null(self._enc_mail_pass):
            return ''

        return decrypt(self._enc_mail_pass)

    @mail_pass.setter
    def mail_pass(self, value: str):
        if is_null(value):
            self._enc_mail_pass = None
            return

        self._enc_mail_pass = encrypt(value)

    @property
    def mail_pass_is_set(self) -> bool:
        return is_set(self._enc_mail_pass)

    def __str__(self) -> str:
        return 'Ansible-WebUI System Config'


def get_config_from_db() -> SystemConfig:
    try:
        close_old_mysql_connections()
        config_db = SystemConfig.objects.all().first()
        if config_db is None:
            raise ObjectDoesNotExist()

    except ObjectDoesNotExist:
        # create config-object and set dynamic defaults
        config_db = SystemConfig(
            path_play=CONFIG_DEFAULTS['path_play'],
            path_log=CONFIG_DEFAULTS['path_log'],
            timezone=CONFIG_DEFAULTS['timezone'],
        )
        config_db.save()

    return config_db


class SchemaMetadata(BaseModel):
    schema_version = models.CharField(max_length=50)
    schema_version_prev = models.CharField(max_length=50, **DEFAULT_NONE)


def get_schema_metadata() -> SchemaMetadata:
    try:
        close_old_mysql_connections()
        metadata = SchemaMetadata.objects.all().first()
        if metadata is None:
            raise ObjectDoesNotExist()

    except ObjectDoesNotExist:
        metadata = SchemaMetadata(
            schema_version=VERSION,
        )
        metadata.save()

    return metadata


class UserExtended(models.Model):
    user = models.OneToOneField(USERS, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, **DEFAULT_NONE)
    description = models.TextField(max_length=1000, **DEFAULT_NONE)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='en', max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='user_extended_unique')
        ]


class SSHHostkeyFile(models.Model):
    api_fields_read = ['name']

    name = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='sshhostkeyfile_name_unique')
        ]


class SSHHostkeys(models.Model):
    api_fields_read = ['host', 'hostkeys', 'file', 'comment']

    host = models.CharField(max_length=300, null=False, blank=False)
    _hostkeys = models.TextField(max_length=5000, **DEFAULT_NONE)
    comment = models.CharField(max_length=150, **DEFAULT_NONE)

    _file = models.ForeignKey(SSHHostkeyFile, on_delete=models.CASCADE, related_name='sshhostkey_fk_file')

    @property
    def hostkeys(self) -> list[str]:
        if is_null(self._hostkeys):
            return []

        return self._hostkeys.split(',')

    @hostkeys.setter
    def hostkeys(self, value: list[str]):
        self._hostkeys = ','.join(value)

    @property
    def file(self) -> str:
        return self._file.name

    @file.setter
    def file(self, value: SSHHostkeyFile):
        self._file = value

    def __str__(self) -> str:
        return f"SSH-hostkeys for host '{self.host}' (count {len(self.hostkeys)})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['host'], name='sshhostkey_host_unique')
        ]
