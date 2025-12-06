from django.contrib import admin

from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
  list_display = ("id", "invoice_line", "status", "rma_number", "refund_received_at", "created_at")
  list_filter = ("status",)
  search_fields = ("invoice_line__part_number", "rma_number")
