from pathlib import Path
from os import symlink
from os import path as os_path
from os import remove as remove_file

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/
from ansible_runner import Runner, RunnerConfig

from aw.config.main import config
from aw.execute.util import update_status
from aw.model.job_credential import BaseJobCredentials
from aw.execute.play_util import log_save_ansible_command
from aw.utils.db_handler import close_old_mysql_connections
from aw.utils.util import datetime_w_tz, timed_lru_cache, is_set
from aw.utils.filesystem import write_file_0640, overwrite_and_delete_file
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost
from aw.model.base import JOB_EXEC_STATUS_FAILED, JOB_EXEC_STATUS_SUCCESS, JOB_EXEC_STATUS_STOPPED


def _run_stats(pb_stats: dict, db_result: JobExecutionResult) -> bool:
    any_task_failed = False

    for host in pb_stats['processed']:
        result_host = JobExecutionResultHost(hostname=host)

        result_host.unreachable = host in pb_stats['dark']
        result_host.tasks_skipped = pb_stats['skipped'].get(host, 0)
        result_host.tasks_ok = pb_stats['ok'].get(host, 0)
        result_host.tasks_failed = pb_stats['failures'].get(host, 0)
        result_host.tasks_ignored = pb_stats['ignored'].get(host, 0)
        result_host.tasks_rescued = pb_stats['rescued'].get(host, 0)
        result_host.tasks_changed = pb_stats['changed'].get(host, 0)

        if result_host.unreachable:
            any_task_failed = True

        elif result_host.tasks_failed > 0:
            any_task_failed = True
            # todo: create errors

        result_host.result = db_result
        close_old_mysql_connections()
        result_host.save()

    return any_task_failed


def _parse_run_result(execution: JobExecution, db_result: JobExecutionResult, runner: Runner):
    db_result.time_fin = datetime_w_tz()
    db_result.failed = runner.errored
    close_old_mysql_connections()
    db_result.save()

    any_task_failed = False
    pb_stats = runner.stats
    if pb_stats is not None:
        any_task_failed = _run_stats(pb_stats=pb_stats, db_result=db_result)

    final_status = JOB_EXEC_STATUS_SUCCESS
    if execution.is_stopping or runner.canceled:
        final_status = JOB_EXEC_STATUS_STOPPED

    elif runner.errored or runner.timed_out or runner.rc != 0 or any_task_failed:
        final_status = JOB_EXEC_STATUS_FAILED

    update_status(execution, status=final_status)


def _runner_logs(cfg: RunnerConfig, log_files: dict):
    logs_src = {
        'stdout': os_path.join(cfg.artifact_dir, 'stdout'),
        'stderr': os_path.join(cfg.artifact_dir, 'stderr'),
    }

    for log_file in log_files.values():
        write_file_0640(file=log_file, content='')

    # link logs from artifacts to log-directory; have not found a working way of overriding the target files..
    for log_type in ['stdout', 'stderr']:
        try:
            symlink(log_files[log_type], logs_src[log_type])

        except FileExistsError:
            remove_file(logs_src[log_type])
            symlink(log_files[log_type], logs_src[log_type])


def _commandline_arguments(
        job: Job, execution: JobExecution, creds: (BaseJobCredentials, None),
        ssh_known_hosts_file: (None, str, Path),
) -> list[str]:
    cmd_arguments = []
    if execution.mode_check or job.mode_check:
        cmd_arguments.append('--check')

    if execution.mode_diff or job.mode_diff:
        cmd_arguments.append('--diff')

    if ssh_known_hosts_file is not None:
        cmd_arguments.append(
            f"-e 'ansible_ssh_extra_args=\"-o UserKnownHostsFile={ssh_known_hosts_file}\"'"
        )

    if is_set(creds):
        if is_set(creds.become_pass):
            cmd_arguments.append('--ask-become-pass')

        if is_set(creds.become_user):
            cmd_arguments.append(f'--become-user {creds.become_user}')

        if is_set(creds.connect_pass):
            cmd_arguments.append('--ask-pass')

        if is_set(creds.connect_user):
            cmd_arguments.append(f'--user {creds.connect_user}')

        if is_set(creds.vault_pass):
            cmd_arguments.append('--ask-vault-pass')

    return cmd_arguments


