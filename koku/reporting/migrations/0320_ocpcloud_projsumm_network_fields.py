# Generated by Django 4.2.11 on 2024-05-04 00:45
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reporting", "0319_node_network_costs"),
    ]

    operations = [
        migrations.AddField(
            model_name="ocpawscostlineitemprojectdailysummaryp",
            name="data_transfer_direction",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="ocpawscostlineitemprojectdailysummaryp",
            name="infrastructure_data_in_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
        migrations.AddField(
            model_name="ocpawscostlineitemprojectdailysummaryp",
            name="infrastructure_data_out_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
        migrations.AddField(
            model_name="ocpazurecostlineitemprojectdailysummaryp",
            name="data_transfer_direction",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="ocpazurecostlineitemprojectdailysummaryp",
            name="infrastructure_data_in_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
        migrations.AddField(
            model_name="ocpazurecostlineitemprojectdailysummaryp",
            name="infrastructure_data_out_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
        migrations.AddField(
            model_name="ocpgcpcostlineitemprojectdailysummaryp",
            name="data_transfer_direction",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="ocpgcpcostlineitemprojectdailysummaryp",
            name="infrastructure_data_in_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
        migrations.AddField(
            model_name="ocpgcpcostlineitemprojectdailysummaryp",
            name="infrastructure_data_out_gigabytes",
            field=models.DecimalField(decimal_places=15, max_digits=33, null=True),
        ),
    ]
