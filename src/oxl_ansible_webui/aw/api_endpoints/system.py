from ipaddress import ip_network, AddressValueError, NetmaskValueError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from oxl_utils.valid.dns import valid_domain

from aw.config.main import config
from aw.model.system import SystemConfig, get_config_from_db, SSHHostkeys
from aw.api_endpoints.base import API_PERMISSION, get_api_user, GenericResponse, BaseResponse, GenericErrorResponse, \
    HDR_CACHE_1W, response_data_if_changed
from aw.utils.util_no_config import is_set, is_null
from aw.utils.debug import log
from aw.utils.permission import has_manager_privileges
from aw.utils.system import get_system_environment
from aw.config.environment import check_aw_env_var_is_set
from aw.config.hardcoded import SECRET_HIDDEN
from aw.utils.audit import log_audit
from aw.execute.known_hosts import create_or_update_ssh_hostkeys


class SystemConfigSettings(BaseResponse):
    # SystemConfig.api_fields_read
    path_run = serializers.CharField()
    path_play = serializers.CharField()
    path_log = serializers.CharField()
    timezone = serializers.CharField()
    run_timeout = serializers.IntegerField()
    session_timeout = serializers.IntegerField()
    path_ansible_config = serializers.CharField()
    path_ssh_known_hosts = serializers.CharField()
    logo_url = serializers.CharField()
    ara_server = serializers.CharField()
    global_environment_vars = serializers.CharField()
    mail_server = serializers.CharField()
    mail_transport = serializers.IntegerField()
    mail_user = serializers.CharField()
    mail_sender = serializers.CharField()
    mail_ssl_verify = serializers.BooleanField()
    audit_log = serializers.BooleanField()

    # SystemConfig.api_fields_read_only
    db = serializers.CharField()
    db_migrate = serializers.BooleanField()
    serve_static = serializers.BooleanField()
    deployment = serializers.CharField()
    version = serializers.CharField()
    mail_pass_is_set = serializers.BooleanField()


class SystemConfigReadResponse(BaseResponse):
    settings = SystemConfigSettings()
    env_vars = serializers.DictField()
    read_only = serializers.ListSerializer(child=serializers.CharField())


class SystemConfigWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = SystemConfig.api_fields_write

    mail_pass = serializers.CharField(max_length=100, required=False, default=None, allow_blank=True, allow_null=True)


class APISystemConfig(APIView):
    http_method_names = ['put', 'get']
    serializer_class = SystemConfigReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: SystemConfigReadResponse},
        summary='Return currently active config.',
        operation_id='system_config_view',
    )
    def get(request):
        data = {
            'read_only': SystemConfig.api_fields_read_only,
            'env_vars': {k: config[k] for k in SystemConfig.get_set_public_env_vars()},
            'settings': {},
        }

        for field in SystemConfig.api_fields_read + data['read_only']:
            data['settings'][field] = config[field]

        data['settings']['mail_pass_is_set'] = get_config_from_db().mail_pass_is_set
        data['read_only'] += data['env_vars'].keys()
        data['read_only'] = list(set(data['read_only']))

        return response_data_if_changed(request, data=data)

    @extend_schema(
        request=SystemConfigWriteRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='System config updated'),
            400: OpenApiResponse(response=GenericErrorResponse, description='Invalid system config provided'),
            403: OpenApiResponse(
                response=GenericErrorResponse,
                description='Not privileged to update the system config',
            ),
        },
        summary='Modify system config.',
        operation_id='system_config_edit',
    )
    def put(self, request):
        user = get_api_user(request)
        privileged = has_manager_privileges(user=user, kind='system')
        if not privileged:
            return Response(
                data={'error': 'Not privileged to manage system config'},
                status=403,
            )

        serializer = SystemConfigWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={'error': f"Provided system config is not valid: '{serializer.errors}'"},
                status=400,
            )

        config_db = get_config_from_db()
        try:
            changed = False
            for setting, value in serializer.validated_data.items():
                if check_aw_env_var_is_set(setting):
                    # read-only
                    continue

                if setting in SystemConfig.SECRET_ATTRS:
                    if (setting not in SystemConfig.EMPTY_ATTRS and is_null(value)) or value == SECRET_HIDDEN:
                        value = getattr(config_db, setting)

                if (setting in SystemConfig.EMPTY_ATTRS or is_set(value)) and str(config[setting]) != str(value):
                    setattr(config_db, setting, value)
                    changed = True

            if changed:
                log(msg='System config changed - updating', level=5)
                log_audit(user=user, title='System-Settings edit', msg='System-Settings edited')
                config_db.save()

            return Response(data={'msg': "System config updated"}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided system config is not valid: '{err}'"}, status=400)


class SystemEnvironmentReadResponse(BaseResponse):
    aw = serializers.CharField()
    aw_db_schema = serializers.CharField()
    linux = serializers.CharField()
    git = serializers.CharField()
    ansible_core = serializers.CharField()
    ansible_runner = serializers.CharField()
    django = serializers.CharField()
    django_api = serializers.CharField()
    gunicorn = serializers.CharField()
    jinja = serializers.CharField()
    libyaml = serializers.CharField()
    python = serializers.CharField()
    user = serializers.CharField()
    aws_session_manager_plugin = serializers.CharField()
    aws_cli = serializers.CharField()
    ansible_ara = serializers.CharField()
    ansible_playbook = serializers.CharField()
    python_modules = serializers.ListSerializer(child=serializers.DictField())
    ansible_config = serializers.ListSerializer(child=serializers.DictField())
    ansible_collections = serializers.ListSerializer(child=serializers.DictField())


class APISystemEnvironment(APIView):
    http_method_names = ['get']
    serializer_class = SystemEnvironmentReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: SystemEnvironmentReadResponse},
        summary='Return system environment.',
        operation_id='system_env_view',
    )
    def get(request):
        del request
        return Response(get_system_environment(), headers=HDR_CACHE_1W)


