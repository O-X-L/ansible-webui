from threading import Thread
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from aw.model.repository import Repository
from aw.api_endpoints.base import API_PERMISSION, GenericResponse, get_api_user, LogDownloadResponse, api_docs_put, \
    api_docs_delete, api_docs_post, validate_no_xss, GenericErrorResponse, response_data_if_changed, API_PARAM_HASH
from aw.utils.permission import has_manager_privileges, has_repository_permission, get_viewable_repositories
from aw.model.job import Job
from aw.utils.util import unset_or_null, is_set, is_null
from aw.model.permission import CHOICE_PERMISSION_READ, CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE, \
    CHOICE_PERMISSION_EXECUTE
from aw.api_endpoints.job_util import get_log_file_content
from aw.execute.repository import ExecuteRepository


class RepositoryWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = Repository.api_fields_write

    name = serializers.CharField(validators=[])  # uc on update

    def validate(self, attrs: dict):
        for field in Repository.api_fields_write:
            if field in attrs:
                if field in Repository.fields_shell_cmds and attrs[field] is not None:
                    validate_no_xss(value=attrs[field], field=field, shell_cmd=True)

                else:
                    validate_no_xss(value=attrs[field], field=field)

        return attrs


class RepositoryReadResponse(RepositoryWriteRequest):
    class Meta:
        model = Repository
        fields = Repository.api_fields_read

    rtype_name = serializers.CharField()
    status_name = serializers.CharField()
    log_stdout_url = serializers.CharField()
    log_stderr_url = serializers.CharField()


def repository_in_use(repo: Repository) -> bool:
    return Job.objects.filter(repository=repo).exists()


def validate_repository_types(repo: dict) -> (bool, str):
    rtype_name = Repository.rtype_name_from_id(repo['rtype'])
    if rtype_name == 'Git':
        try:
            if is_set(repo['git_override_initialize']) and is_set(repo['git_override_update']):
                return True, ''

        except KeyError:
            pass

        if unset_or_null(repo, 'git_origin'):
            return False, 'Git Origin is required'

        if unset_or_null(repo, 'git_branch'):
            return False, 'Git Branch is required'

    else:
        if unset_or_null(repo, 'static_path'):
            return False, 'Static Path is required'

    return True, ''


def build_repository(repo: Repository) -> dict:
    data = RepositoryReadResponse(instance=repo).data
    data['time_update'] = repo.time_update_str
    if data['log_stderr'] is None or not Path(data['log_stderr']).is_file():
        data['log_stderr'] = None
        data['log_stderr_url'] = None

    return data


def create_update_git_repo(repo: Repository):
    if is_null(repo) or repo.rtype != 2:
        return

    def _create_update(r: Repository):
        ExecuteRepository(r).create_or_update_repository()

    Thread(
        target=_create_update,
        kwargs={'r': repo}
    ).start()


class APIRepository(APIView):
    http_method_names = ['get', 'post']
    serializer_class = RepositoryReadResponse
    permission_classes = API_PERMISSION

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(RepositoryReadResponse, description='Return list of credentials'),
        },
        summary='Return list of repositories',
        operation_id='repository_list',
        parameters=[API_PARAM_HASH],
    )
    def get(self, request):
        user = get_api_user(request)
        repositories = []

        for repo in get_viewable_repositories(user=user):
            repositories.append(build_repository(repo))

        return response_data_if_changed(request, data=repositories)

    @extend_schema(
        request=RepositoryWriteRequest,
        responses=api_docs_post('Repository'),
        summary='Create a new Repository.',
        operation_id='repository_create',
    )
    def post(self, request):
        privileged = has_manager_privileges(user=get_api_user(request), kind='repository')
        if not privileged:
            return Response(data={'error': 'Not privileged to manage repositories'}, status=403)

        serializer = RepositoryWriteRequest(data=request.data)

        if not serializer.is_valid():
            return Response(data={'error': f"Provided repository data is not valid: '{serializer.errors}'"}, status=400)

        rtype_valid, rtype_error = validate_repository_types(serializer.validated_data)
        if not rtype_valid:
            return Response(data={'error': f"Provided repository data is not valid: '{rtype_error}'"}, status=400)

        try:
            repo = serializer.save()
            create_update_git_repo(repo)

            return Response({
                'msg': f"Repository '{serializer.validated_data['name']}' created successfully",
                'id': repo.id,
            })

        except IntegrityError as err:
            return Response(data={'error': f"Provided repository data is not valid: '{err}'"}, status=400)


