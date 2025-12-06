from django.contrib import admin

from .models import ReceiptUpload, ReceiptLine


class ReceiptLineInline(admin.TabularInline):
  model = ReceiptLine
  extra = 0


@admin.register(ReceiptUpload)
class ReceiptUploadAdmin(admin.ModelAdmin):
  list_display = ("id", "filename", "source", "uploaded_by", "processed_at", "created_at")
  list_filter = ("source",)
  inlines = [ReceiptLineInline]


@admin.register(ReceiptLine)
class ReceiptLineAdmin(admin.ModelAdmin):
  list_display = ("upload", "part_number", "quantity_received", "invoice_line")
  search_fields = ("part_number",)
