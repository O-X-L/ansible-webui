from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from aw.api_endpoints.key import APIKey, APIKeyItem
from aw.api_endpoints.job import APIJob, APIJobItem, APIJobExecutionItem, APIJobExecutionLogs, \
    APIJobExecutionLogFile, APIJobExecution, APIJobExecutionSingleJob
from aw.api_endpoints.permission import APIPermission, APIPermissionItem
from aw.api_endpoints.credentials import APIJobCredentials, APIJobSharedCredentials, \
    APIJobSharedCredentialsItem, APIJobUserCredentialsItem, APIJobUserCredentials, APIJobTMPCredentials
from aw.api_endpoints.filesystem import APIFsBrowse, APIFsExists
from aw.api_endpoints.system import APISystemConfig, APISystemEnvironment, APIUserPasswordChange
from aw.api_endpoints.repository import APIRepository, APIRepositoryItem, APIRepositoryLogFile
from aw.api_endpoints.alert import APIAlertPlugin, APIAlertPluginItem, APIAlertUser, APIAlertUserItem, \
    APIAlertGlobal, APIAlertGlobalItem, APIAlertGroup, APIAlertGroupItem, APIAlertAll
from aw.api_endpoints.frontend import APIBackendInfo, APIBackendTranslations, APIFormInfosJob, \
    APIFormInfosCredentials, APIFormInfosRepositories, APIFormInfosConfig, APIFormInfosGlobalAlerts, \
    APIFormInfosGroupAlerts, APIFormInfosUserAlerts, APIFormInfosPermissions
from aw.api_endpoints.stats import APIStatsJobs
# from aw.api_endpoints.base import not_implemented

urlpatterns_api = [
    path('api/key/<str:token>', APIKeyItem.as_view()),
    path('api/key', APIKey.as_view()),
    path('api/job/<int:job_id>/<int:exec_id>/log/<int:line_start>', APIJobExecutionLogs.as_view()),
    path('api/job/<int:job_id>/<int:exec_id>/log', APIJobExecutionLogFile.as_view()),
    path('api/job/<int:job_id>/<int:exec_id>', APIJobExecutionItem.as_view()),
    path('api/job/<int:job_id>', APIJobItem.as_view()),
    path('api/job_exec', APIJobExecution.as_view()),
    path('api/job_exec/<int:job_id>', APIJobExecutionSingleJob.as_view()),
    path('api/job', APIJob.as_view()),
    path('api/permission/<int:perm_id>', APIPermissionItem.as_view()),
    path('api/permission', APIPermission.as_view()),
    path('api/credentials/shared/<int:credentials_id>', APIJobSharedCredentialsItem.as_view()),
    path('api/credentials/shared', APIJobSharedCredentials.as_view()),
    path('api/credentials/user/<int:credentials_id>', APIJobUserCredentialsItem.as_view()),
    path('api/credentials/user', APIJobUserCredentials.as_view()),
    path('api/credentials/tmp', APIJobTMPCredentials.as_view()),
    path('api/credentials', APIJobCredentials.as_view()),
    path('api/repository/log/<int:repo_id>', APIRepositoryLogFile.as_view()),
    path('api/repository/<int:repo_id>', APIRepositoryItem.as_view()),
    path('api/repository', APIRepository.as_view()),
    path('api/alert', APIAlertAll.as_view()),
    path('api/alert/plugin/<int:plugin_id>', APIAlertPluginItem.as_view()),
    path('api/alert/plugin', APIAlertPlugin.as_view()),
    path('api/alert/global/<int:alert_id>', APIAlertGlobalItem.as_view()),
    path('api/alert/global', APIAlertGlobal.as_view()),
    path('api/alert/group/<int:alert_id>', APIAlertGroupItem.as_view()),
    path('api/alert/group', APIAlertGroup.as_view()),
    path('api/alert/user/<int:alert_id>', APIAlertUserItem.as_view()),
    path('api/alert/user', APIAlertUser.as_view()),
    path('api/config', APISystemConfig.as_view()),
    path('api/environment', APISystemEnvironment.as_view()),
    path('api/user/password', APIUserPasswordChange.as_view()),
    path('api/fs/browse/<str:repository>', APIFsBrowse.as_view()),
    path('api/fs/exists', APIFsExists.as_view()),
    path('api/_schema/', SpectacularAPIView.as_view(), name='_schema'),
    path('api/_docs', SpectacularSwaggerView.as_view(url_name='_schema'), name='swagger-ui'),
    path('api/frontend/info', APIBackendInfo.as_view()),
    path('api/frontend/lang', APIBackendTranslations.as_view()),
    path('api/frontend/form/job', APIFormInfosJob.as_view()),
    path('api/frontend/form/credentials', APIFormInfosCredentials.as_view()),
    path('api/frontend/form/repository', APIFormInfosRepositories.as_view()),
    path('api/frontend/form/config', APIFormInfosConfig.as_view()),
    path('api/frontend/form/alert/global', APIFormInfosGlobalAlerts.as_view()),
    path('api/frontend/form/alert/group', APIFormInfosGroupAlerts.as_view()),
    path('api/frontend/form/alert/user', APIFormInfosUserAlerts.as_view()),
    path('api/frontend/form/permission', APIFormInfosPermissions.as_view()),
    path('api/stats/jobs', APIStatsJobs.as_view()),
]
