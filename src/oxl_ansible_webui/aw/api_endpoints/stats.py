from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist

from aw.config.main import config
from aw.api_endpoints.base import get_api_user, GenericResponse, API_PERMISSION, API_PARAM_HASH, \
    response_data_if_changed
from aw.utils.permission import get_viewable_jobs
from aw.model.job import JobExecution, JobExecutionResultHost, Job
from aw.utils.util import datetime_w_tz
from aw.model.base import JOB_EXEC_STATI_INACTIVE, JOB_EXEC_STATUS_SUCCESS, JOB_EXEC_STATUS_FAILED, \
    JOB_EXEC_STATUS_STOPPED
from aw.base import USERS


def relative_time_to_dt(t: str) -> (datetime, None):
    # pylint: disable=R0911
    if t.isnumeric():
        return datetime.fromtimestamp(int(t), tz=config.timezone)

    if t.replace('.', '').isnumeric():
        return datetime.fromtimestamp(float(t), tz=config.timezone)

    n = datetime_w_tz()

    tt, tf = t[:-1], t[-1]
    if not tt.isnumeric():
        return None

    tt = int(tt)

    if tf == 'm':
        return n - timedelta(minutes=tt)

    if tf == 'h':
        return n - timedelta(hours=tt)

    if tf == 'd':
        return n - timedelta(days=tt)

    if tf == 'w':
        return n - timedelta(weeks=tt)

    if tf == 'M':
        return n - timedelta(days=tt * 30)

    return datetime.timestamp(n)


def _build_stats_jobs_query_limits(request, job_ids: list[Job]) -> dict:
    # pylint: disable=R0912
    if 'limit_jobs' in request.GET:
        job_ids_new = []
        for limit_job in request.GET['limit_jobs'].split(','):
            if limit_job.isnumeric():
                limit_job = int(limit_job)
                if limit_job in job_ids:
                    job_ids_new.append(limit_job)

        job_ids = job_ids_new

    limits = {'job__in': job_ids}
    limit_time = None
    if 'limit_time' in request.GET:
        limit_time = relative_time_to_dt(request.GET['limit_time'])

    if limit_time is None:
        limit_time = relative_time_to_dt('1w')

    limits['created__gte'] = limit_time

    if 'limit_users' in request.GET:
        limit_users = []

        if request.GET['limit_users'].lower() == 'schedule':
            limits['user__isnull'] = True

        else:
            for limit_user in request.GET['limit_users'].split(','):
                try:
                    user = USERS.objects.get(username=limit_user)
                    if user is None:
                        continue

                    limit_users.append(user.id)

                except ObjectDoesNotExist:
                    continue

            limits['user__in'] = limit_users

    if 'failed' in request.GET:
        if request.GET['failed']:
            limits['status'] = JOB_EXEC_STATUS_FAILED

        else:
            limits['status__in'] = [JOB_EXEC_STATUS_SUCCESS, JOB_EXEC_STATUS_STOPPED]

    return limits


class APIStatsJobs(APIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    @staticmethod
    @extend_schema(
        request=None,
        responses={200: GenericResponse},
        summary='Return execution-stats for all jobs the current user is privileged to view',
        operation_id='stats_jobs',
        parameters=[
            API_PARAM_HASH,
            OpenApiParameter(
                name='limit_jobs', type=str, default='',
                description='Comma-separated list of job-ids to filter the stats on',
                required=False,
            ),
            OpenApiParameter(
                name='limit_time', type=int, default='',
                description='Point in time from which the stats should be generated.'
                            "Either a timestamp or relative. Example: 30m,2h,3d,2w,1M",
                required=False,
            ),
            OpenApiParameter(
                name='limit_users', type=str, default='',
                description='Comma-separated list of users to filter the stats on',
                required=False,
            ),
            OpenApiParameter(
                name='failed', type=bool, default=None,
                description='Supply to only get failed or succeeded executions',
                required=False,
            ),
        ]
    )
    def get(request):
        user = get_api_user(request)
        job_ids = [job.id for job in get_viewable_jobs(user)]

        execs = JobExecution.objects.filter(
            status__in=JOB_EXEC_STATI_INACTIVE,
            **_build_stats_jobs_query_limits(request, job_ids),
        ).order_by('-created')

        data = {
            'stats': [],
            'mapping': {
                'jobs': {},
                'users': {},
                'status': {},
                'stats': [
                    'job',
                    'status',
                    'user',
                    'duration',
                    'time',
                    'failed',
                    'host_stats',
                ],
                'host_stats': JobExecutionResultHost.STATS_SHORT,
            }
        }

        for e in execs:
            user_id = None if e.user is None else e.user.id
            data['stats'].append([
                e.job.id,
                e.status,
                user_id,
                e.time_duration_sec,
                e.time_fin_ts,
                1 if e.failed else 0,
                e.get_stats_short(),
            ])
            data['mapping']['jobs'][e.job.id] = e.job.name
            data['mapping']['users'][user_id] = e.user_name
            data['mapping']['status'][e.status] = e.status_name

        if len(data['stats']) == 0:
            return Response(data=None, status=304)

        return response_data_if_changed(request, data)
