# Generated by Django 3.2.15 on 2022-09-28 14:49
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reporting", "0258_aws_azure_daily_summ_idxs"),
    ]

    operations = [
        migrations.AddField(
            model_name="ocpnode",
            name="node_role",
            field=models.TextField(null=True),
        ),
    ]