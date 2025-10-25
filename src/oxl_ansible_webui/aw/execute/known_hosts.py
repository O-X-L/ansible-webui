from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_address

from django.core.exceptions import ObjectDoesNotExist
from oxl_utils.net import resolve_dns

from aw.utils.debug import log
from aw.utils.subps import process
from aw.model.system import SSHHostkeys
from aw.utils.db_handler import close_old_mysql_connections


def _get_ssh_hostkeys(host: (str, IPv4Network, IPv6Network, IPv4Address, IPv6Address), port: int) -> list[str]:
    result = process(
        cmd=f'ssh-keyscan -p{port} -T 2 -H {host}',
        timeout_sec=5,
    )

    if result['rc'] != 0:
        log(msg=f"Got error scanning for SSH-hostkeys: {result['stderr']}", level=5)
        return []

    data = []
    for line in result['stdout'].split('\n'):
        if line.startswith('|'):
            data.append(line.strip())

    return data


def _get_ssh_hostkeys_by_domain_network(target: (str, IPv4Network, IPv6Network), port: int) -> dict:
    data = {}

    if isinstance(target, str):
        data[target] = _get_ssh_hostkeys(host=target, port=port)

        ips = resolve_dns(v=target, t='A')
        ips.extend(resolve_dns(v=target, t='AAAA'))
        for ip in ips:
            ip = ip_address(ip)
            data[str(ip)] = _get_ssh_hostkeys(host=ip, port=port)

    else:
        for ip in target:
            data[str(ip)] = _get_ssh_hostkeys(host=ip, port=port)

    return data


def create_or_update_ssh_hostkeys(target: (str, IPv4Network, IPv6Network), port: int, file: str):
    entries_to_process = _get_ssh_hostkeys_by_domain_network(target=target, port=port)
    for host, hostkeys in entries_to_process.items():
        if len(hostkeys) == 0:
            continue

        try:
            close_old_mysql_connections()
            entry = SSHHostkeys.objects.filter(host=host).first()

        except ObjectDoesNotExist:
            entry = None

        if entry is None:
            entry = SSHHostkeys(host=host)

        entry.file = file
        entry.hostkeys = hostkeys
        close_old_mysql_connections()
        entry.save()
