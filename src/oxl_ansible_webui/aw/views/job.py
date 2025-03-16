from django.shortcuts import render
from django.shortcuts import HttpResponse
# from django.urls import path
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper_kwargs
# from aw.views.forms.job import job_edit, job_clone, job_credentials_edit, job_repository_static_edit, \
#     job_repository_git_edit

LIMIT_JOB_RESULTS = 10
LIMIT_JOB_LOG_RESULTS = 50


@login_required
@ui_endpoint_wrapper_kwargs
def job_logs(request) -> HttpResponse:
    return render(request, status=200, template_name='job_logs.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper_kwargs
def job_credentials(request) -> HttpResponse:
    return render(request, status=200, template_name='job_credentials.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper_kwargs
def job_repository(request) -> HttpResponse:
    return render(request, status=200, template_name='job_repository.html', context={'show_update_time': True})


# urlpatterns_jobs = [
#     path('ui/jobs/credentials/<int:credentials_id>', job_credentials_edit),
#     path('ui/jobs/credentials', job_credentials),
#     path('ui/jobs/log', job_logs),
#     path('ui/jobs/manage/job/clone/<int:job_id>', job_clone),
#     path('ui/jobs/manage/job/<int:job_id>', job_edit),
#     path('ui/jobs/manage/job', job_edit),
#     path('ui/jobs/repository/static/<int:repo_id>', job_repository_static_edit),
#     path('ui/jobs/repository/git/<int:repo_id>', job_repository_git_edit),
#     path('ui/jobs/repository', job_repository),
# ]
