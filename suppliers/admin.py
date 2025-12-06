from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
  list_display = ("name", "supplier_type", "contact_email", "updated_at")
  search_fields = ("name",)
  list_filter = ("supplier_type",)
