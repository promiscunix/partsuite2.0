from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ("service_requests", "0001_initial"),
  ]

  operations = [
    migrations.RenameField(
      model_name="servicerequest",
      old_name="promised_date",
      new_name="received_date",
    ),
    migrations.AddField(
      model_name="servicerequest",
      name="ordered_date",
      field=models.DateField(blank=True, null=True),
    ),
  ]