def _get_credentials_args(creds: BaseJobCredentials) -> dict:
    if not is_set(creds):
        return {'ssh_key': None, 'passwords': None}

    args = {}
    if is_set(creds.ssh_key):
        args['ssh_key'] = str(creds.ssh_key)

    else:
        args['ssh_key'] = None

    if is_set(creds.connect_pass) or is_set(creds.become_pass) or is_set(creds.vault_pass):
        args['passwords'] = {}
        if is_set(creds.connect_pass):
            args['passwords'][r'^SSH\spassword:\s*$'] = str(creds.connect_pass)

        if is_set(creds.become_pass):
            args['passwords'][r'^BECOME\spassword.*:\s*$'] = str(creds.become_pass)

        if is_set(creds.vault_pass):
            args['passwords'][r'^Vault\spassword:\s*$'] = str(creds.vault_pass)

    else:
        args['passwords'] = None

    return args


def _extend_options(
        job: Job, execution: (JobExecution, None), creds: BaseJobCredentials,
        ssh_known_hosts_file: (None, str, Path), executor_kwargs: dict,
) -> dict:
    cmdline_args = _commandline_arguments(
        job=job,
        execution=execution,
        creds=creds,
        ssh_known_hosts_file=ssh_known_hosts_file,
    )
    executor_kwargs['cmdline'].extend(cmdline_args)
    if len(executor_kwargs['cmdline']) == 0:
        executor_kwargs['cmdline'] = None

    else:
        # sadly passing a list[str] will throw an exception (as it wants to split a string)
        executor_kwargs['cmdline'] = ' '.join(executor_kwargs['cmdline'])

    creds_args = _get_credentials_args(creds=creds)
    return {
        **executor_kwargs,
        **creds_args,
    }


def executor_ansible_runner(
        job: Job, execution: (JobExecution, None), result: JobExecutionResult, creds: BaseJobCredentials,
        log_files: dict, ssh_known_hosts_file: (None, str, Path),
        executor_kwargs: dict,
):
    @timed_lru_cache(seconds=1)  # check actual status every N seconds; lower DB queries
    def _callback_cancel_job() -> bool:
        return execution.is_stopping

    kwargs = _extend_options(
        job=job,
        execution=execution,
        creds=creds,
        ssh_known_hosts_file=ssh_known_hosts_file,
        executor_kwargs=executor_kwargs,
    )
    path_run = kwargs.pop('private_data_dir')
    runner_cfg = RunnerConfig(
        # user config
        project_dir=kwargs.pop('project_dir'),
        playbook=kwargs.pop('playbook'),
        inventory=kwargs.pop('inventory'),
        passwords=kwargs.pop('passwords'),
        ssh_key=kwargs.pop('ssh_key'),
        limit=kwargs.pop('limit'),
        tags=kwargs.pop('tags'),
        skip_tags=kwargs.pop('skip_tags'),
        verbosity=kwargs.pop('verbosity'),
        envvars=kwargs.pop('envvars'),
        ## contains check-mode, diff-mode, extra-vars, ssh-known-hosts-file, users & password-flags, vault-id
        cmdline=kwargs.pop('cmdline'),
        extravars=kwargs.pop('extra_vars'),
        ## whatever we might've missed
        **kwargs,
        # system-relevant
        private_data_dir=path_run,
        timeout=config['run_timeout'],
        quiet=True,
        # todo: containerization support
    )
    _runner_logs(cfg=runner_cfg, log_files=log_files)

    runner_cfg.prepare()

    command_str = ' '.join(runner_cfg.command)
    log_save_ansible_command(job=job, execution=execution, command=command_str)

    runner = Runner(config=runner_cfg, cancel_callback=_callback_cancel_job)

    update_status(execution, status='Running')
    runner.run()

    _parse_run_result(
        execution=execution,
        db_result=result,
        runner=runner,
    )
    del runner

    overwrite_and_delete_file(f"{path_run}/env/passwords")
    overwrite_and_delete_file(f"{path_run}/env/ssh_key")
