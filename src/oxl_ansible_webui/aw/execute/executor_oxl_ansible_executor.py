from pathlib import Path

from oxl_ansible_executor import Execution, ExecutionConfig, \
    ConfigError, SetupError, ExecutionStatus

from aw.config.main import config
from aw.utils.deployment import deployment_dev
from aw.utils.util import datetime_w_tz, is_set
from aw.utils.handlers import AnsibleConfigError
from aw.model.base import JOB_EXEC_STATUS_FAILED
from aw.config.environment import AW_ENV_VARS_SECRET
from aw.model.job_credential import BaseJobCredentials
from aw.execute.play_util import log_save_ansible_command
from aw.utils.db_handler import close_old_mysql_connections
from aw.execute.util import update_status, is_execution_status
from aw.model.job import Job, JobExecution, JobExecutionResult  # JobExecutionResultHost


def _parse_run_result(execution: JobExecution, db_result: JobExecutionResult, executor_result: ExecutionStatus):
    db_result.time_fin = datetime_w_tz()
    db_result.failed = executor_result.failed
    close_old_mysql_connections()
    db_result.save()

    # any_task_failed = False
    # todo: generate per-host stats (_run_stats) and check if any task failed (any_task_failed)

    if executor_result.failed or executor_result.timed_out:
        update_status(execution, status=JOB_EXEC_STATUS_FAILED)

    else:
        status = 'Finished'
        if is_execution_status(execution, 'Stopping') or executor_result.canceled:
            status = 'Stopped'

        update_status(execution, status=status)


def _build_credentials(creds: BaseJobCredentials) -> dict:
    kwargs = {
        'ssh_key': None,
        'connect_user': None,
        'connect_pass': None,
        'become_user': None,
        'become_pass': None,
        'vault_pass': None,
        'vault_id': None,
    }

    if is_set(creds):
        if is_set(creds.ssh_key):
            kwargs['ssh_key'] = creds.ssh_key

        if is_set(creds.connect_user):
            kwargs['connect_user'] = creds.connect_user

        if is_set(creds.connect_pass):
            kwargs['connect_pass'] = creds.connect_pass

        if is_set(creds.become_user):
            kwargs['become_user'] = creds.become_user

        if is_set(creds.become_pass):
            kwargs['become_pass'] = creds.become_pass

        if is_set(creds.vault_pass):
            kwargs['vault_pass'] = creds.vault_pass

        if is_set(creds.vault_id):
            kwargs['vault_id'] = creds.vault_id

    return kwargs


# pylint: disable=R0914
def executor_oxl_ansible_executor(
        job: Job, execution: (JobExecution, None), result: JobExecutionResult, creds: BaseJobCredentials,
        log_files: dict, ssh_known_hosts_file: (None, str, Path),
        executor_kwargs: dict,
):
    kwargs = executor_kwargs
    kwargs_creds = _build_credentials(creds=creds)
    debug = deployment_dev() or config['debug']

    try:
        c = ExecutionConfig(
            # user config
            playbook_dir=kwargs['project_dir'],
            playbook_file=kwargs['playbook'],
            inventory_files=kwargs['inventory'],
            mode_diff=execution.mode_diff or job.mode_diff,
            mode_check=execution.mode_check or job.mode_check,
            ssh_known_hosts_file=ssh_known_hosts_file,
            ssh_key_value=kwargs_creds['ssh_key'],
            connect_user=kwargs_creds['connect_user'],
            connect_pass_value=kwargs_creds['connect_pass'],
            become_user=kwargs_creds['become_user'],
            become_pass_value=kwargs_creds['become_pass'],
            vault_pass_value=kwargs_creds['vault_pass'],
            vault_id=kwargs_creds['vault_id'],
            limit=kwargs['limit'],
            tags=kwargs['tags'],
            skip_tags=kwargs['skip_tags'],
            verbosity=kwargs['verbosity'],
            cmd_args=kwargs['cmdline'],  # currently also used for 'extra_vars'
            env_vars=kwargs['envvars'],
            # system-relevant
            env_vars_strip=AW_ENV_VARS_SECRET,
            log_stdout_file=log_files['stdout'],
            log_stderr_file=log_files['stderr'],
            log_file_mode=0o640,
            timeout_sec_run=config['run_timeout'],
            debug=debug,
            output_color=True,
            run_dir=kwargs['private_data_dir'],
            # todo: containerization support
        )
        e = Execution(c)

        command_str = ' '.join(e.status.ansible_command)
        log_save_ansible_command(job=job, execution=execution, command=command_str)

        e.run(blocking=True)

    except (ConfigError, SetupError) as e:
        raise AnsibleConfigError(e)

    _parse_run_result(
        execution=execution,
        db_result=result,
        executor_result=e.status,
    )
