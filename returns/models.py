from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from invoices.models import InvoiceLine


class ReturnRequest(TimeStampedModel):
  class Status(models.TextChoices):
    WAITING = ("waiting_refund", "Waiting on refund")
    REFUNDED = ("refunded", "Refunded")
    DENIED = ("denied", "Denied")

  invoice_line = models.ForeignKey(InvoiceLine, on_delete=models.CASCADE, related_name="return_requests")
  status = models.CharField(max_length=32, choices=Status.choices, default=Status.WAITING)
  reason = models.TextField(blank=True)
  rma_number = models.CharField(max_length=128, blank=True)
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="return_requests"
  )
  refund_received_at = models.DateField(null=True, blank=True)

  def __str__(self) -> str:
    return f"Return {self.id} for {self.invoice_line}"
