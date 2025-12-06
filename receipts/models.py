from django.db import models
from django.conf import settings

from common.models import TimeStampedModel
from invoices.models import InvoiceLine


class ReceiptUpload(TimeStampedModel):
  class Source(models.TextChoices):
    CSV = ("csv", "CSV")
    MANUAL = ("manual", "Manual")

  uploaded_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="receipt_uploads",
  )
  source = models.CharField(max_length=32, choices=Source.choices, default=Source.CSV)
  filename = models.CharField(max_length=255, blank=True)
  processed_at = models.DateTimeField(null=True, blank=True)
  notes = models.TextField(blank=True)

  def __str__(self) -> str:
    return self.filename or f"Upload {self.id}"


class ReceiptLine(TimeStampedModel):
  upload = models.ForeignKey(ReceiptUpload, on_delete=models.CASCADE, related_name="lines")
  part_number = models.CharField(max_length=128)
  quantity_received = models.IntegerField(default=0)
  invoice_line = models.ForeignKey(InvoiceLine, on_delete=models.SET_NULL, null=True, blank=True, related_name="receipt_lines")

  def __str__(self) -> str:
    return f"{self.part_number} x{self.quantity_received}"
