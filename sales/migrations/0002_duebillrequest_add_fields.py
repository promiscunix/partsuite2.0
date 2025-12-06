from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="duebillrequest",
            name="customer_number",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="duebillrequest",
            name="sales_consultant_name",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="duebillrequest",
            name="sent_to_parts_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="duebillrequest",
            name="stock_number",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="duebillrequest",
            name="vin",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
