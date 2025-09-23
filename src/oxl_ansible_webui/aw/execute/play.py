import traceback

from django.db.utils import OperationalError, IntegrityError
from ansible_runner import RunnerConfig, Runner

from aw.config.main import config
from aw.model.job import Job, JobExecution, JobExecutionResult
from aw.execute.play_util import runner_cleanup, runner_prep, parse_run_result, failure, runner_logs
from aw.execute.util import get_path_run, is_execution_status, job_logs
from aw.execute.repository import ExecuteRepository
from aw.execute.alert import Alert
from aw.utils.util import datetime_w_tz, is_null, timed_lru_cache  # get_ansible_versions
from aw.utils.handlers import AnsibleConfigError, AnsibleRepositoryError
from aw.utils.debug import log
from aw.utils.db_handler import close_old_mysql_connections


class AwRunnerConfig(RunnerConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, timeout=config['run_timeout'], quiet=True)



def _tmp_dump_runner_config(cfg: RunnerConfig):
    attrs = {}
    for attr in [
        'runner_mode',
        'playbook',
        'inventory',
        'roles_path',
        'limit',
        'module',
        'module_args',
        'host_pattern',
        'binary',
        'extra_vars',
        'process_isolation_path',
        'process_isolation_path_actual',
        'process_isolation_hide_paths',
        'process_isolation_show_paths',
        'process_isolation_ro_paths',
        'directory_isolation_path',
        'verbosity',
        'suppress_output_file',
        'suppress_ansible_output',
        'tags',
        'skip_tags',
        'execution_mode',
        'forks',
        'cmdline_args',
        'omit_event_data',
        'only_failed_event_data',
        'host_cwd',
        'envvars',
        'ssh_key_data',
        'command:',
        'process_isolation',
        'process_isolation_executable',
        'container_image',
        'container_volume_mounts',
        'container_workdir',
        'container_auth_data',
        'registry_auth_path:',
        'container_name:',
        'container_options',
        'rotate_artifacts',
        'quiet',
        'json_mode',
        'passwords',
        'settings',
        'timeout',
        'check_job_event_data',
        'suppress_env_files',
        'private_data_dir',
        'ident',
        'artifact_dir',
        'private_data_dir,',
        'rotate_artifacts',
        'fact_cache_type',
        'fact_cache_type',
        'loader',
        'host_cwd',
        'cwd',
    ]:
        attrs[attr] = getattr(cfg, attr)

    with open('/tmp/runner_config.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join([f'{k}={v}' for k, v in attrs.items()]))

    raise ValueError(attrs)


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime_w_tz()
    path_run = get_path_run()
    if is_null(execution):
        execution = JobExecution(user=None, job=job, comment='Scheduled')

    result = JobExecutionResult(time_start=time_start)
    close_old_mysql_connections()
    result.save()

    execution.result = result
    close_old_mysql_connections()
    execution.save()

    log_files = job_logs(job=job, execution=execution)

    @timed_lru_cache(seconds=1)  # check actual status every N seconds; lower DB queries
    def _cancel_job() -> bool:
        return is_execution_status(execution, 'Stopping')

    exec_repo = ExecuteRepository(repository=job.repository, execution=execution, path_run=path_run)
    try:
        exec_repo.create_or_update_repository()
        project_dir = exec_repo.get_project_dir()
        opts = runner_prep(job=job, execution=execution, path_run=path_run, project_dir=project_dir)
        close_old_mysql_connections()
        execution.save()
        runner_cfg = AwRunnerConfig(**opts)
        runner_logs(cfg=runner_cfg, log_files=log_files)
        runner_cfg.prepare()
        command = ' '.join(runner_cfg.command)
        log(msg=f"Running job '{job.name}': '{command}'", level=5)
        execution.command = command[command.find('ansible-playbook'):]
        close_old_mysql_connections()
        execution.save()

        _tmp_dump_runner_config(runner_cfg)
        runner = Runner(config=runner_cfg, cancel_callback=_cancel_job)
        runner.run()

        parse_run_result(
            result=result,
            execution=execution,
            runner=runner,
        )
        del runner

        runner_cleanup(execution=execution, path_run=path_run, exec_repo=exec_repo)
        Alert(job=job, execution=execution).go()

    except (
            AnsibleConfigError, AnsibleRepositoryError,
            OSError, ValueError, AttributeError, IndexError, KeyError,
            OperationalError, IntegrityError,
    ) as err:
        tb = traceback.format_exc(limit=1024)
        failure(
            execution=execution, exec_repo=exec_repo, path_run=path_run, result=result,
            error_s=str(err), error_m=tb,
        )
        Alert(job=job, execution=execution).go()
        raise