class UserPasswordChangeRequest(BaseResponse):
    password = serializers.CharField()


class APIUserPasswordChange(APIView):
    http_method_names = ['put']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=UserPasswordChangeRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Password updated'),
            400: OpenApiResponse(response=GenericErrorResponse, description='Invalid password provided'),
        },
        summary='Update the current users password.',
        operation_id='system_user_pwd_change',
    )
    def put(self, request):
        user = get_api_user(request)
        if user.username == 'demo':
            return Response({'error': 'The demo-user is not allowed to change password'}, status=403)

        pwd = request.data['password']

        if len(pwd) < 10:
            return Response({'error': 'Password does not meet requirements'}, status=400)

        user.set_password(pwd)
        user.save()
        log_audit(user=user, title='Password change', msg='Password changed')
        return Response({'msg': 'Password updated'}, status=200)


class APISSHHostkeyScanRequest(BaseResponse):
    target = serializers.CharField()  # Target to scan - an IP, Domain or Network in CIDR-format
    port = serializers.IntegerField(default=22)  # SSH port to scan
    file = serializers.CharField(default='default')  # Known-Hosts file to add the hostkeys to


class APISSHHostkeyQueryRequest(serializers.ModelSerializer):
    class Meta:
        model = SSHHostkeys
        fields = SSHHostkeys.api_fields_read


class APISSHHostkey(APIView):
    http_method_names = ['get', 'post']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: APISSHHostkeyQueryRequest,
            404: OpenApiResponse(response=GenericErrorResponse, description='No SSH-hostkeys found'),
        },
        summary='Return SSH-hostkeys saved inside the database.',
        operation_id='system_ssh_hostkey_view',
    )
    def get(request):
        del request
        try:
            data = {}
            for entry in SSHHostkeys.objects.all():
                data[entry.host] = entry.hostkeys

            return Response(data=data, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': 'No SSH-hostkeys found'}, status=404)

    @extend_schema(
        request=APISSHHostkeyScanRequest,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='SSH-Hostkey scan initiated'),
            400: OpenApiResponse(response=GenericErrorResponse, description='Invalid target or port provided'),
        },
        summary='Scan target(s) for SSH-hostkeys and add them to the database.',
        operation_id='system_ssh_hostkey_scan',
    )
    def post(self, request):
        user = get_api_user(request)
        target = request.data.get('target', None)
        port = request.data.get('port', 22)
        file = request.data.get('file', 'default')

        if valid_domain(target):
            valid = True

        else:
            try:
                target = ip_network(target, strict=False)
                valid = True

            except (ValueError, AddressValueError, NetmaskValueError):
                valid = False

        if not valid:
            return Response({'error': 'Target is neither a valid IP, Domain nor Network'}, status=400)

        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise TypeError()

        except TypeError:
            return Response({'error': 'Port is not valid'}, status=400)

        create_or_update_ssh_hostkeys(target=target, port=port, file=file)

        log_audit(
            user=user,
            title='System-SSH-Hostkey scan',
            msg=f"Target(s) '{target} -p {port}' scanned for SSH-hostkeys (file {file})",
        )
        return Response({'msg': 'SSH-Hostkey scan initiated'}, status=200)
