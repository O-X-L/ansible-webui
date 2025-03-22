from django.db import models
from django.core.exceptions import FieldDoesNotExist

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)
DEFAULT_NONE = {'null': True, 'default': None, 'blank': True}
JOB_EXEC_STATUS_WAIT = 0
JOB_EXEC_STATUS_START = 1
JOB_EXEC_STATUS_RUN = 2
JOB_EXEC_STATUS_FAILED = 3
JOB_EXEC_STATUS_SUCCESS = 4
JOB_EXEC_STATUS_STOPPING = 5
JOB_EXEC_STATUS_STOPPED = 6
JOB_EXEC_STATUS_RETRY = 7
CHOICES_JOB_EXEC_STATUS = [
    (JOB_EXEC_STATUS_WAIT, 'Waiting'),
    (JOB_EXEC_STATUS_START, 'Starting'),
    (JOB_EXEC_STATUS_RUN, 'Running'),
    (JOB_EXEC_STATUS_FAILED, 'Failed'),
    (JOB_EXEC_STATUS_SUCCESS, 'Finished'),
    (JOB_EXEC_STATUS_STOPPING, 'Stopping'),
    (JOB_EXEC_STATUS_STOPPED, 'Stopped'),
    (JOB_EXEC_STATUS_RETRY, 'Retry'),
]
JOB_EXEC_STATI_ACTIVE = [
    JOB_EXEC_STATUS_WAIT,
    JOB_EXEC_STATUS_START,
    JOB_EXEC_STATUS_RUN,
    JOB_EXEC_STATUS_STOPPING,
    JOB_EXEC_STATUS_RETRY,
]
JOB_EXEC_STATI_INACTIVE = [
    JOB_EXEC_STATUS_SUCCESS,
    JOB_EXEC_STATUS_FAILED,
    JOB_EXEC_STATUS_STOPPED,
]


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_model_field_default(m, field: str):
    try:
        field = m._meta.get_field(field)
        return field.default if field.default is not models.fields.NOT_PROVIDED else None

    except FieldDoesNotExist:
        return None


def get_model_field_choices(m, field: str):
    try:
        field = m._meta.get_field(field)
        return field.choices if field.choices else None

    except FieldDoesNotExist:
        return None
