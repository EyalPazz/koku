# Generated by Django 4.2.11 on 2024-05-16 18:41
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reporting", "0323_remove_awscostentrylineitemsummarybyec2compute_availability_zone_and_org_unit"),
    ]

    operations = [
        migrations.AddField(
            model_name="ocppvc",
            name="csi_volume_handle",
            field=models.TextField(null=True),
        ),
    ]