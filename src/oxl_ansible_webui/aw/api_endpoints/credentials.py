from shutil import rmtree
from re import compile as regex_compile

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.model.job import Job, JobExecution
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials, JobSharedCredentials, JobUserTMPCredentials
from aw.model.permission import CHOICE_PERMISSION_READ, CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE
from aw.api_endpoints.base import API_PERMISSION, get_api_user, GenericResponse, BaseResponse, api_docs_delete, \
    api_docs_put, api_docs_post, validate_no_xss, GenericErrorResponse, response_data_if_changed, API_PARAM_HASH
from aw.utils.util import is_null, overwrite_and_delete_file, write_file_0600, is_set
from aw.utils.permission import has_credentials_permission, has_manager_privileges
from aw.execute.play_credentials import get_pwd_file
from aw.execute.util import get_path_run, create_dirs
from aw.config.hardcoded import SECRET_HIDDEN
from aw.utils.subps import process
from aw.base import USERS
from aw.utils.audit import log_audit


class JobSharedCredentialsReadResponse(serializers.ModelSerializer):
    class Meta:
        model = JobSharedCredentials
        fields = JobSharedCredentials.api_fields_read

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for secret_attr in BaseJobCredentials.SECRET_ATTRS:
            setattr(self, f'{secret_attr}_is_set', serializers.BooleanField(required=False))


class JobUserCredentialsReadResponse(JobSharedCredentialsReadResponse):
    class Meta:
        model = JobUserCredentials
        fields = JobUserCredentials.api_fields_read


class JobCredentialsList(BaseResponse):
    shared = serializers.ListSerializer(child=JobSharedCredentialsReadResponse())
    user = serializers.ListSerializer(child=JobUserCredentialsReadResponse())


class JobSharedCredentialsWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = JobSharedCredentials
        fields = JobSharedCredentials.api_fields_write

    name = serializers.CharField(validators=[])  # uc on update
    vault_pass = serializers.CharField(
        max_length=100, required=False, default=None, allow_blank=True, allow_null=True,
    )
    become_pass = serializers.CharField(
        max_length=100, required=False, default=None, allow_blank=True, allow_null=True,
    )
    connect_pass = serializers.CharField(
        max_length=100, required=False, default=None, allow_blank=True, allow_null=True,
    )
    ssh_key = serializers.CharField(
        max_length=5000, required=False, default=None, allow_blank=True, allow_null=True,
    )

    def validate(self, attrs: dict):
        for field in JobSharedCredentials.api_fields_write:
            if field in attrs and field not in BaseJobCredentials.SECRET_ATTRS:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


class JobUserCredentialsWriteRequest(JobSharedCredentialsWriteRequest):
    class Meta:
        model = JobUserCredentials
        fields = JobUserCredentials.api_fields_write

    def validate(self, attrs: dict):
        for field in JobUserCredentials.api_fields_write:
            if field in attrs and field not in BaseJobCredentials.SECRET_ATTRS:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


class JobTMPCredentialsWriteRequest(JobSharedCredentialsWriteRequest):
    class Meta:
        model = JobUserTMPCredentials
        fields = JobUserTMPCredentials.api_fields_write

    def validate(self, attrs: dict):
        for field in JobUserCredentials.api_fields_write:
            if field in attrs and field not in BaseJobCredentials.SECRET_ATTRS:
                validate_no_xss(value=attrs[field], field=field)

        return attrs


def credentials_in_use(credentials: BaseJobCredentials) -> bool:
    if isinstance(credentials, JobSharedCredentials):
        in_use_jobs = Job.objects.filter(credentials_default=credentials).exists()
        in_use_execs = JobExecution.objects.filter(credentials_shared=credentials).exists()
        in_use = in_use_jobs or in_use_execs

    else:
        in_use = JobExecution.objects.filter(credentials_user=credentials).exists()

    return in_use


REGEX_SSH_KEY_PREFIX = regex_compile(r'.*?(-----BEGIN [A-Z]* PRIVATE KEY-----)(.*)')
REGEX_SSH_KEY_APPENDIX = regex_compile(r'(.*)(-----END [A-Z]* PRIVATE KEY-----).*?')
REGEX_NL_REPLACE = '§'


