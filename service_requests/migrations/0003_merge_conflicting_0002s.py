from django.db import migrations


class Migration(migrations.Migration):

  dependencies = [
    ("service_requests", "0002_add_ordered_and_received_dates"),
    ("service_requests", "0002_servicerequest_part_and_customer_fields"),
  ]

  operations = []
