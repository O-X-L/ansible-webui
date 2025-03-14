from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

from aw.settings import AUTH_MODE
from aw.api_endpoints.base import BaseResponse, get_api_user, HDR_NOCACHE
from aw.templatetags.util import get_logo, get_version


class BackendInfoResponse(BaseResponse):
    authenticated = serializers.BooleanField()
    sso = serializers.BooleanField()


class APIBackendInfo(GenericAPIView):
    http_method_names = ['get']
    serializer_class = BackendInfoResponse
    permission_classes = [AllowAny]

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: BackendInfoResponse},
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
