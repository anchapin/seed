# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-07 01:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0003_auto_20160412_1123'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='exportablefield',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='exportablefield',
            name='organization',
        ),
        migrations.DeleteModel(
            name='ExportableField',
        ),
    ]
