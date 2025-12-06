from django.db import models

from common.models import TimeStampedModel


class Notification(TimeStampedModel):
  class Status(models.TextChoices):
    PENDING = ("pending", "Pending")
    SENT = ("sent", "Sent")
    FAILED = ("failed", "Failed")

  class Type(models.TextChoices):
    RADIO_EXPIRY = ("radio_expiry", "Radio expiry")
    INVOICE_MISMATCH = ("invoice_mismatch", "Invoice mismatch")
    RETURN_STATUS = ("return_status", "Return status")
    DUEBILL_STATUS = ("duebill_status", "Due bill status")

  type = models.CharField(max_length=64, choices=Type.choices)
  target_email = models.EmailField()
  subject = models.CharField(max_length=255, blank=True)
  body = models.TextField(blank=True)
  send_on = models.DateTimeField(null=True, blank=True)
  sent_at = models.DateTimeField(null=True, blank=True)
  status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
  payload = models.JSONField(default=dict, blank=True)

  def __str__(self) -> str:
    return f"{self.type} -> {self.target_email}"
