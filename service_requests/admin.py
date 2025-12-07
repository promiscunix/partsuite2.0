from django.contrib import admin

from .models import ServiceRequest, ServiceRequestComment


class ServiceRequestCommentInline(admin.TabularInline):
  model = ServiceRequestComment
  extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
  list_display = ("id", "request_type", "status", "vin", "ro_number", "received_date", "expiry_date")
  list_filter = ("request_type", "status")
  search_fields = ("vin", "ro_number", "customer_name")
  inlines = [ServiceRequestCommentInline]


@admin.register(ServiceRequestComment)
class ServiceRequestCommentAdmin(admin.ModelAdmin):
  list_display = ("id", "request", "author", "created_at")
