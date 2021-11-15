# Generated by Django 3.1.13 on 2021-11-15 14:26
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("api", "0050_exchangerates"), ("reporting", "0205_ocpall_perspective_db_defaults")]

    operations = [
        migrations.AlterField(
            model_name="ocpallcomputesummarypt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallcostsummarybyaccountpt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallcostsummarybyregionpt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallcostsummarybyservicept",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallcostsummarypt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpalldatabasesummarypt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallnetworksummarypt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
        migrations.AlterField(
            model_name="ocpallstoragesummarypt",
            name="source_uuid",
            field=models.ForeignKey(
                db_column="source_uuid", null=True, on_delete=django.db.models.deletion.CASCADE, to="api.provider"
            ),
        ),
    ]
