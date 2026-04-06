from pathlib import Path
from os import remove as remove_file
from os import stat as os_stat

try:
    from ara.setup.callback_plugins import callback_plugins as ara_callback_plugins

except (ImportError, ModuleNotFoundError):
    ara_callback_plugins = None

from aw.utils.debug import log
from aw.config.main import config
from aw.utils.filesystem import rm_dir
from aw.utils.util import is_set, datetime_w_tz
from aw.model.base import JOB_EXEC_STATUS_FAILED
from aw.execute.repository import ExecuteRepository
from aw.utils.db_handler import close_old_mysql_connections
from aw.model.job import Job, JobExecution, JobExecutionResult, JobError
from aw.execute.util import update_status, decode_job_env_vars, create_dirs, config_error


def _exec_log(execution: JobExecution, msg: str, level: int = 3):
    # todo: add execution logs to UI (?)
    log(
        msg=f"Job-execution '{execution.job}' @ {execution.result.time_start}: {msg}",
        level=level,
    )


def _environmental_variables(job: Job, execution: JobExecution) -> dict:
    # merge global, job + execution env-vars
    env_vars = {}
    if is_set(config['ara_server']):
        if ara_callback_plugins is None:
            _exec_log(
                execution=execution,
                msg="Ignoring 'ara_server' setting because 'ara' module is not installed'",
                level=3,
            )

        else:
            env_vars['ANSIBLE_CALLBACK_PLUGINS'] = ara_callback_plugins
            env_vars['ARA_API_CLIENT'] = 'http'
            env_vars['ARA_API_SERVER'] = config['ara_server']

    if is_set(config['global_environment_vars']):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=config['global_environment_vars'], src='Global')
        }

    if is_set(job.environment_vars) and is_set(job.environment_vars.strip()):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=job.environment_vars, src='Job')
        }

    if is_set(execution.environment_vars):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=execution.environment_vars, src='Execution')
        }

    # ansible-runner will default to 'False' if it's not set :(
    if 'ANSIBLE_HOST_KEY_CHECKING' not in env_vars:
        env_vars['ANSIBLE_HOST_KEY_CHECKING'] = True

    # pass aw-metadata to ansible (https://github.com/O-X-L/ansible-webui/issues/5)
    if is_set(job.owner):
        env_vars['AW_OWNER_USER'] = job.owner.username
        env_vars['AW_OWNER_EMAIL'] = job.owner.email

    if is_set(execution.user):
        env_vars['AW_EXECUTION_USER'] = execution.user.username
        env_vars['AW_EXECUTION_EMAIL'] = execution.user.email

    return env_vars


def _execution_or_job(job: Job, execution: JobExecution, attr: str):
    exec_val = getattr(execution, attr)
    if is_set(exec_val):
        return exec_val

    job_val = getattr(job, attr)
    if is_set(job_val):
        return job_val

    return None


def _executor_options(
        job: Job, execution: JobExecution, path_run: Path, project_dir: str,
) -> dict:
    verbosity = None
    if execution.verbosity != 0:
        verbosity = execution.verbosity

    elif job.verbosity != 0:
        verbosity = job.verbosity

    cmdline_args = []
    if is_set(job.cmd_args):
        cmdline_args.append(job.cmd_args)

    if is_set(execution.cmd_args):
        cmdline_args.append(execution.cmd_args)

    opts = {
        'project_dir': project_dir,
        'private_data_dir': path_run,
        'limit': _execution_or_job(job, execution, 'limit'),
        'tags': _execution_or_job(job, execution, 'tags'),
        'skip_tags': _execution_or_job(job, execution, 'tags_skip'),
        'verbosity': verbosity,
        'envvars': _environmental_variables(job=job, execution=execution),
        'cmdline': cmdline_args,
    }

    return opts


def executor_prep(job: Job, execution: JobExecution, path_run: Path, project_dir: str) -> dict:
    update_status(execution, status='Starting')

    opts = _executor_options(job=job, execution=execution, path_run=path_run, project_dir=project_dir)
    opts['playbook'] = job.playbook_file
    if is_set(job.inventory_file):
        opts['inventory'] = job.inventory_file.split(',')

    # https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout
    ppf = Path(opts['project_dir']) / opts['playbook']
    if not Path(ppf).is_file():
        config_error(f"Configured playbook not found: '{ppf}'")

    if 'inventory' in opts:
        for inventory in opts['inventory']:
            pi = Path(opts['project_dir']) / inventory
            if not Path(pi).exists():
                config_error(f"Configured inventory not found: '{pi}'")

    create_dirs(path=path_run, desc='run')
    create_dirs(path=config['path_log'], desc='log')

    update_status(execution, status='Running')
    return opts


def executor_cleanup(execution: JobExecution, path_run: Path, exec_repo: ExecuteRepository):
    if is_set(execution.credentials_tmp):
        execution.credentials_tmp.cleanup_secret(remove_file=True)
        execution.credentials_tmp.delete()

    try:
        exec_repo.cleanup_repository()

    except AttributeError as err:
        log(msg=f'Got error of repository cleanup: {err}')

    # clean empty log files
    for log_file in JobExecution.log_file_fields:
        log_file_path = getattr(execution, log_file)
        try:
            if os_stat(log_file_path).st_size == 0:
                remove_file(log_file_path)

        except (FileNotFoundError, TypeError):
            pass

    rm_dir(path_run)


def failure(
        execution: JobExecution, exec_repo: ExecuteRepository, path_run: Path,
        result: JobExecutionResult, error_s: str, error_m: str
):
    update_status(execution, status=JOB_EXEC_STATUS_FAILED)
    job_error = JobError(
        short=error_s,
        med=error_m,
    )
    close_old_mysql_connections()
    job_error.save()
    result.time_fin = datetime_w_tz()
    result.failed = True
    result.error = job_error
    close_old_mysql_connections()
    result.save()
    close_old_mysql_connections()
    execution.save()

    executor_cleanup(execution=execution, path_run=path_run, exec_repo=exec_repo)
