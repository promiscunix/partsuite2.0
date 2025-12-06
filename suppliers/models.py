from django.db import models

from common.models import TimeStampedModel


class Supplier(TimeStampedModel):
  class SupplierType(models.TextChoices):
    MOPAR = ("mopar", "Mopar")
    AFTERMARKET = ("aftermarket", "Aftermarket")
    OTHER = ("other", "Other")

  name = models.CharField(max_length=255, unique=True)
  supplier_type = models.CharField(max_length=32, choices=SupplierType.choices, default=SupplierType.MOPAR)
  contact_email = models.EmailField(blank=True)
  default_terms = models.CharField(max_length=64, blank=True)

  def __str__(self) -> str:
    return self.name
