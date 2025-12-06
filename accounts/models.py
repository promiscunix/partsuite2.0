from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
  class Role(models.TextChoices):
    ADMIN = ("admin", "Admin")
    PARTS = ("parts", "Parts")
    SERVICE = ("service", "Service")
    SALES = ("sales", "Sales")
    ACCOUNTING = ("accounting", "Accounting")

  role = models.CharField(max_length=32, choices=Role.choices, default=Role.PARTS)
  department = models.CharField(max_length=64, blank=True)

  def __str__(self) -> str:
    return f"{self.username} ({self.role})"
