from pathlib import Path

from django.db.models import Q

from aw.base import USERS
from aw.utils.util import ansible_log_text, ansible_log_html
from aw.model.job import Job, JobExecution
from aw.utils.permission import has_job_permission, CHOICE_PERMISSION_READ
from aw.model.alert import BaseAlert, AlertUser, AlertGroup, AlertGlobal, \
    ALERT_CONDITION_FAIL, ALERT_CONDITION_SUCCESS, ALERT_CONDITION_ALWAYS, \
    ALERT_TYPE_PLUGIN
from aw.execute.alert_plugin.plugin_email import alert_plugin_email
from aw.execute.alert_plugin.plugin_wrapper import alert_plugin_wrapper
from aw.utils.db_handler import close_old_mysql_connections


class Alert:
    def __init__(self, job: Job, execution: JobExecution):
        self.job = job
        self.execution = execution
        self.failed = execution.has_failed
        self.privileged_users = []
        close_old_mysql_connections()
        for user in USERS.objects.all():
            if has_job_permission(user=user, job=job, permission_needed=CHOICE_PERMISSION_READ):
                self.privileged_users.append(user)

        self.error_msgs = {'html': [], 'text': []}
        self._get_task_errors()

    def _get_task_errors(self):
        if self.failed and Path(self.execution.log_stdout).is_file():
            with open(self.execution.log_stdout, 'r', encoding='utf-8') as _f:
                for line in _f.readlines():
                    line_text = ansible_log_text(line)
                    line_html = ansible_log_html(line)
                    if line_text.startswith('fatal: '):
                        self.error_msgs['html'].append(line_html)
                        self.error_msgs['text'].append(line_text)

    def _job_filter(self, model: type):
        close_old_mysql_connections()
        return model.objects.filter(Q(jobs=self.job) | Q(jobs_all=True))

    def _condition_filter(self, alerts: list[BaseAlert]):
        matching = []
        for alert in alerts:
            if alert.condition == ALERT_CONDITION_ALWAYS or \
                    (self.failed and alert.condition == ALERT_CONDITION_FAIL) or \
                    (not self.failed and alert.condition == ALERT_CONDITION_SUCCESS):
                matching.append(alert)

        return matching

    def _route(self, alert: BaseAlert, user: USERS):
        if alert.alert_type == ALERT_TYPE_PLUGIN:
            alert_plugin_wrapper(
                alert=alert,
                user=user,
                stats=self.execution.get_stats(),
                execution=self.execution,
                failed=self.failed,
                error_msgs=self.error_msgs,
            )

        else:
            alert_plugin_email(
                user=user,
                stats=self.execution.get_stats(),
                execution=self.execution,
                error_msgs=self.error_msgs,
            )

    def _global(self):
        for alert in self._condition_filter(self._job_filter(AlertGlobal)):
            for user in self.privileged_users:
                self._route(alert=alert, user=user)

    def _group(self):
        for alert in self._condition_filter(self._job_filter(AlertGroup)):
            for user in self.privileged_users:
                if user.groups.filter(name=alert.group).exists():
                    self._route(alert=alert, user=user)

    def _user(self):
        for user in self.privileged_users:
            for alert in self._condition_filter(self._job_filter(AlertUser).filter(user=user)):
                self._route(alert=alert, user=user)

    def go(self):
        self._global()
        self._group()
        self._user()
