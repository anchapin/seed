# Generated by Django 2.2.20 on 2021-06-03 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0139_auto_20210524_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='columnlistprofile',
            name='derived_columns',
            field=models.ManyToManyField(related_name='column_list_profiles', to='seed.DerivedColumn'),
        ),
    ]
