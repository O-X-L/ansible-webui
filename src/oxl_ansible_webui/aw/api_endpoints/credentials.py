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
from aw.utils.permission import has_credentials_permission, has_manager_privileges
from aw.config.hardcoded import SECRET_HIDDEN
from aw.utils.util import is_null
from aw.base import USERS


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


SSH_KEY_PREFIX = '-----BEGIN OPENSSH PRIVATE KEY-----'
SSH_KEY_APPENDIX = '-----END OPENSSH PRIVATE KEY-----'


def _validate_and_fix_ssh_key(key: str) -> (str, None):
    if is_null(key):
        return ''

    if key.find(SSH_KEY_PREFIX) == -1:
        return None

    key = key.replace(SSH_KEY_PREFIX, '').replace(SSH_KEY_APPENDIX, '').strip().replace(' ', '\n')
    return f'{SSH_KEY_PREFIX}\n{key}\n{SSH_KEY_APPENDIX}\n'


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
        credentials, update_error = _update_creds(credentials, serializer)
        if update_error is not None:
            return update_error

        credentials.user = user
        credentials.save()

        return Response(
            data={'msg': f"User-credentials '{credentials.name}' updated", 'id': credentials_id},
            status=200,
        )
