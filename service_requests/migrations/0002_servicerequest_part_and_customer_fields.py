from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ("service_requests", "0001_initial"),
  ]

  operations = [
    migrations.AddField(
      model_name="servicerequest",
      name="customer_number",
      field=models.CharField(blank=True, max_length=64),
    ),
    migrations.AddField(
      model_name="servicerequest",
      name="part_number",
      field=models.CharField(blank=True, max_length=64),
    ),
    migrations.AddField(
      model_name="servicerequest",
      name="warranty_type",
      field=models.CharField(
        choices=[
          ("mopar_warranty", "Mopar Warranty"),
          ("basic_warranty", "Basic Warranty"),
          ("customer_pay", "Customer Pay"),
          ("service_contract", "Service Contract"),
        ],
        default="mopar_warranty",
        max_length=32,
      ),
    ),
  ]
