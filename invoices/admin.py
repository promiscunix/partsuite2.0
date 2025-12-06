from django.contrib import admin

from .models import Invoice, InvoiceFile, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
  model = InvoiceLine
  extra = 0


class InvoiceFileInline(admin.TabularInline):
  model = InvoiceFile
  extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
  list_display = ("invoice_number", "supplier", "invoice_date", "total_amount", "status", "billed_flag", "received_flag")
  list_filter = ("supplier", "status", "billed_flag", "received_flag")
  search_fields = ("invoice_number", "supplier__name")
  inlines = [InvoiceLineInline, InvoiceFileInline]


@admin.register(InvoiceFile)
class InvoiceFileAdmin(admin.ModelAdmin):
  list_display = ("invoice", "file_kind", "file_path", "updated_at")


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
  list_display = ("invoice", "part_number", "quantity", "unit_price", "refund_status")
  list_filter = ("refund_status",)
  search_fields = ("part_number", "invoice__invoice_number")
