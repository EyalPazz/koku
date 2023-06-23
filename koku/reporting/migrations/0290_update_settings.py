# Generated by Django 3.2.18 on 2023-05-22 20:38
from django.db import migrations


def update_settings(apps, schema_editor):
    UserSettings = apps.get_model("reporting", "UserSettings")
    if user_settings := UserSettings.objects.first():
        if user_settings.settings.get("cost_type") == "savingsplan_effective_cost":
            user_settings.settings["cost_type"] = "calculated_amortized_cost"
            user_settings.save()


def revert(apps, schema_editor):
    UserSettings = apps.get_model("reporting", "UserSettings")
    if user_settings := UserSettings.objects.first():
        if user_settings.settings.get("cost_type") == "calculated_amortized_cost":
            user_settings.settings["cost_type"] = "savingsplan_effective_cost"
            user_settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ("reporting", "0289_alter_awsorganizationalunit_provider"),
    ]

    operations = [
        migrations.RunPython(update_settings, reverse_code=revert),
    ]