from pathlib import Path
from os import symlink
from os import path as os_path
from os import remove as remove_file

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/
from ansible_runner import Runner, RunnerConfig

from aw.utils.debug import log
from aw.config.main import config
from aw.model.base import JOB_EXEC_STATUS_FAILED
from aw.model.job_credential import BaseJobCredentials
from aw.utils.db_handler import close_old_mysql_connections
from aw.execute.util import update_status, is_execution_status
from aw.utils.util import datetime_w_tz, timed_lru_cache, is_set
from aw.utils.filesystem import write_file_0640, overwrite_and_delete_file
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost


def _run_stats(runner: Runner, result: JobExecutionResult) -> bool:
    any_task_failed = False
    for host in runner.stats['processed']:
        result_host = JobExecutionResultHost(hostname=host)

        result_host.unreachable = host in runner.stats['dark']
        result_host.tasks_skipped = runner.stats['skipped'][host] if host in runner.stats['skipped'] else 0
        result_host.tasks_ok = runner.stats['ok'][host] if host in runner.stats['ok'] else 0
        result_host.tasks_failed = runner.stats['failures'][host] if host in runner.stats['failures'] else 0
        result_host.tasks_ignored = runner.stats['ignored'][host] if host in runner.stats['ignored'] else 0
        result_host.tasks_rescued = runner.stats['rescued'][host] if host in runner.stats['rescued'] else 0
        result_host.tasks_changed = runner.stats['changed'][host] if host in runner.stats['changed'] else 0

        if result_host.unreachable:
            any_task_failed = True

        elif result_host.tasks_failed > 0:
            any_task_failed = True
            # todo: create errors

        result_host.result = result
        close_old_mysql_connections()
        result_host.save()

    return any_task_failed


def _parse_run_result(execution: JobExecution, result: JobExecutionResult, runner: Runner):
    result.time_fin = datetime_w_tz()
    result.failed = runner.errored
    close_old_mysql_connections()
    result.save()

    any_task_failed = False
    if runner.stats is not None:
        any_task_failed = _run_stats(runner=runner, result=result)

    if runner.errored or runner.timed_out or runner.rc != 0 or any_task_failed:
        update_status(execution, status=JOB_EXEC_STATUS_FAILED)

    else:
        status = 'Finished'
        if is_execution_status(execution, 'Stopping') or runner.canceled:
            status = 'Stopped'

        update_status(execution, status=status)


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
) -> str:
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

    return ' '.join(cmd_arguments)


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
            args['passwords'][r'^SSH\spassword:\s*$'] = f'{creds.connect_pass}'

        if is_set(creds.become_pass):
            args['passwords'][r'^BECOME\spassword.*:\s*$'] = f'{creds.become_pass}'

        if is_set(creds.vault_pass):
            args['passwords'][r'^Vault\spassword:\s*$'] = f'{creds.vault_pass}'

    else:
        args['passwords'] = None

    return args


def _extend_options(
        job: Job, execution: (JobExecution, None), creds: BaseJobCredentials,
        ssh_known_hosts_file: (None, str, Path), executor_options: dict,
) -> dict:
    cmdline_args = _commandline_arguments(
        job=job,
        execution=execution,
        creds=creds,
        ssh_known_hosts_file=ssh_known_hosts_file,
    )
    executor_options['cmdline'].extend(cmdline_args)

    creds_args = _get_credentials_args(creds=creds)
    return {
        **executor_options,
        **creds_args,
    }


def executor_ansible_runner(
        job: Job, execution: (JobExecution, None), result: JobExecutionResult, creds: BaseJobCredentials,
        log_files: dict, ssh_known_hosts_file: (None, str, Path),
        executor_options: dict,
):
    @timed_lru_cache(seconds=1)  # check actual status every N seconds; lower DB queries
    def _cancel_job() -> bool:
        return is_execution_status(execution, 'Stopping')

    opts = _extend_options(
        job=job,
        execution=execution,
        creds=creds,
        ssh_known_hosts_file=ssh_known_hosts_file,
        executor_options=executor_options,
    )
    path_run = opts.pop('private_data_dir')
    runner_cfg = RunnerConfig(
        # user config
        project_dir=opts.pop('project_dir'),
        playbook=opts.pop('playbook'),
        inventory=opts.pop('inventory'),
        passwords=opts.pop('passwords'),
        ssh_key=opts.pop('ssh_key'),
        limit=opts.pop('limit'),
        tags=opts.pop('tags'),
        skip_tags=opts.pop('skip_tags'),
        verbosity=opts.pop('verbosity'),
        envvars=opts.pop('envvars'),
        ## contains check-mode, diff-mode, extra-vars, ssh-known-hosts-file, users & password-flags, vault-id
        cmdline=opts.pop('cmdline'),
        ## whatever we might've missed..
        **opts,
        # system-relevant
        private_data_dir=path_run,
        timeout=config['run_timeout'],
        quiet=True,
        # todo: containerization support
    )
    _runner_logs(cfg=runner_cfg, log_files=log_files)

    runner_cfg.prepare()
    command = ' '.join(runner_cfg.command)
    log(msg=f"Running job '{job.name}': '{command}'", level=5)
    execution.command = command[command.find('ansible-playbook'):]
    close_old_mysql_connections()
    execution.save()

    runner = Runner(config=runner_cfg, cancel_callback=_cancel_job)
    runner.run()

    _parse_run_result(
        result=result,
        execution=execution,
        runner=runner,
    )
    del runner

    overwrite_and_delete_file(f"{path_run}/env/passwords")
    overwrite_and_delete_file(f"{path_run}/env/ssh_key")
