from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class AuditEvent(TimeStampedModel):
  actor = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events"
  )
  action = models.CharField(max_length=128)
  object_type = models.CharField(max_length=128, blank=True)
  object_id = models.CharField(max_length=64, blank=True)
  metadata = models.JSONField(default=dict, blank=True)

  def __str__(self) -> str:
    return f"{self.action} by {self.actor}"
