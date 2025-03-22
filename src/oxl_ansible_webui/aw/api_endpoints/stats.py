from datetime import datetime, timedelta

from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist

from aw.api_endpoints.base import get_api_user, GenericResponse, API_PERMISSION, API_PARAM_HASH, \
    response_data_if_changed
from aw.utils.permission import get_viewable_jobs
from aw.model.job import JobExecution
from aw.utils.util import datetime_w_tz
from aw.model.base import JOB_EXEC_STATI_INACTIVE, JOB_EXEC_STATUS_SUCCESS, JOB_EXEC_STATUS_FAILED, \
    JOB_EXEC_STATUS_STOPPED
from aw.base import USERS


def relative_time_to_timestamp(t: str) -> (int, float, None):
    if t.isnumeric():
        return int(t)

    if t.replace('.', '').isnumeric():
        return float(t)

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


class APIStatsJobs(APIView):
    http_method_names = ['get']
    serializer_class = GenericResponse
    permission_classes = API_PERMISSION

    # todo: params that allow for limit
    #    by job
    #    time period (1w,2w,1m)
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

        if 'limit_jobs' in request.GET:
            job_ids_new = []
            for limit_job in request.GET['limit_jobs'].split(','):
                if limit_job.isnumeric():
                    limit_job = int(limit_job)
                    if limit_job in job_ids:
                        job_ids_new.append(limit_job)

            job_ids = job_ids_new

        limits = {}
        if 'limit_time' in request.GET:
            limits['created__gte'] = relative_time_to_timestamp(request.GET['limit_time'])

        if 'limit_users' in request.GET:
            limit_users = []

            if request.GET['limit_users'].lower() == 'scheduled':
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

        execs = JobExecution.objects.filter(
            job__in=job_ids,
            status__in=JOB_EXEC_STATI_INACTIVE,
            **limits,
        ).order_by('-created')

        data = []
        for e in execs:
            data.append({
                'job': e.job.id,
                'job_name': e.job.name,
                'status': e.status_name,
                'user': e.user_name,
                'duration': e.time_duration,
                'time': e.time_fin_ts,
                'failed': e.failed,
                'stats': e.get_stats(),
            })

        return response_data_if_changed(request, data)
