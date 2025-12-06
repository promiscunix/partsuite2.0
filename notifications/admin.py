from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
  list_display = ("id", "type", "target_email", "status", "send_on", "sent_at")
  list_filter = ("type", "status")
  search_fields = ("target_email", "subject")
