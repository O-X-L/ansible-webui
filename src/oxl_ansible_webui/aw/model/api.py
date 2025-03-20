from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

from aw.base import USERS
from aw.model.base import DEFAULT_NONE


class AwAPIKey(AbstractAPIKey):
    user = models.ForeignKey(USERS, on_delete=models.CASCADE, editable=False)
    comment = models.CharField(max_length=100, **DEFAULT_NONE)
