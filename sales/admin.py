from django.contrib import admin

from .models import DueBillRequest, DueBillItem, DueBillComment


class DueBillItemInline(admin.TabularInline):
  model = DueBillItem
  extra = 0


class DueBillCommentInline(admin.TabularInline):
  model = DueBillComment
  extra = 0


@admin.register(DueBillRequest)
class DueBillRequestAdmin(admin.ModelAdmin):
  list_display = (
    "id",
    "customer_name",
    "customer_number",
    "vin",
    "stock_number",
    "status",
    "promised_date",
    "sent_to_parts_at",
  )
  list_filter = ("status", "sent_to_parts_at")
  search_fields = (
    "customer_name",
    "customer_number",
    "vin",
    "stock_number",
    "vehicle_info",
    "sales_consultant_name",
  )
  inlines = [DueBillItemInline, DueBillCommentInline]


@admin.register(DueBillItem)
class DueBillItemAdmin(admin.ModelAdmin):
  list_display = ("request", "description", "part_number", "status")
  list_filter = ("status",)
  search_fields = ("description", "part_number")


@admin.register(DueBillComment)
class DueBillCommentAdmin(admin.ModelAdmin):
  list_display = ("id", "request", "author", "created_at")