def _validate_and_fix_ssh_key(key: str) -> (str, None):
    if is_null(key):
        return ''

    key = key.replace('\n', REGEX_NL_REPLACE)

    prefix = REGEX_SSH_KEY_PREFIX.match(key)
    if prefix is None:
        return None

    try:
        key = prefix[2]
        prefix = prefix[1]

    except IndexError:
        return None

    appendix = REGEX_SSH_KEY_APPENDIX.match(key)
    if appendix is None:
        return None

    key = appendix[1].replace(REGEX_NL_REPLACE, '\n').strip()
    appendix = appendix[2]
    return f'{prefix}\n{key}\n{appendix}\n'


class APIJobCredentials(APIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobCredentialsList, description='Return list of credentials'),
        },
        summary='Return list of all credentials the current user is privileged to view.',
        operation_id='credentials_list',
        parameters=[API_PARAM_HASH]
    )
    def get(self, request):
        user = get_api_user(request)
        credentials_shared = []
        credentials_shared_raw = JobSharedCredentials.objects.all()
        for credentials in credentials_shared_raw:
            if has_credentials_permission(
                user=user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_READ,
            ):
                credentials_shared.append(JobSharedCredentialsReadResponse(instance=credentials).data)

        credentials_user_raw = JobUserCredentials.objects.filter(user=user)
        credentials_user = []
        for credentials in credentials_user_raw:
            credentials_user.append(JobUserCredentialsReadResponse(instance=credentials).data)

        return response_data_if_changed(request, data={'shared': credentials_shared, 'user': credentials_user})


def _validate_create_creds(serializer: serializers.BaseSerializer) -> (None, Response):
    if not serializer.is_valid():
        return Response(
            data={'error': f"Provided shared-credentials data is not valid: '{serializer.errors}'"},
            status=400,
        )

    for field in BaseJobCredentials.SECRET_ATTRS:
        value = serializer.validated_data[field]
        if field in BaseJobCredentials.SECRET_ATTRS:
            if is_null(value) or value == SECRET_HIDDEN:
                serializer.validated_data[field] = None

            elif field == 'ssh_key':
                value = _validate_and_fix_ssh_key(value)
                if value is None:
                    return Response(
                        data={'error': 'Provided shared-credentials ssh-key is not valid'},
                        status=400,
                    )

                serializer.validated_data[field] = value

    return None


def _update_creds(
        credentials: BaseJobCredentials, serializer: serializers.BaseSerializer,
    ) -> (None, Response):
    if not serializer.is_valid():
        return Response(
            data={'error': f"Provided credentials data is not valid: '{serializer.errors}'"},
            status=400,
        )

    try:
        # not working with password properties: 'Job.objects.filter(id=job_id).update(**serializer.data)'
        for field, value in serializer.validated_data.items():
            if field in BaseJobCredentials.SECRET_ATTRS:
                if (field not in BaseJobCredentials.EMPTY_ATTRS and is_null(value)) or value == SECRET_HIDDEN:
                    value = getattr(credentials, field)

                elif field == 'ssh_key':
                    value = _validate_and_fix_ssh_key(value)
                    if value is None:
                        return Response(
                            data={'error': 'Provided ssh-key is not valid'},
                            status=400,
                        )

            elif field == 'user':
                continue

            setattr(credentials, field, value)

    except IntegrityError as err:
        return Response(
            data={'error': f"Provided credentials data is not valid: '{err}'"},
            status=400,
        )

    return None


