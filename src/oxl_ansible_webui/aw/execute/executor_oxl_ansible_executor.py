from pathlib import Path
from time import sleep, time

from oxl_ansible_executor import Execution, ExecutionConfig, \
    ConfigError, SetupError, ExecutionStatus, AnsiblePlaybookStatsByHost

from aw.config.main import config
from aw.execute.util import update_status
from aw.utils.deployment import deployment_dev
from aw.utils.util import datetime_w_tz, is_set
from aw.utils.handlers import AnsibleConfigError
from aw.config.environment import AW_ENV_VARS_SECRET
from aw.model.job_credential import BaseJobCredentials
from aw.execute.play_util import log_save_ansible_command
from aw.utils.db_handler import close_old_mysql_connections
from aw.model.system import ANSIBLE_EXECUTOR_ENGINE_CONTAINERS
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost
from aw.model.base import JOB_EXEC_STATUS_FAILED, JOB_EXEC_STATUS_SUCCESS, JOB_EXEC_STATUS_STOPPED


def _run_stats(pb_stats: AnsiblePlaybookStatsByHost, db_result: JobExecutionResult) -> bool:
    any_task_failed = False

    for host, host_stats in pb_stats.items():
        result_host = JobExecutionResultHost(hostname=host)

        result_host.tasks_ok = host_stats['ok']
        result_host.tasks_changed = host_stats['changed']
        result_host.unreachable = host_stats['unreachable'] > 0
        result_host.tasks_failed = host_stats['failures']
        result_host.tasks_skipped = host_stats['skipped']
        result_host.tasks_rescued = host_stats['rescued']
        result_host.tasks_ignored = host_stats['ignored']

        if result_host.unreachable:
            any_task_failed = True

        elif result_host.tasks_failed > 0:
            any_task_failed = True
            # todo: create errors

        result_host.result = db_result
        close_old_mysql_connections()
        result_host.save()

    return any_task_failed


def _parse_run_result(execution: JobExecution, db_result: JobExecutionResult, executor_result: ExecutionStatus):
    db_result.time_fin = datetime_w_tz()
    close_old_mysql_connections()
    db_result.save()

    any_task_failed = False
    pb_stats = executor_result.status.stats
    if pb_stats is not None:
        any_task_failed = _run_stats(pb_stats=pb_stats, db_result=db_result)

    final_status = JOB_EXEC_STATUS_SUCCESS
    if execution.is_stopping or executor_result.canceled:
        final_status = JOB_EXEC_STATUS_STOPPED

    elif executor_result.failed or executor_result.timed_out or any_task_failed:
        db_result.failed = True
        final_status = JOB_EXEC_STATUS_FAILED

    update_status(execution, status=final_status)


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


def _execution_run_loop(job_exec: JobExecution, executor: Execution):
    was_stopped = False
    time_start = time()
    run_timeout = config['run_timeout']

    while job_exec.is_play_active and not executor.status.finished and (time() - run_timeout)  < time_start:
        sleep(1)
        if not was_stopped and job_exec.is_stopping:
            was_stopped = True
            executor.stop()


# pylint: disable=R0914
def executor_oxl_ansible_executor(
        job: Job, execution: (JobExecution, None), result: JobExecutionResult, creds: BaseJobCredentials,
        log_files: dict, ssh_known_hosts_file: (None, str, Path),
        executor_kwargs: dict,
):
    kwargs = executor_kwargs
    kwargs_creds = _build_credentials(creds=creds)
    debug = deployment_dev() or config['debug']
    job_exec = execution

    containerized = False
    container_engine = None
    container_image = None
    if config['ansible_executor_engine'] in ANSIBLE_EXECUTOR_ENGINE_CONTAINERS:
        containerized = True
        container_engine = ANSIBLE_EXECUTOR_ENGINE_CONTAINERS[config['ansible_executor_engine']]

    if is_set(config['ansible_executor_container_image']):
        container_image = config['ansible_executor_container_image']

    try:
        c = ExecutionConfig(
            # user config
            playbook_dir=kwargs['project_dir'],
            playbook_file=kwargs['playbook'],
            inventory_files=kwargs['inventory'],
            mode_diff=job_exec.mode_diff or job.mode_diff,
            mode_check=job_exec.mode_check or job.mode_check,
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
            cmd_args=kwargs['cmdline'],
            extra_vars=kwargs['extra_vars'],
            env_vars=kwargs['envvars'],
            # system-relevant
            env_vars_strip=AW_ENV_VARS_SECRET,
            log_stdout_file=log_files['stdout'],
            log_stderr_file=log_files['stderr'],
            load_log_stdout=False,
            load_log_stderr=False,
            log_file_mode=0o640,
            timeout_sec_run=config['run_timeout'],
            debug=debug,
            output_color=True,
            run_dir=kwargs['private_data_dir'],
            # engine
            stats_live=True,
            stats_recap=True,
            containerized=containerized,
            container_engine=container_engine,
            container_image=container_image,
        )
        executor = Execution(c)

        command_str = ' '.join(executor.status.ansible_command)
        log_save_ansible_command(job=job, execution=job_exec, command=command_str)

        update_status(job_exec, status='Running')
        executor.run(blocking=False)

        _execution_run_loop(job_exec=job_exec, executor=executor)

        _parse_run_result(
            execution=execution,
            db_result=result,
            executor_result=executor.status,
        )

    except (ConfigError, SetupError) as e:
        raise AnsibleConfigError(e)
