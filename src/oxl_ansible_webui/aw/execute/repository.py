from os import listdir
from pathlib import Path
from threading import Thread
from re import sub as regex_replace

from django.utils import timezone

from aw.utils.debug import log
from aw.config.main import config
from aw.utils.subps import process
from aw.model.job import  JobExecution
from aw.model.base import JOB_EXEC_STATUS_FAILED
from aw.utils.handlers import AnsibleRepositoryError
from aw.utils.filesystem import write_file_0640, rm_dir
from aw.utils.util import is_null, is_set, datetime_w_tz
from aw.utils.db_handler import close_old_mysql_connections
from aw.execute.ssh_hostkey import get_ssh_known_hosts_file
from aw.utils.repository import get_path_repo, get_path_play
from aw.model.repository import Repository, REPOSITORY_TYPE_STATIC
from aw.execute.play_credentials import write_pwd_file, get_pwd_file
from aw.execute.util import update_status, create_dirs, get_path_run
from aw.config.hardcoded import REPO_CLONE_TIMEOUT, FILE_TIME_FORMAT, SECRET_HIDDEN_PLAIN


ENV_VAR_GIT_SECRET = 'AW_GIT_SECRET'


class ExecuteRepository:
    def __init__(self, repository: Repository, execution: JobExecution = None, path_run: Path = None):
        self.repository = repository
        self.path_run_base = path_run
        if self.path_run_base is None:
            self.path_run_base = get_path_run()

        self.path_run = self.path_run_base / '.repository'

        self.execution = execution
        self.isolate_browsable = self.execution is None
        self._path_repo = self._get_path_repo()
        create_dirs(path=config['path_log'], desc='log')

    def create_repository(self, env: dict):
        if self._path_repo.is_dir() and not (self._path_repo / '.git').is_dir() and len(listdir(self._path_repo)) > 0:
            # not empty and not a git repo
            rm_dir(self._path_repo)
            self._path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)

        if is_set(self.repository.git_override_initialize):
            self._run_repo_hooks(
                cmds=self.repository.git_override_initialize,
                env=env,
            )
            return

        git_clone = ['git', 'clone', '--branch', self.repository.git_branch]

        if is_set(self.repository.git_limit_depth):
            git_clone.extend(['--depth', str(self.repository.git_limit_depth)])

        git_clone.extend([self._git_origin_with_credentials(), str(self._path_repo)])

        git_cmds = [' '.join(git_clone)]

        if self.repository.git_lfs:
            git_cmds.append('git lfs fetch')
            git_cmds.append('git lfs checkout')

        for cmd in git_cmds:
            self._repo_process(cmd=cmd, env=env)

    def update_repository(self, env: dict):
        if is_set(self.repository.git_override_update):
            self._run_repo_hooks(
                cmds=self.repository.git_override_update,
                env=env,
            )
            return

        git_pull = ['git', 'pull']

        if is_set(self.repository.git_limit_depth):
            git_pull.extend(['--depth', str(self.repository.git_limit_depth)])

        git_cmds = [
            'git reset --hard',
            ' '.join(git_pull),
        ]

        if self.repository.git_lfs:
            git_cmds.append('git lfs fetch')
            git_cmds.append('git lfs checkout')

        for cmd in git_cmds:
            self._repo_process(cmd=cmd, env=env)

    def create_or_update_repository(self):
        if is_null(self.repository) or self.repository.rtype_name == REPOSITORY_TYPE_STATIC:
            return

        if not self.repository.git_isolate and self.repository.is_running:
            # race condition
            return

        if self.execution is not None:
            self.repository.log_stderr = self.execution.log_stderr_repo
            self.repository.log_stdout = self.execution.log_stdout_repo

        else:
            self._logs_init()

        close_old_mysql_connections()
        self.repository.save()

        try:
            update_status(self.repository, status='Running')
            self.path_run.mkdir(mode=0o700, parents=True, exist_ok=True)

            self._log_file_write(f"PATH: {self._path_repo}")

            env = self._git_env()
            if len(env) > 0:
                env_str = str(env)
                if ENV_VAR_GIT_SECRET in env:
                    env_str = env_str.replace(env[ENV_VAR_GIT_SECRET], SECRET_HIDDEN_PLAIN)

                self._log_file_write(f"USING ENVIRONMENT: {env_str}")

            self._run_repo_hooks(cmds=self.repository.git_hook_pre, env=env)

            if not (self._path_repo / '.git').is_dir():
                self.create_repository(env=env)

            else:
                self.update_repository(env=env)

            self.repository.time_update = timezone.now()

            self._run_repo_hooks(cmds=self.repository.git_hook_post, env=env)

            update_status(self.repository, status='Finished')

        except AnsibleRepositoryError:
            raise

        # pylint: disable=W0718
        except Exception as err:
            self._error(msg=f"Got unexpected error: '{err}'")

        rm_dir(self.path_run_base)

    def _error(self, msg: str):
        write_file_0640(file=self.repository.log_stderr, content=msg)
        update_status(self.repository, status=JOB_EXEC_STATUS_FAILED)
        raise AnsibleRepositoryError(msg)

    def _git_env(self) -> dict:
        env = {
            'GIT_SSH_COMMAND': 'ssh -o ConnectTimeout=10',
            'GIT_HTTP_CONNECT_TIMEOUT': '10',
        }
        if self.repository.git_origin.find(' -p') != -1:
            try:
                self.repository.git_origin, port = self.repository.git_origin.split(' -p')
                env['GIT_SSH_COMMAND'] += f" -p {port}"

            except IndexError:
                pass

        if is_set(self.repository.git_credentials):
            if is_set(self.repository.git_credentials.ssh_key):
                write_pwd_file(credentials=self.repository.git_credentials, attr='ssh_key', path_run=self.path_run)
                env['GIT_SSH_COMMAND'] += f" -i {get_pwd_file(path_run=self.path_run, attr='ssh_key')}"

            if is_set(self.repository.git_credentials.connect_pass):
                env[ENV_VAR_GIT_SECRET] = self.repository.git_credentials.connect_pass

        ssh_known_hosts_file = get_ssh_known_hosts_file(self.repository, path_run=self.path_run)
        if ssh_known_hosts_file is not None:
            env['GIT_SSH_COMMAND'] += f" -o UserKnownHostsFile={ssh_known_hosts_file}"

        if env['GIT_SSH_COMMAND'] == 'ssh':
            env.pop('GIT_SSH_COMMAND')

        return env

    def get_project_dir(self) -> str:
        exec_id = None
        if self.execution is not None:
            exec_id = self.execution.id

        return str(get_path_play(
            repository=self.repository,
            exec_id=exec_id,
        ))

    def cleanup_repository(self):
        if is_null(self.repository) or self.repository.rtype_name == REPOSITORY_TYPE_STATIC:
            return

        self._run_repo_hooks(cmds=self.repository.git_hook_cleanup, env=self._git_env())
        if self.repository.git_isolate and not self.isolate_browsable:
            rm_dir(self._path_repo)

    def _get_path_repo(self) -> Path:
        exec_id = None
        if self.execution is not None:
            exec_id = self.execution.id

        return get_path_repo(repository=self.repository, exec_id=exec_id)

    def _repo_process(self, cmd: str, env: dict, hook: bool = False):
        if not hook:
            cmd = f'timeout {self.repository.git_timeout} {cmd}'

        result = process(cmd=cmd, cwd=self._path_repo, env=env, shell=True, timeout_sec=REPO_CLONE_TIMEOUT)
        self._log_file_write(f"COMMAND: {cmd}\n{result['stdout']}")
        if result['rc'] != 0:
            if result['stdout'].strip() != '':
                self._log_file_write(result['stdout'])

            self._error(
                f"Repository command failed: '{cmd}'\n"
                f"{result['stdout']}\n"
                f"{result['stderr']}"
            )

    def _run_repo_hooks(self, cmds: str, env: dict):
        if is_set(cmds):
            for cmd in cmds.split(','):
                self._repo_process(cmd=cmd, env=env, hook=True)

    def _git_origin_with_credentials(self) -> str:
        origin = self.repository.git_origin

        if not is_set(self.repository.git_credentials):
            return origin

        credentials = self.repository.git_credentials

        if origin.find('://') != -1 and origin.find('ssh://') == -1:
            # not ssh
            if origin.find('@') == -1:
                proto, origin_host = origin.split('://', 1)
                if is_set(credentials.connect_user) and is_set(credentials.connect_pass):
                    origin = f'{proto}://{credentials.connect_user}:${{{ENV_VAR_GIT_SECRET}}}@{origin_host}'

                elif is_set(credentials.connect_pass):
                    # token authentication
                    origin = f'{proto}://${{{ENV_VAR_GIT_SECRET}}}@{origin_host}'

        else:
            # ssh
            if origin.find('@') == -1 and is_set(credentials.connect_user):
                origin = f'{credentials.connect_user}@{origin}'

        return origin

    def _log_file_write(self, content: str):
        if self.repository.log_stdout is None:
            return

        write_file_0640(
            file=self.repository.log_stdout,
            content=f"{content}\n"
        )

    def _logs_init(self):
        safe_repo_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=self.repository.name)
        timestamp = datetime_w_tz().strftime(FILE_TIME_FORMAT)
        log_file = f"{config['path_log']}/repo_{safe_repo_name}_{timestamp}"
        self.repository.log_stdout = f'{log_file}_stdout_repo.log'
        self.repository.log_stderr = f'{log_file}_stderr_repo.log'


def create_update_git_repo(repo: Repository) -> bool:
    if is_null(repo) or repo.rtype_name == REPOSITORY_TYPE_STATIC:
        return False

    def _create_update(r: Repository):
        try:
            ExecuteRepository(r).create_or_update_repository()

        except Exception as e:
            error_lines = ' | '.join(str(e).split('\n'))
            log(msg=f"Got error creating/updating repository: {error_lines}", level=2)

    Thread(
        target=_create_update,
        kwargs={'r': repo}
    ).start()
    return True
