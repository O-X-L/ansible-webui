from pathlib import Path

from aw.config.main import config
from aw.utils.util import is_set
from aw.model.job import Job
from aw.model.repository import Repository
from aw.model.system import SSHHostkeys
from aw.utils.db_handler import close_old_mysql_connections


def _get_and_create_custom_known_hosts_file(job_repo: (Job, Repository), path_run: Path) -> (None, str, Path):
    if not is_set(job_repo.ssh_hostkey_file):
        return None

    custom_file = path_run / f'ssh_known_hosts_{job_repo.ssh_hostkey_file.name}'
    close_old_mysql_connections()
    hostkeys = SSHHostkeys.objects.filter(_file=job_repo.ssh_hostkey_file)
    with open(custom_file, 'w', encoding='utf-8') as f:
        for entry in hostkeys:
            f.write(f'# {entry.host} {entry.comment}' + '\n')
            for pubkey in entry.hostkeys:
                f.write(pubkey + '\n')

    return custom_file


def get_ssh_known_hosts_file(job_repo: (Job, Repository), path_run: Path) -> (None, str, Path):
    custom_file = _get_and_create_custom_known_hosts_file(job_repo=job_repo, path_run=path_run)
    if custom_file is not None:
        return custom_file

    global_file = config['path_ssh_known_hosts']
    if is_set(global_file) and Path(global_file).is_file():
        return global_file

    return None