class APIRepositoryItem(GenericAPIView):
    http_method_names = ['get', 'put', 'post', 'delete']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: RepositoryReadResponse,
            404: OpenApiResponse(response=GenericErrorResponse, description='Repository does not exist'),
        },
        summary='Return information of a repository.',
        operation_id='repository_get'
    )
    def get(request, repo_id: int):
        user = get_api_user(request)

        try:
            repo = Repository.objects.get(id=repo_id)
            if not has_repository_permission(
                user=user,
                repository=repo,
                permission_needed=CHOICE_PERMISSION_READ
            ):
                return Response(
                    data={'error': f"Not privileged to view the repository '{repo.name}'"},
                    status=403,
                )

            return Response(data=build_repository(repo), status=200)

        except ObjectDoesNotExist:
            return Response(data={'error': f"Repository with ID {repo_id} does not exist"}, status=404)

    @extend_schema(
        request=RepositoryWriteRequest,
        responses=api_docs_put('Repository'),
        summary='Modify a repository.',
        operation_id='repository_edit',
    )
    def put(self, request, repo_id: int):
        user = get_api_user(request)

        serializer = RepositoryWriteRequest(data=request.data)
        if not serializer.is_valid():
            return Response(data={'error': f"Provided repository data is not valid: '{serializer.errors}'"}, status=400)

        rtype_valid, rtype_error = validate_repository_types(serializer.validated_data)
        if not rtype_valid:
            return Response(data={'error': f"Provided repository data is not valid: '{rtype_error}'"}, status=400)

        try:
            repo = Repository.objects.get(id=repo_id)

        except ObjectDoesNotExist:
            repo = None

        if repo is None:
            return Response(data={'error': f"Repository with ID {repo_id} does not exist"}, status=404)

        if not has_repository_permission(
            user=user,
            repository=repo,
            permission_needed=CHOICE_PERMISSION_WRITE
        ):
            return Response(
                data={'error': f"Not privileged to modify the repository '{repo.name}'"},
                status=403,
            )

        try:
            Repository.objects.filter(id=repo_id).update(**serializer.validated_data)
            return Response(data={'msg': f"Repository '{repo.name}' updated", 'id': repo_id}, status=200)

        except IntegrityError as err:
            return Response(data={'error': f"Provided repository data is not valid: '{err}'"}, status=400)

    @extend_schema(
        request=None,
        responses=api_docs_delete('Repository'),
        summary='Delete a repository.',
        operation_id='repository_delete'
    )
    def delete(self, request, repo_id: int):
        user = get_api_user(request)

        try:
            repo = Repository.objects.get(id=repo_id)
            if repo is not None:
                if not has_repository_permission(
                    user=user,
                    repository=repo,
                    permission_needed=CHOICE_PERMISSION_DELETE
                ):
                    return Response(
                        data={'error': f"Not privileged to delete the repository '{repo.name}'"},
                        status=403,
                    )

                if repository_in_use(repo):
                    return Response(
                        data={'error': f"Repository '{repo.name}' cannot be deleted as it is still in use"},
                        status=400,
                    )

                repo.delete()
                return Response(data={'msg': f"Repository '{repo.name}' deleted", 'id': repo_id}, status=200)

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Repository with ID {repo_id} does not exist"}, status=404)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(response=GenericResponse, description='Repository update initiated'),
            403: OpenApiResponse(response=GenericErrorResponse, description='Not privileged to update the repository'),
            404: OpenApiResponse(response=GenericErrorResponse, description='Repository does not exist'),
        },
        summary='Download/Update a repository.',
        operation_id='repository_update'
    )
    def post(self, request, repo_id: int):
        user = get_api_user(request)

        try:
            repo = Repository.objects.get(id=repo_id)
            if repo is not None:
                if not has_repository_permission(
                    user=user,
                    repository=repo,
                    permission_needed=CHOICE_PERMISSION_EXECUTE,
                ):
                    return Response(
                        data={'error': f"Not privileged to update the repository '{repo.name}'"},
                        status=403,
                    )

                create_update_git_repo(repo)

                return Response(
                    data={'msg': f"Repository '{repo.name}' update initiated", 'id': repo_id},
                    status=200,
                )

        except ObjectDoesNotExist:
            pass

        return Response(data={'error': f"Repository with ID {repo_id} does not exist"}, status=404)


class APIRepositoryLogFile(GenericAPIView):
    http_method_names = ['get']
    serializer_class = LogDownloadResponse
    permission_classes = API_PERMISSION
    valid_logfile_type = ['stdout', 'stderr']

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(GenericResponse, description='Download repository log-file'),
            403: OpenApiResponse(GenericErrorResponse, description='Not privileged to view the repository logs'),
            404: OpenApiResponse(GenericErrorResponse, description='Repository or log-file dos not exist'),
        },
        summary='Download log-file of the last repository update.',
        operation_id='repository_logfile',
        parameters=[
            OpenApiParameter(
                name='type', type=str, default='stdout',
                description=f"Type of log-file to download. One of {valid_logfile_type}",
                required=False,
            ),
        ],
    )
    def get(self, request, repo_id: int):
        user = get_api_user(request)
        try:
            repo = Repository.objects.get(id=repo_id)
            if repo is not None:
                if not has_repository_permission(
                    user=user,
                    repository=repo,
                    permission_needed=CHOICE_PERMISSION_READ,
                ):
                    return Response(
                        data={'error': f"Not privileged to view logs of the repository '{repo.name}'"},
                        status=403,
                    )

                logfile = repo.log_stdout
                if 'type' in request.GET and request.GET['type'] == 'stderr':
                    logfile = repo.log_stderr

                if logfile is None:
                    return Response(data={'error': f"No logs found for repository '{repo.name}'"}, status=404)

                return get_log_file_content(logfile)

        except (ObjectDoesNotExist, FileNotFoundError):
            pass

        return Response(
            data={'error': f"Repository with ID '{repo_id}' or log-file does not exist"},
            status=404,
        )
