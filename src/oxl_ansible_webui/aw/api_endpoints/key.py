from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from aw.utils.util import datetime_w_tz
from aw.config.hardcoded import KEY_TIME_FORMAT
from aw.model.api import AwAPIKey
from aw.api_endpoints.base import API_PERMISSION, get_api_user, BaseResponse, GenericResponse, GenericErrorResponse, \
    response_data_if_changed


class KeyReadResponse(BaseResponse):
    token = serializers.CharField()
    comment = serializers.CharField()
    created_at = serializers.CharField()


class KeyWriteResponse(BaseResponse):
    token = serializers.CharField()
    secret = serializers.CharField()
    comment = serializers.CharField(max_length=50)


class APIKey(APIView):
    http_method_names = ['post', 'get']
    serializer_class = KeyReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: KeyReadResponse},
        summary='Return a list of all existing API keys of the current user.',
    )
    def get(request):
        tokens = []
        for key in AwAPIKey.objects.filter(user=get_api_user(request)):
            tokens.append({
                'token': key.name,
                'comment': key.comment,
            })

        return response_data_if_changed(request, data=tokens)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(KeyWriteResponse, description='Returns generated API token & key'),
            400: OpenApiResponse(KeyWriteResponse, description='Invalid API keypair name provided'),
        },
        summary='Create a new API key.',
    )
    def post(self, request):
        self.serializer_class = KeyWriteResponse

        comment = None
        if request.data is not None and 'comment' in request.data:
            comment = request.data['comment']
            if len(comment) > 100:
                return Response(data={'error': 'Provided API-keypair comment is invalid'}, status=400)

        user = get_api_user(request)
        token = f'{user}-{datetime_w_tz().strftime(KEY_TIME_FORMAT)}'
        _, key = AwAPIKey.objects.create_key(name=token, user=user, comment=comment)

        return Response({'token': token, 'key': key, 'comment': comment})


class APIKeyItem(APIView):
    http_method_names = ['delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='API key deleted'),
            404: OpenApiResponse(response=GenericErrorResponse, description='API key does not exist'),
        },
        summary='Delete one of the existing API keys of the current user.',
    )
    def delete(self, request, token: str):
        try:
            result = AwAPIKey.objects.get(user=get_api_user(request), name=token)

            if result is not None:
                result.delete()
                return Response(data={'msg': 'API key deleted'}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': 'API key not found'}, status=404)
