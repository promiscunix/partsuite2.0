from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ("service_requests", "0003_merge_conflicting_0002s"),
  ]

  operations = [
    migrations.AlterField(
      model_name="servicerequest",
      name="request_type",
      field=models.CharField(
        choices=[("radio", "Radio"), ("vor", "VOR")],
        max_length=32,
      ),
    ),
    migrations.AlterField(
      model_name="servicerequest",
      name="warranty_type",
      field=models.CharField(
        choices=[
          ("mopar_warranty", "Mopar Warranty"),
          ("customer_pay", "Customer Pay"),
          ("regular_warranty", "Regular Warranty"),
          ("good_will", "Good Will"),
        ],
        default="mopar_warranty",
        max_length=32,
      ),
    ),
  ]
