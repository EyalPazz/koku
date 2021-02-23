# Generated by Django 3.1.6 on 2021-02-18 22:34
from django.db import migrations

from koku.database import install_migrations_dbfunc


def reapply_app_needs_migrations_func(apps, schema_editor):
    conn = schema_editor.connection
    install_migrations_dbfunc(conn)


class Migration(migrations.Migration):

    dependencies = [("api", "0035_reapply_partition_and_clone_func")]

    operations = [migrations.RunPython(code=reapply_app_needs_migrations_func)]