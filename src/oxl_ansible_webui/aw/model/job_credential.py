from time import time
from pathlib import Path

from django.db import models

from aw.model.base import BaseModel, DEFAULT_NONE
from aw.utils.util import is_null, is_set, write_file_0600, overwrite_and_delete_file, get_random_str
from aw.utils.crypto import decrypt, encrypt
from aw.base import USERS
from aw.config.main import config


class BaseJobCredentials(BaseModel):
    SECRET_ATTRS = ['become_pass', 'vault_pass', 'connect_pass', 'ssh_key']
    PUBLIC_ATTRS_ARGS = {
        'connect_user': '--user',
        'become_user': '--become-user',
        'vault_file': '--vault-password-file',
        'vault_id': '--vault-id',
    }
    EMPTY_ATTRS = [
        'connect_user', 'vault_file', 'vault_id', 'vault_pass', 'become_pass', 'connect_pass', 'ssh_key',
    ]

    name = models.CharField(max_length=100, null=False, blank=False)
    connect_user = models.CharField(max_length=100, **DEFAULT_NONE)
    become_user = models.CharField(max_length=100, default='root', null=True, blank=True)
    # default become_user according to ansible-playbook docs
    vault_file = models.TextField(max_length=300, **DEFAULT_NONE)
    vault_id = models.CharField(max_length=50, **DEFAULT_NONE)

    _enc_vault_pass = models.TextField(max_length=500, **DEFAULT_NONE)
    _enc_become_pass = models.TextField(max_length=500, **DEFAULT_NONE)
    _enc_connect_pass = models.TextField(max_length=500, **DEFAULT_NONE)
    _enc_ssh_key = models.TextField(max_length=5000, **DEFAULT_NONE)

    @property
    def vault_pass(self) -> str:
        if is_null(self._enc_vault_pass):
            return ''

        return decrypt(self._enc_vault_pass)

    @vault_pass.setter
    def vault_pass(self, value: str):
        if is_null(value):
            self._enc_vault_pass = None
            return

        self._enc_vault_pass = encrypt(value)

    @property
    def vault_pass_is_set(self) -> bool:
        return is_set(self._enc_vault_pass)

    @property
    def become_pass(self) -> str:
        if is_null(self._enc_become_pass):
            return ''

        return decrypt(self._enc_become_pass)

    @become_pass.setter
    def become_pass(self, value: str):
        if is_null(value):
            self._enc_become_pass = None
            return

        self._enc_become_pass = encrypt(value)

    @property
    def become_pass_is_set(self) -> bool:
        return is_set(self._enc_become_pass)

    @property
    def connect_pass(self) -> str:
        if is_null(self._enc_connect_pass):
            return ''

        return decrypt(self._enc_connect_pass)

    @connect_pass.setter
    def connect_pass(self, value: str):
        if is_null(value):
            self._enc_connect_pass = None
            return

        self._enc_connect_pass = encrypt(value)

    @property
    def connect_pass_is_set(self) -> bool:
        return is_set(self._enc_connect_pass)

    @property
    def ssh_key(self) -> str:
        if is_null(self._enc_ssh_key):
            return ''

        return decrypt(self._enc_ssh_key)

    @ssh_key.setter
    def ssh_key(self, value: str):
        if is_null(value):
            self._enc_ssh_key = None
            return

        self._enc_ssh_key = encrypt(value)

    @property
    def ssh_key_is_set(self) -> bool:
        return is_set(self._enc_ssh_key)

    def _get_set_creds_str(self) -> str:
        creds_set = [attr for attr in self.SECRET_ATTRS if is_set(getattr(self, attr))]
        creds_set_str = ''
        if len(creds_set) > 0:
            creds_set_str = f" ({', '.join(creds_set)})"

        return creds_set_str

    class Meta:
        abstract = True


class JobSharedCredentials(BaseJobCredentials):
    api_fields_read = [
        'id', 'name', 'become_user', 'connect_user', 'vault_file', 'vault_id',
    ]
    api_fields_write = api_fields_read.copy()
    api_fields_write.extend(BaseJobCredentials.SECRET_ATTRS)
    for secret_attr in BaseJobCredentials.SECRET_ATTRS:
        api_fields_read.append(f'{secret_attr}_is_set')
    form_fields = api_fields_write

    def __str__(self) -> str:
        return f"Shared credentials '{self.name}'{self._get_set_creds_str()}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='jobcreds_name_unique')
        ]


