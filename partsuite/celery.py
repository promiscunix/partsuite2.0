import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "partsuite.settings")

app = Celery("partsuite")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
