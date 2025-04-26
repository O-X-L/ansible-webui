from pytz import all_timezones
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from aw.base import USERS
from aw.model.system import SystemConfig
from aw.settings import AUTH_MODE
from aw.utils.util import get_logo
from aw.utils.version import get_version
from aw.config.language import TRANSLATIONS
from aw.config.environment import AW_ENV_VARS
from aw.utils.deployment import deployment_dev
from aw.config.defaults import CONFIG_DEFAULTS
from aw.api_endpoints.base import get_api_user, HDR_CACHE_1W, GenericResponse, API_PERMISSION
from aw.model.job import Job, JobUserCredentials, Repository, JobSharedCredentials
from aw.model.base import get_model_field_default, get_model_field_choices
from aw.views.base import choices_user, choices_group
from aw.model.alert import AlertGlobal, AlertGroup, AlertUser, AlertPlugin
from aw.model.permission import JobPermission
from aw.utils.permission import get_viewable_credentials, get_viewable_jobs, get_viewable_repositories


def _choices_alert_plugins() -> list[tuple]:
    return [(p.id, p.name) for p in AlertPlugin.objects.all()]


FK_CHOICES = {
    AlertGlobal: {
        'plugin': _choices_alert_plugins,
    },
    AlertGroup: {
        'group': choices_group,
        'plugin': _choices_alert_plugins,
    },
    AlertUser: {
        'plugin': _choices_alert_plugins,
    },
    JobPermission: {
        'users': choices_user,
        'groups': choices_group,
    },
}

FK_CHOICES_FILTERED = {
    Job: {
        'repository': get_viewable_repositories,
        'credentials_default': get_viewable_credentials,
    },
    Repository: {
        'git_credentials': get_viewable_credentials,
    },
    AlertGlobal: {
        'jobs': get_viewable_jobs,
    },
    AlertGroup: {
        'jobs': get_viewable_jobs,
    },
    AlertUser: {
        'jobs': get_viewable_jobs,
    },
    JobPermission: {
        'jobs': get_viewable_jobs,
        'credentials': get_viewable_credentials,
        'repositories': get_viewable_repositories,
    },
}


def _django_to_svelte_choices(c: (list[tuple], tuple[tuple])) -> list[dict]:
    cv = []
    for v in c:
        cv.append({'value': v[0], 'name': v[1]})

    return cv


def _obj_to_svelte_choices(c: list[(Job, JobPermission, JobSharedCredentials)]) -> list[dict]:
    cv = []
    for v in c:
        cv.append({'value': v.id, 'name': v.name})

    return cv


def _build_model_defaults_choices(m, user: USERS) -> dict:
    d = {
        'choices': {},
        'defaults': {},
    }

    for f in m.form_fields:
        d['defaults'][f] = get_model_field_default(m, f)
        if m in FK_CHOICES and f in FK_CHOICES[m]:
            d['choices'][f] = _django_to_svelte_choices(FK_CHOICES[m][f]())
            continue

        if m in FK_CHOICES_FILTERED and f in FK_CHOICES_FILTERED[m]:
            d['choices'][f] = _obj_to_svelte_choices(FK_CHOICES_FILTERED[m][f](user))
            continue

        c = get_model_field_choices(m, f)
        if c is None:
            d['choices'][f] = None

        else:
            cv = _django_to_svelte_choices(c)
            if len(cv) == 2 and isinstance(cv[0]['value'], bool):
                # no need for boolean choices
                d['choices'][f] = None

            else:
                d['choices'][f] = cv

    return d


class APIBackendInfo(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = [AllowAny]

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return backend-infos needed for frontend rendering',
        operation_id='backend_infos',
    )
    def get(request):
        states = {
            'authenticated': False, 'sso': False, 'user': None, 'user_id': None,
            'version': get_version(),
            'logo': get_logo(),
        }

        if 'Referer' in request.headers:
            ref = request.headers['Referer']
            if ref.endswith('/'):
                ref = ref[:-1]

            if ref.endswith('/a/login') or ref.endswith('/a/login/fallback'):
                states['sso'] = AUTH_MODE == 'saml'

        user = get_api_user(request)
        if user is not None:
            states['user'] = user.username
            states['user_id'] = user.id
            states['authenticated'] = user.is_authenticated

        return Response(data=states, status=200)


class APIBackendTranslations(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = [AllowAny]

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return text-translations needed for frontend rendering',
        operation_id='backend_translations',
    )
    def get(request):
        del request
        return Response(data=TRANSLATIONS, status=200, headers=HDR_CACHE_1W)


class APIFormInfosJob(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return job-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_job',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(Job, user), status=200)


class APIFormInfosCredentials(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return credential-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_credentials',
    )
    def get(request):
        user = get_api_user(request)
        return Response(
            data=_build_model_defaults_choices(JobUserCredentials, user),
            status=200,
            headers=HDR_CACHE_1W,
        )


class APIFormInfosRepositories(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return repository-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_repositories',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(Repository, user), status=200)


class APIFormInfosConfig(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return system-config form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_config',
    )
    def get(request):
        user = get_api_user(request)
        data = _build_model_defaults_choices(SystemConfig, user)

        data['choices']['timezone'] = sorted(all_timezones)
        data['defaults']['path_run'] = CONFIG_DEFAULTS['path_run']
        data['defaults']['path_play'] = CONFIG_DEFAULTS['path_play']
        data['defaults']['path_log'] = CONFIG_DEFAULTS['path_log']
        data['defaults']['path_ansible_config'] = CONFIG_DEFAULTS['path_ansible_config']
        data['defaults']['path_ssh_known_hosts'] = CONFIG_DEFAULTS['path_ssh_known_hosts']
        data['defaults']['debug'] = CONFIG_DEFAULTS['debug'] or deployment_dev()
        data['env_vars'] = AW_ENV_VARS

        return Response(data=data, status=200, headers=HDR_CACHE_1W)


class APIFormInfosGlobalAlerts(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return global-alert-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_global_alerts',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(AlertGlobal, user), status=200)


class APIFormInfosGroupAlerts(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return group-alert-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_group_alerts',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(AlertGroup, user), status=200)


class APIFormInfosUserAlerts(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return user-alert-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_user_alerts',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(AlertUser, user), status=200)


class APIFormInfosPermissions(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return permission-form-choices & -defaults needed for frontend rendering',
        operation_id='form_choices_permission',
    )
    def get(request):
        user = get_api_user(request)
        return Response(data=_build_model_defaults_choices(JobPermission, user), status=200)