class JobUserCredentials(BaseJobCredentials):
    api_fields_read = JobSharedCredentials.api_fields_read.copy()
    api_fields_read.extend(['user', 'category'])
    api_fields_write = JobSharedCredentials.api_fields_write.copy()
    api_fields_write.extend(['category'])
    form_fields = JobSharedCredentials.api_fields_write.copy()
    form_fields.append('category')

    user = models.ForeignKey(USERS, on_delete=models.CASCADE, related_name='credsuser_fk_user')
    category = models.CharField(max_length=100, **DEFAULT_NONE)

    def __str__(self) -> str:
        return f"Credentials '{self.name}' of user '{self.user.username}'{self._get_set_creds_str()}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='jobcredsuser_name_unique')
        ]


class JobUserTMPCredentials(BaseJobCredentials):
    api_fields_read = JobSharedCredentials.api_fields_read.copy()
    api_fields_read.append('user')
    api_fields_write = JobSharedCredentials.api_fields_write.copy()
    form_fields = JobSharedCredentials.api_fields_write.copy()

    user = models.ForeignKey(USERS, on_delete=models.CASCADE, related_name='credstmp_fk_user')
    file_id = models.PositiveIntegerField(**DEFAULT_NONE)

    def __str__(self) -> str:
        return f"Temporary Credentials '{self.name}' of user '{self.user.username}'{self._get_set_creds_str()}"

    def _get_secret_file(self) -> Path:
        if self.file_id is None:
            self.file_id = int(time())

        return Path(config['path_run']) / f'.exec_tmpkey_{self.file_id}'

    def _generate_secret(self):
        write_file_0600(file=self._get_secret_file(), content=get_random_str())

    def cleanup_secret(self):
        overwrite_and_delete_file(self._get_secret_file())

    def get_secret(self) -> str:
        sf = self._get_secret_file()
        if not sf.is_file():
            self._generate_secret()

        with open(sf, 'r', encoding='utf-8') as f:
            return f.read()

    # double-encrypt with tmp-secret for an additional layer of protection
    @property
    def vault_pass(self) -> str:
        if is_null(self._enc_vault_pass):
            return ''

        d1 = decrypt(self._enc_vault_pass)
        return decrypt(ciphertext=d1, secret=self.get_secret())

    @vault_pass.setter
    def vault_pass(self, value: str):
        if is_null(value):
            self._enc_vault_pass = None
            return

        e1 = encrypt(plaintext=value, secret=self.get_secret())
        self._enc_vault_pass = encrypt(e1)

    @property
    def become_pass(self) -> str:
        if is_null(self._enc_become_pass):
            return ''

        d1 = decrypt(self._enc_become_pass)
        return decrypt(ciphertext=d1, secret=self.get_secret())

    @become_pass.setter
    def become_pass(self, value: str):
        if is_null(value):
            self._enc_become_pass = None
            return

        e1 = encrypt(plaintext=value, secret=self.get_secret())
        self._enc_become_pass = encrypt(e1)

    @property
    def connect_pass(self) -> str:
        if is_null(self._enc_connect_pass):
            return ''

        d1 = decrypt(self._enc_connect_pass)
        return decrypt(ciphertext=d1, secret=self.get_secret())

    @connect_pass.setter
    def connect_pass(self, value: str):
        if is_null(value):
            self._enc_connect_pass = None
            return

        e1 = encrypt(plaintext=value, secret=self.get_secret())
        self._enc_connect_pass = encrypt(e1)

    @property
    def ssh_key(self) -> str:
        if is_null(self._enc_ssh_key):
            return ''

        d1 = decrypt(self._enc_ssh_key)
        return decrypt(ciphertext=d1, secret=self.get_secret())

    @ssh_key.setter
    def ssh_key(self, value: str):
        if is_null(value):
            self._enc_ssh_key = None
            return

        e1 = encrypt(plaintext=value, secret=self.get_secret())
        self._enc_ssh_key = encrypt(e1)
