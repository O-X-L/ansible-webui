from pathlib import Path
from re import sub as regex_replace

from aw.config.main import config
from aw.utils.util import is_set, is_null
from aw.model.repository import Repository, REPOSITORY_TYPE_STATIC, REPOSITORY_TYPE_GIT

ISOLATE_MAIN = 'isolated'
# we need a persistent repo-clone for the WebUI-interaction (file-browsing and so on)
ISOLATE_BROWSABLE = 'browse'


def get_path_repo(repository: Repository, exec_id: (int, None) = None) -> (Path, None):
    if is_null(repository):
        return None

    if repository.rtype_name == REPOSITORY_TYPE_STATIC:
        return Path(repository.static_path)

    safe_repo_name = str(repository.id) + '_'
    safe_repo_name += regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=repository.name)

    path_repo = Path(config['path_run']) / 'repositories'
    if repository.git_isolate:
        path_repo = path_repo / ISOLATE_MAIN

    path_repo = path_repo / safe_repo_name
    if not path_repo.is_dir():
        path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)

    if repository.git_isolate:
        isolate_subdir = ISOLATE_BROWSABLE
        if exec_id is not None:
            isolate_subdir = str(exec_id)

        path_repo = path_repo / isolate_subdir

    if not path_repo.is_dir():
        path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)

    return path_repo


def get_path_play(repository: (None, Repository) = None, exec_id: (None, int) = None) -> (Path, None):
    if repository is None:
        return Path(config['path_play'])

    path_play = get_path_repo(repository=repository, exec_id=exec_id)
    if path_play is None:
        return None

    if repository.rtype_name == REPOSITORY_TYPE_GIT and is_set(repository.git_playbook_base):
        path_play = path_play / repository.git_playbook_base

    if not path_play.is_dir():
        path_play.mkdir(mode=0o750, parents=True, exist_ok=True)

    return path_play
