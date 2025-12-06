from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class DueBillRequest(TimeStampedModel):
  class Status(models.TextChoices):
    OPEN = ("open", "Open")
    IN_PROGRESS = ("in_progress", "In progress")
    FULFILLED = ("fulfilled", "Fulfilled")
    CANCELLED = ("cancelled", "Cancelled")

  customer_name = models.CharField(max_length=128, blank=True)
  customer_number = models.CharField(max_length=64, blank=True)
  vin = models.CharField(max_length=64, blank=True)
  stock_number = models.CharField(max_length=64, blank=True)
  sales_consultant_name = models.CharField(max_length=128, blank=True)
  vehicle_info = models.CharField(max_length=128, blank=True)
  promised_date = models.DateField(null=True, blank=True)
  status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
  requested_by = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="due_bills_requested"
  )
  assigned_to = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="due_bills_assigned"
  )
  notes = models.TextField(blank=True)
  sent_to_parts_at = models.DateTimeField(null=True, blank=True)

  def __str__(self) -> str:
    return f"Due Bill {self.id} - {self.customer_name}"


class DueBillItem(TimeStampedModel):
  class Status(models.TextChoices):
    PENDING = ("pending", "Pending")
    ORDERED = ("ordered", "Ordered")
    RECEIVED = ("received", "Received")
    INSTALLED = ("installed", "Installed")
    CANCELLED = ("cancelled", "Cancelled")

  request = models.ForeignKey(DueBillRequest, on_delete=models.CASCADE, related_name="items")
  description = models.CharField(max_length=255)
  part_number = models.CharField(max_length=128, blank=True)
  status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)

  def __str__(self) -> str:
    return f"{self.description} ({self.status})"


class DueBillComment(TimeStampedModel):
  request = models.ForeignKey(DueBillRequest, on_delete=models.CASCADE, related_name="comments")
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
  body = models.TextField()

  def __str__(self) -> str:
    return f"Comment by {self.author} on {self.request}"
