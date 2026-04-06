from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist

from aw.base import USERS
from aw.utils.debug import log
from aw.utils.util import is_set, is_null
from aw.execute.util import config_error
from aw.model.job import Job, JobExecution
from aw.utils.filesystem import write_file_0600
from aw.utils.db_handler import close_old_mysql_connections
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials
from aw.utils.permission import has_credentials_permission, CHOICE_PERMISSION_READ


def get_pwd_file(path_run: (str, Path), attr: str) -> str:
    return f"{path_run}/.aw_{attr}"


def write_pwd_file(credentials: BaseJobCredentials, attr: str, path_run: (Path, str)):
    if credentials is None or is_null(getattr(credentials, attr)):
        return None

    return write_file_0600(
        file=get_pwd_file(path_run=path_run, attr=attr),
        content=getattr(credentials, attr),
    )


def _scheduled_or_has_credentials_access(
        user: USERS, credentials: BaseJobCredentials, job_owner: (USERS, None),
) -> bool:
    user_to_check = user

    if user is None:
        # scheduled execution; permission has been checked at creation-time

        if job_owner is None:
            # else an unprivileged user could create a scheduled job that he has no privileges for;
            #   delete his own user; and get to run the job with full privileges..
            log(
                msg='Scheduled job has no owner defined. Maybe the old one got deleted? '
                    'Simply edit and save it to set a new owner!',
                level=4,
            )
            return False

        user_to_check = job_owner

    permitted = has_credentials_permission(
        user=user_to_check,
        credentials=credentials,
        permission_needed=CHOICE_PERMISSION_READ,
    )
    if not permitted:
        log(
            msg=f"User '{user_to_check.username}' has no permission to use credentials {credentials.name}",
            level=7,
        )

    return permitted


def get_credentials_to_use(job: Job, execution: JobExecution) -> (BaseJobCredentials, None):
    credentials = None

    # todo: write warn log if user tried to execute job using non-permitted credentials (if execution.cred*)
    if execution.user is not None and is_set(execution.credentials_user) and \
            execution.credentials_user.user.id == execution.user.id:
        credentials = execution.credentials_user

    elif execution.user is not None and is_set(execution.credentials_tmp) and \
            execution.credentials_tmp.user.id == execution.user.id:
        credentials = execution.credentials_tmp

    elif is_set(execution.credentials_shared) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=execution.credentials_shared, job_owner=job.owner,
    ):
        credentials = execution.credentials_shared

    elif is_set(job.credentials_default) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=job.credentials_default, job_owner=job.owner,
    ):
        credentials = job.credentials_default

    elif job.credentials_needed and is_set(execution.user):
        # get user credentials that match the job credential-category
        if is_set(job.credentials_category):
            close_old_mysql_connections()
            for user_creds in JobUserCredentials.objects.filter(user=execution.user):
                if user_creds.category == job.credentials_category:
                    credentials = user_creds
                    break

        if credentials is None:
            # try to get default user-credentials as a last-resort if the job needs some credentials
            try:
                close_old_mysql_connections()
                credentials = JobUserCredentials.objects.filter(user=execution.user).first()

            except ObjectDoesNotExist:
                pass

    if job.credentials_needed and credentials is None:
        config_error(
            'The job is set to require credentials - but none were provided or readable! '
            'Make sure you have privileges for the configured credentials or create user-specific ones.'
        )

    return credentials
