from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from aw.settings import AUTH_MODE
from aw.api_endpoints.base import get_api_user, HDR_NOCACHE, HDR_CACHE_1W, GenericResponse, API_PERMISSION
from aw.templatetags.util import get_logo, get_version
from aw.config.language import TRANSLATIONS
from aw.model.job import Job
from aw.model.base import get_model_field_default, get_model_field_choices


def _build_model_defaults_choices(m) -> dict:
    d = {
        'choices': {},
        'defaults': {},
    }

    for f in m.form_fields:
        d['defaults'][f] = get_model_field_default(m, f)
        c = get_model_field_choices(m, f)
        if c is None:
            d['choices'][f] = None

        else:
            cv = []
            for v in c:
                cv.append({'value': v[0], 'name': v[1]})

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
            'authenticated': False, 'sso': False, 'user': None,
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
            states['authenticated'] = user.is_authenticated

        return Response(data=states, status=200, headers=HDR_NOCACHE)


class APIBackendTranslations(GenericAPIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = [AllowAny]

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return text-translations in needed for frontend rendering',
        operation_id='backend_infos',
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
        summary='Return job-form-choices needed for frontend rendering',
        operation_id='form_choices_job',
    )
    def get(request):
        del request
        return Response(
            data=_build_model_defaults_choices(Job),
            status=200,
            headers=HDR_CACHE_1W,
        )
