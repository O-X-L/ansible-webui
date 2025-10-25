from threading import Lock
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_address

from django.core.exceptions import ObjectDoesNotExist
from oxl_utils.net import resolve_dns
from oxl_utils.ps import process_list_in_threads

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
        log(msg=f"SSH-hostkey target is unreachable: {host} -p {port}", level=5)
        return []

    data = []
    for line in result['stdout'].split('\n'):
        if line.startswith('|'):
            data.append(line.strip())

    return data


class HostkeyIPThreader:
    def __init__(self, ips: list, port: int):
        self.ips = [ip_address(ip) for ip in ips]
        self.port = port
        self.data = {}
        self._lock = Lock()

    def _get_hostkeys_by_ip(self, ip: (IPv4Address, IPv6Address)):
        result = _get_ssh_hostkeys(host=ip, port=self.port)
        with self._lock:
            self.data[str(ip)] = result

    def process(self):
        process_list_in_threads(
            to_process=self.ips,
            callback=self._get_hostkeys_by_ip,
            key='ip',
            parallel=50,
        )


def _get_ssh_hostkeys_by_domain_network(target: (str, IPv4Network, IPv6Network), port: int) -> dict:
    data = {}

    if isinstance(target, (IPv4Network, IPv6Network)):
        ips = list(target)

    else:
        data[target] = _get_ssh_hostkeys(host=target, port=port)

        # hostkey-matching is different for IPs and hostnames
        ips = resolve_dns(v=target, t='A')
        ips.extend(resolve_dns(v=target, t='AAAA'))

    if len(ips) > 0:
        threader = HostkeyIPThreader(ips=ips, port=port)
        threader.process()
        data = {**data, **threader.data}

    return data


def create_or_update_ssh_hostkeys(target: (str, IPv4Network, IPv6Network), port: int, file: str, comment: (str, None)):
    entries_to_process = _get_ssh_hostkeys_by_domain_network(target=target, port=port)
    for host, hostkeys in entries_to_process.items():
        if len(hostkeys) == 0:
            continue

        try:
            close_old_mysql_connections()
            entry = SSHHostkeys.objects.get(host=host)

        except ObjectDoesNotExist:
            entry = None

        if entry is None:
            entry = SSHHostkeys(host=host)

        entry.file = file
        entry.comment = comment
        entry.hostkeys = hostkeys
        close_old_mysql_connections()
        entry.save()
