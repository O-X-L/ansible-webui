from aw.model.job import Job
from aw.model.job_credential import JobSharedCredentials
from aw.base import USERS, GROUPS
from aw.model.repository import Repository


def choices_job() -> list[tuple]:
    # todo: only show jobs the user is privileged to view => get_viewable_jobs(user)
    return [(job.id, job.name) for job in Job.objects.all()]


def choices_global_credentials() -> list[tuple]:
    # todo: only show credentials the user is privileged to view => get_viewable_credentials(user)
    return [(credentials.id, credentials.name) for credentials in JobSharedCredentials.objects.all()]


# def choices_credentials(user: USERS) -> dict:
#     return {
#         'global': [
#             (c.id, c.name) for c in JobSharedCredentials.objects.all()
#             if has_credentials_permission(user, c, CHOICE_PERMISSION_READ)
#         ],
#         'user': [(c.id, c.name) for c in JobUserCredentials.objects.filter(user=user)],
#     }


def choices_repositories() -> list[tuple]:
    # todo: only show credentials the user is privileged to view => get_viewable_credentials(user)
    return [(repo.id, repo.name) for repo in Repository.objects.all()]


def choices_user() -> list[tuple]:
    return [(user.id, user.username) for user in USERS.objects.all() if user.username != 'schedule']


def choices_group() -> list[tuple]:
    return [(group.id, group.name) for group in GROUPS.objects.all()]
