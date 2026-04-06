import traceback

from django.db.utils import OperationalError, IntegrityError
from oxl_ansible_executor import ExecutionError, PreparationError

from aw.config.main import config
from aw.model.system import ANSIBLE_EXECUTOR_OXL
from aw.model.job import Job, JobExecution, JobExecutionResult
from aw.execute.play_util import executor_cleanup, executor_prep, failure
from aw.execute.util import get_path_run, job_logs
from aw.execute.repository import ExecuteRepository
from aw.execute.alert import Alert
from aw.utils.util import datetime_w_tz, is_null  # get_ansible_versions
from aw.utils.handlers import AnsibleConfigError, AnsibleRepositoryError
from aw.utils.debug import log
from aw.utils.db_handler import close_old_mysql_connections
from aw.utils.audit import log_audit
from aw.execute.executor_ansible_runner import executor_ansible_runner
from aw.execute.executor_oxl_ansible_executor import executor_oxl_ansible_executor
from aw.execute.ssh_hostkey import get_ssh_known_hosts_file
from aw.execute.play_credentials import get_credentials_to_use
from aw.model.job_credential import JobUserTMPCredentials


def _log_audit(job: Job, execution: JobExecution):
    user = execution.user
    if user is None:
        user = job.owner

    if user is None:
        log(msg=f"Execution of job '{job.name}' has neither user nor owner!", level=3)
        return

    log_audit(
        user=user,
        title='Job execute',
        msg=f"Job executed: ID '{execution.id}', Job-ID '{job.id}', Name '{job.name}', Comment '{execution.comment}'"
    )


def ansible_playbook(job: Job, execution: (JobExecution, None)):
    time_start = datetime_w_tz()
    path_run = get_path_run()
    path_run.mkdir(mode=0o750, parents=True, exist_ok=True)

    if is_null(execution):
        execution = JobExecution(user=None, job=job, comment='Scheduled')

    _log_audit(job, execution)

    result = JobExecutionResult(time_start=time_start)
    close_old_mysql_connections()
    result.save()

    execution.result = result
    close_old_mysql_connections()
    execution.save()

    log_files = job_logs(job=job, execution=execution)
    ssh_known_hosts_file = get_ssh_known_hosts_file(job, path_run=path_run)
    exec_repo = ExecuteRepository(repository=job.repository, execution=execution, path_run=path_run)

    creds = get_credentials_to_use(job=job, execution=execution)
    if isinstance(creds, JobUserTMPCredentials):
        creds.cleanup_secret(remove_file=False)

    try:
        exec_repo.create_or_update_repository()
        project_dir = exec_repo.get_project_dir()
        executor_options = executor_prep(job=job, execution=execution, path_run=path_run, project_dir=project_dir)
        close_old_mysql_connections()
        execution.save()

        if config['ansible_executor'] == ANSIBLE_EXECUTOR_OXL:
            executor_oxl_ansible_executor(
                job=job,
                execution=execution,
                result=result,
                log_files=log_files,
                ssh_known_hosts_file=ssh_known_hosts_file,
                executor_options=executor_options,
                creds=creds,
            )

        else:
            executor_ansible_runner(
                job=job,
                execution=execution,
                result=result,
                log_files=log_files,
                ssh_known_hosts_file=ssh_known_hosts_file,
                executor_options=executor_options,
                creds=creds,
            )

        executor_cleanup(execution=execution, path_run=path_run, exec_repo=exec_repo)
        Alert(job=job, execution=execution).go()

    except (
            AnsibleConfigError, AnsibleRepositoryError,
            OSError, ValueError, AttributeError, IndexError, KeyError,
            OperationalError, IntegrityError,
            ExecutionError, PreparationError,
    ) as err:
        tb = traceback.format_exc(limit=1024)
        failure(
            execution=execution, exec_repo=exec_repo, path_run=path_run, result=result,
            error_s=str(err), error_m=tb,
        )
        Alert(job=job, execution=execution).go()
        raise
