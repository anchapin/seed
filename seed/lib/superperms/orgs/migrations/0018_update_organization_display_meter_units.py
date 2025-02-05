# Generated by Django 2.2.10 on 2020-03-27 19:13

from django.db import migrations


def update_display_meter_units_options(apps, schema_editor):
    Organization = apps.get_model('orgs', 'Organization')
    for org in Organization.objects.all():
        org.display_meter_units['Electric - Unknown'] = 'kWh (thousand Watt-hours)'
        org.save()


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0017_auto_20210218_1715'),
    ]

    operations = [
        migrations.RunPython(update_display_meter_units_options),
    ]
