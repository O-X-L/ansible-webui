from hashlib import md5
from json import dumps as json_dumps

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.html import escape as escape_html
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import BaseHasAPIKey
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter

from aw.model.api import AwAPIKey
from aw.base import USERS, GROUPS
from aw.utils.util import is_set


class HasAwAPIKey(BaseHasAPIKey):
    model = AwAPIKey


API_PERMISSION = [IsAuthenticated | HasAwAPIKey]
HDR_CACHE_1W = {'Cache-Control': 'max-age=604800'}
HDR_HASH = 'X-Hash'


# see: rest_framework_api_key.permissions.BaseHasAPIKey:get_from_header
def get_api_user(request) -> USERS:
    if isinstance(request.user, AnonymousUser):
        api_key = request.META.get(getattr(settings, 'API_KEY_CUSTOM_HEADER'))
        if api_key is None:
            return None

        try:
            return AwAPIKey.objects.get_from_key(api_key).user

        except ObjectDoesNotExist:
            # invalid api key
            return None

    return request.user


class BaseResponse(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class GenericResponse(BaseResponse):
    msg = serializers.CharField()


class GenericItemResponse(GenericResponse):
    id = serializers.IntegerField()


class GenericErrorResponse(BaseResponse):
    error = serializers.CharField()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GROUPS


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USERS


class LogDownloadResponse(BaseResponse):
    binary = serializers.CharField()


def api_docs_put(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericItemResponse, description=f'{item} updated'),
        400: OpenApiResponse(response=GenericErrorResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericErrorResponse, description=f'Not privileged to edit the {item}'),
        404: OpenApiResponse(response=GenericErrorResponse, description=f'{item} does not exist'),
    }


def api_docs_delete(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericItemResponse, description=f'{item} deleted'),
        400: OpenApiResponse(response=GenericErrorResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericErrorResponse, description=f'Not privileged to delete the {item}'),
        404: OpenApiResponse(response=GenericErrorResponse, description=f'{item} does not exist'),
    }


def api_docs_post(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericItemResponse, description=f'{item} created'),
        400: OpenApiResponse(response=GenericErrorResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericErrorResponse, description=f'Not privileged to create {item}'),
    }


def not_implemented(*args, **kwargs):
    del args, kwargs
    return JsonResponse({'error': 'Not yet implemented'}, status=404)


def validate_no_xss(value: str, field: str, shell_cmd: bool = False, single_quote: bool = False):
    if is_set(value) and isinstance(value, str):
        # ignore characters shell-commands may need
        if single_quote or shell_cmd:
            value = value.replace("'", '')

        if shell_cmd:
            value = value.replace('&', '')
            value = value.replace('"', '')

        if value != escape_html(value):
            raise ValidationError(f"Found illegal characters in field '{field}'")


API_PARAM_HASH = OpenApiParameter(
    name='hash', type=str, default='',
    description='Hash to compare client-side & server-side information',
    required=False,
)

def client_server_data_changed(request, data) -> (bool, str):
    if 'hash' in request.GET and str(request.GET['hash']) != '0':
        h = md5(json_dumps(data).encode('utf-8')).hexdigest()[:6]
        return h != request.GET['hash'], h

    return True, '-'


def response_data_if_changed(request, data) -> Response:
    changed, h = client_server_data_changed(request, data=data)
    if not changed:
        return Response(data=None, status=304, headers={HDR_HASH: h})

    return Response(data=data, status=200, headers={HDR_HASH: h})