class APIJobSharedCredentials(APIView):
    http_method_names = ['get', 'post']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobCredentialsList, description='Return list of shared-redentials'),
        },
        summary='Return list of all shared-credentials the current user is privileged to view.',
        operation_id='credentials_shared_list',
        parameters=[API_PARAM_HASH]
    )
    def get(self, request):
        user = get_api_user(request)
        credentials_shared = []
        credentials_shared_raw = JobSharedCredentials.objects.all()
        for credentials in credentials_shared_raw:
            if has_credentials_permission(
                user=user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_READ,
            ):
                credentials_shared.append(JobSharedCredentialsReadResponse(instance=credentials).data)

        return response_data_if_changed(request, data=credentials_shared)

    @extend_schema(
        request=JobSharedCredentialsWriteRequest,
        responses=api_docs_post('Credentials'),
        summary='Create shared-credentials.',
        operation_id='credentials_shared_create',
    )
    def post(self, request):
        user = get_api_user(request)

        if not has_manager_privileges(user=user, kind='credentials'):
            return Response(data={'error': 'Not privileged to create shared-credentials'}, status=403)

        serializer = JobSharedCredentialsWriteRequest(data=request.data)
        validation_error = _validate_create_creds(serializer)
        if validation_error is not None:
            return validation_error

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Credentials-Shared create',
                msg=f"Credentials-Shared created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(data={'msg': 'Shared-credentials created', 'id': o.id}, status=200)

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided shared-credentials data is not valid: '{err}'"},
                status=400,
            )


class APIJobUserCredentials(APIView):
    http_method_names = ['get', 'post']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobCredentialsList, description='Return list of user-credentials'),
        },
        summary='Return list of user-credentials of the current user.',
        operation_id='credentials_user_list',
        parameters=[API_PARAM_HASH]
    )
    def get(self, request):
        user = get_api_user(request)
        credentials_user_raw = JobUserCredentials.objects.filter(user=user)
        credentials_user = []
        for credentials in credentials_user_raw:
            credentials_user.append(JobUserCredentialsReadResponse(instance=credentials).data)

        return response_data_if_changed(request, data=credentials_user)

    @extend_schema(
        request=JobSharedCredentialsWriteRequest,
        responses=api_docs_post('Credentials'),
        summary='Create user-credentials.',
        operation_id='credentials_user_create',
    )
    def post(self, request):
        user = get_api_user(request)

        serializer = JobUserCredentialsWriteRequest(data=request.data)
        validation_error = _validate_create_creds(serializer)
        if validation_error is not None:
            return validation_error

        serializer.validated_data['user'] = user

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Credentials-User create',
                msg=f"Credentials-User created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(data={'msg': 'User-credentials created', 'id': o.id}, status=200)

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided user-credentials data is not valid: '{err}'"},
                status=400,
            )


class APIJobTMPCredentials(APIView):
    http_method_names = ['post']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=JobTMPCredentialsWriteRequest,
        responses=api_docs_post('Credentials'),
        summary='Create temporary-credentials.',
        operation_id='credentials_tmp_create',
    )
    def post(self, request):
        user = get_api_user(request)

        serializer = JobTMPCredentialsWriteRequest(data=request.data)
        validation_error = _validate_create_creds(serializer)
        if validation_error is not None:
            return validation_error

        serializer.validated_data['user'] = user

        try:
            o = serializer.save()
            log_audit(
                user=user,
                title='Credentials-Temporary create',
                msg=f"Credentials-Temporary created: ID '{o.id}', Name '{o.name}'",
            )
            return Response(data={'msg': 'Temporary-credentials created', 'id': o.id}, status=200)

        except IntegrityError as err:
            return Response(
                data={'error': f"Provided temporary-credentials data is not valid: '{err}'"},
                status=400,
            )

def _get_shared_creds(credentials_id: int) -> (JobUserCredentials, None):
    try:
        return JobSharedCredentials.objects.get(id=credentials_id)

    except ObjectDoesNotExist:
        return None


