from json import JSONDecodeError
from json import loads as json_loads

from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist

from aw.utils.subps import process
from aw.model.repository import Repository
from aw.utils.repository import get_path_play
from aw.utils.db_handler import close_old_mysql_connections
from aw.api_endpoints.base import API_PERMISSION, BaseResponse, GenericErrorResponse


class InventoryListResponse(BaseResponse):
    hosts = serializers.ListSerializer(child=serializers.CharField())
    groups = serializers.ListSerializer(child=serializers.CharField())
    members = serializers.DictField()
    ansible_hosts = serializers.DictField()


def _build_ansible_inventory(ansible_inventory_result: dict) -> dict:
    ansible_hosts = {}
    for host, hostvars in ansible_inventory_result['_meta']['hostvars'].items():
        if 'ansible_host' in hostvars:
            ansible_hosts[host] = hostvars['ansible_host']

    members = {}
    members_raw = {}

    for group, value in ansible_inventory_result.items():
        if group == '_meta':
            continue

        members[group] = set()
        members_raw[group] = value

    # pylint: disable=C0206
    # children can be nested - we try to resolve them with a max-depth of 10
    for _ in range(10):
        for child_group in members:
            if len(members_raw[child_group].get('children', [])) > 0:
                continue

            hosts = set(members_raw[child_group].get('hosts', []))
            members[child_group].update(hosts)
            hosts.update(members[child_group])

            for parent_group in members_raw:
                if child_group in members_raw[parent_group].get('children', []):
                    members[parent_group].update(hosts)
                    members_raw[parent_group]['children'].remove(child_group)

    hosts = set()
    for group in members:
        hosts.update(members[group])
        members[group] = list(members[group])
        members[group].sort()

    hosts = list(hosts)
    hosts.sort()

    groups = list(members.keys())
    groups.sort()
    for group in groups:
        if len(members[group]) == 0:
            members.pop(group)

    return {
        'hosts': hosts,
        'groups': groups,
        'members': members,
        'ansible_hosts': ansible_hosts,
    }


class APIInventoryList(APIView):
    http_method_names = ['get']
    serializer_class = InventoryListResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={
            200: InventoryListResponse,
            403: OpenApiResponse(response=GenericErrorResponse, description='Traversal not allowed'),
            404: OpenApiResponse(
                response=GenericErrorResponse,
                description='Playbook-directory or Inventory file does not exist',
            ),
            500: OpenApiResponse(response=GenericErrorResponse, description='Failed to list inventory'),
        },
        summary='Return a list of inventory-hosts and -groups that are available.',
        parameters=[
            OpenApiParameter(
                name='inventory', type=str, required=True,
                description='Relative path to the inventory-file to query',
            ),
            OpenApiParameter(
                name='repository', type=int, default=None, required=False,
                description='ID of the repository containing the inventory-file',
            ),
            OpenApiParameter(
                name='limit', type=str, default='all', description='Inventory-limit to apply', required=False,
            ),
        ],
    )
    def get(request):
        repo_id = request.GET.get('repository', None)
        limit = request.GET.get('limit', 'all')
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

        inventory = request.GET.get('inventory', None)
        if inventory is None or inventory.strip() == '':
            inventory = 'dynamic'
            inventory_arg = ''

        else:
            if inventory.find('..') != -1:
                return Response(data={'error': 'Traversal not allowed'}, status=403)

            path_inventory = path_play / inventory
            if not path_inventory.is_file():
                return Response(data={'error': f"Inventory file does not exist: {path_inventory}"}, status=404)

            inventory_arg = f'--inventory {path_inventory}'

        result_raw = process(
            'ansible-inventory --list '
            f"--playbook-dir {path_play} "
            f"--limit {limit} {inventory_arg}",
        )
        # NOTE: older versions might require 'response_format json'
        try:
            if result_raw['rc'] != 0:
                raise ValueError()

            result = json_loads(result_raw['stdout'])

        except (JSONDecodeError, ValueError):
            return Response(data={'error': f"Failed to list inventory: {inventory}"}, status=500)

        return Response(
            data=_build_ansible_inventory(result),
            status=200,
        )
