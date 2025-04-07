from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework_api_key.admin import APIKey

from aw.base import USERS
from aw.model.api import AwAPIKey
from aw.model.job import Job, JobExecution, JobExecutionResult, JobError, JobExecutionResultHost
from aw.model.permission import JobPermission, JobPermissionMemberUser, JobPermissionMemberGroup, \
    JobPermissionMapping, JobCredentialsPermissionMapping, JobRepositoryPermissionMapping
from aw.model.job_credential import JobSharedCredentials, JobUserCredentials
from aw.model.repository import Repository
from aw.model.system import SystemConfig, UserExtended
from aw.model.alert import AlertUser, AlertGroup, AlertGlobal, AlertPlugin


class UserExtendedInline(admin.StackedInline):
    model = UserExtended
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UserExtendedInline]


admin.site.unregister(APIKey)
admin.site.unregister(USERS)
admin.site.register(USERS, UserAdmin)

admin.site.register(Job)
admin.site.register(JobExecution)
admin.site.register(JobPermission)
admin.site.register(JobPermissionMemberUser)
admin.site.register(JobPermissionMemberGroup)
admin.site.register(JobPermissionMapping)
admin.site.register(JobCredentialsPermissionMapping)
admin.site.register(JobRepositoryPermissionMapping)
admin.site.register(JobExecutionResult)
admin.site.register(JobExecutionResultHost)
admin.site.register(JobError)
admin.site.register(JobSharedCredentials)
admin.site.register(JobUserCredentials)
admin.site.register(AwAPIKey)
admin.site.register(Repository)
admin.site.register(SystemConfig)
admin.site.register(AlertUser)
admin.site.register(AlertGroup)
admin.site.register(AlertGlobal)
admin.site.register(AlertPlugin)
