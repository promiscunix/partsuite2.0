from datetime import timedelta

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class ServiceRequest(TimeStampedModel):
  class RequestType(models.TextChoices):
    RADIO = ("radio", "Radio")
    VOR = ("vor", "VOR")

  class WarrantyType(models.TextChoices):
    MOPAR_WARRANTY = ("mopar_warranty", "Mopar Warranty")
    CUSTOMER_PAY = ("customer_pay", "Customer Pay")
    REGULAR_WARRANTY = ("regular_warranty", "Regular Warranty")
    GOOD_WILL = ("good_will", "Good Will")

  class Status(models.TextChoices):
    OPEN = ("open", "Open")
    IN_PROGRESS = ("in_progress", "In progress")
    DONE = ("done", "Done")
    CANCELLED = ("cancelled", "Cancelled")

  request_type = models.CharField(max_length=32, choices=RequestType.choices)
  part_number = models.CharField(max_length=64, blank=True)
  vin = models.CharField(max_length=32, blank=True)
  ro_number = models.CharField(max_length=64, blank=True)
  customer_name = models.CharField(max_length=128, blank=True)
  customer_number = models.CharField(max_length=64, blank=True)
  warranty_type = models.CharField(
    max_length=32, choices=WarrantyType.choices, default=WarrantyType.MOPAR_WARRANTY
  )
  ordered_date = models.DateField(null=True, blank=True)
  received_date = models.DateField(null=True, blank=True)
  expiry_date = models.DateField(null=True, blank=True)
  status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_requests_created"
  )
  assigned_to = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_requests_assigned"
  )
  notes = models.TextField(blank=True)

  def __str__(self) -> str:
    return f"{self.get_request_type_display()} ({self.vin or 'no VIN'})"

  def save(self, *args, **kwargs):
    if self.received_date:
      self.expiry_date = self.received_date + timedelta(days=30)
    super().save(*args, **kwargs)


class ServiceRequestComment(TimeStampedModel):
  request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="comments")
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
  body = models.TextField()

  def __str__(self) -> str:
    return f"Comment by {self.author} on {self.request}"