class APIJobSharedCredentialsItem(APIView):
    http_method_names = ['get', 'delete', 'put']
    serializer_class = JobSharedCredentialsReadResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobSharedCredentialsReadResponse, description='Return information about credentials'),
            403: OpenApiResponse(GenericErrorResponse, description='Not privileged to view the credentials'),
            404: OpenApiResponse(GenericErrorResponse, description='Credentials not exist'),
        },
        summary='Return information about a set of credentials.',
        operation_id='credentials_shared_view',
    )
    def get(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_shared_creds(credentials_id)
        if credentials is None:
            return Response(
                data={'error': f"Shared-credentials with ID {credentials_id} do not exist"},
                status=404,
            )

        if not has_credentials_permission(
            user=user,
            credentials=credentials,
            permission_needed=CHOICE_PERMISSION_READ,
        ):
            return Response(
                data={'error': f"Shared-credentials '{credentials.name}' are not viewable"},
                status=403,
            )

        return Response(data=self.serializer_class(instance=credentials).data, status=200)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Credentials'),
        summary='Delete shared-credentials.',
        operation_id='credentials_shared_delete',
    )
    def delete(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_shared_creds(credentials_id)
        if credentials is None:
            return Response(data={
                'error': f"Shared-credentials with ID {credentials_id} do not exist"},
                status=404,
            )

        if not has_credentials_permission(
            user=user,
            credentials=credentials,
            permission_needed=CHOICE_PERMISSION_DELETE,
        ):
            return Response(
                data={'error': f"Not privileged to delete the shared-credentials '{credentials.name}'"},
                status=403,
            )

        if credentials_in_use(credentials):
            return Response(
                data={'error': f"Shared-credentials '{credentials.name}' cannot be deleted as they are still in use"},
                status=400,
            )

        credentials.delete()
        log_audit(
            user=user,
            title='Credentials-Shared delete',
            msg=f"Credentials-Shared deleted: ID '{credentials.id}', Name '{credentials.name}'",
        )
        return Response(
            data={'msg': f"Shared-credentials '{credentials.name}' deleted", 'id': credentials_id},
            status=200,
        )

    @extend_schema(
        request=JobSharedCredentialsWriteRequest,
        responses=api_docs_put('Credentials'),
        summary='Modify shared-credentials.',
        operation_id='credentials_shared_edit',
    )
    def put(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_shared_creds(credentials_id)
        if credentials is None:
            return Response(
                data={'error': f"Shared-credentials with ID {credentials_id} do not exist"},
                status=404,
            )

        if not has_credentials_permission(
            user=user,
            credentials=credentials,
            permission_needed=CHOICE_PERMISSION_WRITE,
        ):
            return Response(
                data={'error': f"Not privileged to modify the shared-credentials '{credentials.name}'"},
                status=403,
            )

        serializer = JobSharedCredentialsWriteRequest(data=request.data)
        update_error = _update_creds(credentials, serializer)
        if update_error is not None:
            return update_error

        credentials.save()
        log_audit(
            user=user,
            title='Credentials-Shared edit',
            msg=f"Credentials-Shared edited: ID '{credentials.id}', Name '{credentials.name}'",
        )
        return Response(data={
            'msg': f"Shared-credentials '{credentials.name}' updated",
            'id': credentials_id
        }, status=200)


def _get_user_creds(credentials_id: int, user: USERS) -> (JobUserCredentials, None):
    try:
        return JobUserCredentials.objects.get(id=credentials_id, user=user)

    except ObjectDoesNotExist:
        return None


class APIJobUserCredentialsItem(APIView):
    http_method_names = ['get', 'delete', 'put']
    serializer_class = JobUserCredentialsReadResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(JobUserCredentialsReadResponse, description='Return information about credentials'),
            403: OpenApiResponse(GenericErrorResponse, description='Not privileged to view the credentials'),
            404: OpenApiResponse(GenericErrorResponse, description='Credentials not exist'),
        },
        summary='Return information about a set of user-credentials.',
        operation_id='credentials_user_view',
    )
    def get(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_user_creds(credentials_id, user)
        if credentials is None:
            return Response(
                data={'error': f"User-credentials with ID {credentials_id} do not exist"},
                status=404,
            )

        return Response(data=self.serializer_class(instance=credentials).data, status=200)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Credentials'),
        summary='Delete user-credentials.',
        operation_id='credentials_user_delete',
    )
    def delete(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_user_creds(credentials_id, user)
        if credentials is None:
            return Response(
                data={'error': f"User-credentials with ID {credentials_id} do not exist or belong to another user"},
                status=404,
            )

        if credentials_in_use(credentials):
            return Response(
                data={'error': f"User-credentials '{credentials.name}' cannot be deleted as they are still in use"},
                status=400,
            )

        credentials.delete()
        log_audit(
            user=user,
            title='Credentials-User delete',
            msg=f"Credentials-User deleted: ID '{credentials.id}', Name '{credentials.name}'",
        )
        return Response(data={
            'msg': f"User-credentials '{credentials.name}' deleted",
            'id': credentials_id
        }, status=200)

    @extend_schema(
        request=JobUserCredentialsWriteRequest,
        responses=api_docs_put('Credentials'),
        summary='Modify user-credentials.',
        operation_id='credentials_user_edit',
    )
    def put(self, request, credentials_id: int):
        user = get_api_user(request)

        credentials = _get_user_creds(credentials_id, user)
        if credentials is None:
            return Response(
                data={'error': f"User-credentials with ID {credentials_id} do not exist or belong to another user"},
                status=404,
            )

        serializer = JobUserCredentialsWriteRequest(data=request.data)
        credentials.user = user
        update_error = _update_creds(credentials, serializer)
        if update_error is not None:
            return update_error

        credentials.save()
        log_audit(
            user=user,
            title='Credentials-User edit',
            msg=f"Credentials-User edited: ID '{credentials.id}', Name '{credentials.name}'",
        )
        return Response(
            data={'msg': f"User-credentials '{credentials.name}' updated", 'id': credentials_id},
            status=200,
        )


class VaultEncryptRequest(BaseResponse):
    plaintext = serializers.CharField(required=True)


class VaultEncryptResponse(GenericResponse):
    ciphertext = serializers.CharField()


class APIVaultEncrypt(APIView):
    http_method_names = ['post']
    serializer_class = VaultEncryptResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=VaultEncryptRequest,
        responses={
            200: OpenApiResponse(JobUserCredentialsReadResponse, description='Successfully encrypted data'),
            404: OpenApiResponse(GenericErrorResponse, description='Credentials not exist or have no vault-secret set'),
            500: OpenApiResponse(GenericErrorResponse, description='Failed to encrypt data'),
        },
        summary='Encrypt a secret using Ansible-Vault.',
        operation_id='credentials_vault_encrypt',
    )
    def post(self, request, credentials_kind: str, credentials_id: int):
        user = get_api_user(request)

        serializer = VaultEncryptRequest(data=request.data)
        if not serializer.is_valid():
            return Response(data={'error': 'Invalid vault-encrypt request'}, status=400)

        if credentials_kind == 'user':
            credentials = _get_user_creds(credentials_id, user)

        else:
            credentials = _get_shared_creds(credentials_id)

        if credentials is None or credentials_kind not in ['shared', 'user']:
            return Response(
                data={'error': f'Credentials with ID {credentials_id} do not exist or are inaccessible'},
                status=404,
            )

        if is_null(credentials.vault_file) and is_null(credentials.vault_pass) and is_null(credentials.vault_id):
            return Response(
                data={'error': f'Credentials with ID {credentials_id} have no vault-secret configured'},
                status=404,
            )

        cmd = ['ansible-vault', 'encrypt_string']

        tmp_vault_file = False
        vault_file = None
        path_run = None
        if is_set(credentials.vault_file) or is_set(credentials.vault_pass):
            vault_file = credentials.vault_file
            if is_null(vault_file):
                tmp_vault_file = True
                path_run = get_path_run()
                try:
                    create_dirs(path=path_run, desc='run')

                except OSError:
                    return Response(
                        data={'error': 'Failed to create temporary vault-password-file'},
                        status=500,
                    )

                vault_file = get_pwd_file(path_run=path_run, attr='vault_pass')
                write_file_0600(
                    file=vault_file,
                    content=getattr(credentials, 'vault_pass'),
                )

            cmd.append(f'--vault-password-file={vault_file}')

        if is_set(credentials.vault_id):
            cmd.append(f'--vault-id={credentials.vault_id}')

        result = process(cmd=cmd, timeout_sec=2, stdin=serializer.validated_data['plaintext'])

        if tmp_vault_file and path_run is not None:
            overwrite_and_delete_file(vault_file)
            rmtree(path_run, ignore_errors=True)

        if result['rc'] != 0:
            return Response(
                data={'error': 'Failed to Ansible-Vault-encrypt data'},
                status=500,
            )

        return Response(
            data={
                'msg': 'Successfully Ansible-Vault-encrypted data',
                'ciphertext': result['stdout'],
            },
            status=200,
        )
