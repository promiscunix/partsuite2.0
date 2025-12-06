from django.db import models
from django.conf import settings

from common.models import TimeStampedModel
from suppliers.models import Supplier


class Invoice(TimeStampedModel):
  class Status(models.TextChoices):
    PARSED = ("parsed", "Parsed")
    NEEDS_REVIEW = ("needs_review", "Needs review")
    READY = ("ready", "Ready")

  supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="invoices")
  invoice_number = models.CharField(max_length=128)
  invoice_date = models.DateField(null=True, blank=True)
  total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  billed_flag = models.BooleanField(default=False)
  received_flag = models.BooleanField(default=False)
  status = models.CharField(max_length=32, choices=Status.choices, default=Status.PARSED)
  uploaded_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="uploaded_invoices",
  )
  notes = models.TextField(blank=True)

  class Meta:
    unique_together = ("supplier", "invoice_number")
    ordering = ["-invoice_date", "-created_at"]

  def __str__(self) -> str:
    return f"{self.supplier.name} - {self.invoice_number}"


class InvoiceFile(TimeStampedModel):
  class FileKind(models.TextChoices):
    RAW = ("raw", "Raw")
    SUMMARY = ("summary", "Summary")
    GL_CODING = ("gl_coding", "GL Coding")

  invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="files")
  file_path = models.CharField(max_length=512)
  file_kind = models.CharField(max_length=32, choices=FileKind.choices, default=FileKind.RAW)
  description = models.CharField(max_length=255, blank=True)
  text_cache = models.JSONField(default=list, blank=True)

  def __str__(self) -> str:
    return f"{self.invoice} ({self.file_kind})"


class InvoiceLine(TimeStampedModel):
  class RefundStatus(models.TextChoices):
    NONE = ("none", "None")
    WAITING = ("waiting", "Waiting on refund")
    REFUNDED = ("refunded", "Refunded")

  invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
  part_number = models.CharField(max_length=128)
  description = models.CharField(max_length=255, blank=True)
  quantity = models.IntegerField(default=1)
  unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  received_quantity = models.IntegerField(default=0)
  refund_status = models.CharField(max_length=32, choices=RefundStatus.choices, default=RefundStatus.NONE)

  class Meta:
    ordering = ["part_number"]

  @property
  def extended_price(self):
    return self.quantity * self.unit_price

  def __str__(self) -> str:
    return f"{self.part_number} x{self.quantity}"
