from os import listdir
from pathlib import Path
from functools import cache

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist

from aw.model.repository import Repository
from aw.utils.repository import get_path_play
from aw.utils.db_handler import close_old_mysql_connections
from aw.api_endpoints.base import API_PERMISSION, BaseResponse, GenericErrorResponse


class FileSystemReadResponse(BaseResponse):
    files = serializers.ListSerializer(child=serializers.CharField())
    dirs = serializers.ListSerializer(child=serializers.CharField())


class FileSystemExistsResponse(BaseResponse):
    exists = serializers.BooleanField()
    fstype = serializers.CharField()


class APIFsBrowse(APIView):
    http_method_names = ['get']
    serializer_class = FileSystemReadResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @cache
    def _listdir(path: str) -> list[str]:
        return listdir(path)

    @classmethod
    @extend_schema(
        request=None,
        responses={
            200: FileSystemReadResponse,
            400: OpenApiResponse(GenericErrorResponse, description='Invalid browse-selector provided'),
            403: OpenApiResponse(GenericErrorResponse, description='Traversal not allowed'),
            404: OpenApiResponse(GenericErrorResponse, description='Base directory does not exist'),
        },
        summary='Return list of existing files and directories.',
        description="This endpoint is mainly used for form auto-completion when selecting job-files",
        parameters=[
            OpenApiParameter(
                name='base', type=str, default='', description='Relative directory to query',
                required=False,
            ),
        ],
    )
    def get(cls, request, repo_id: int = None):
        # pylint: disable=R0801
        items = {'files': [], 'dirs': []}

        base = str(request.GET.get('base', ''))

        if base.find('..') != -1 or base.startswith('/'):
            return Response(data={'error': 'Traversal not allowed'}, status=403)

        repo = None
        if repo_id is not None:
            try:
                close_old_mysql_connections()
                repo = Repository.objects.get(id=repo_id)
                if repo is None:
                    raise ObjectDoesNotExist()

            except ObjectDoesNotExist:
                return Response(data={'error': 'Provided repository does not exist'}, status=404)

        path_play = get_path_play(repository=repo)
        if path_play is None:
            return Response(data={'error': 'Provided playbook-dir does not exist'}, status=404)

        browse_root = path_play / base

        if not browse_root.is_dir():
            return Response(data={'error': f"Base directory '{browse_root}' does not exist"}, status=404)

        raw_items = cls._listdir(browse_root)

        for item in raw_items:
            try:
                item_path = browse_root / item
                if item_path.is_file():
                    items['files'].append(item)
                elif item_path.is_dir():
                    items['dirs'].append(item)

            except OSError:
                continue

        return Response(items)


class APIFsExists(APIView):
    http_method_names = ['get']
    serializer_class = FileSystemExistsResponse
    permission_classes = API_PERMISSION

    @classmethod
    @extend_schema(
        request=None,
        responses={
            200: FileSystemExistsResponse,
            400: OpenApiResponse(GenericErrorResponse, description='No file or directory not provided'),
            403: OpenApiResponse(GenericErrorResponse, description='Access to file or directory is forbidden'),
        },
        summary='Return if the provided file or directory exists.',
        description="This endpoint is mainly used for form validation when configuring path and files",
        parameters=[
            OpenApiParameter(
                name='item', type=str, default=None, required=True,
                description='File or directory that should be checked',
            ),
        ],
    )
    def get(cls, request):
        if 'item' not in request.GET:
            return Response(data={'error': "Required parameter 'item' was not provided"}, status=400)

        try:
            fs_item = Path(request.GET['item'])
            try:
                return Response({
                    'exists': fs_item.exists(),
                    'fstype': 'file' if fs_item.is_file() else 'directory',
                })

            except OSError:
                return Response({'exists': False, 'fstype': 'unknown'})

        except PermissionError:
            return Response(data={'error': 'Access to file or directory is forbidden'}, status=403)
