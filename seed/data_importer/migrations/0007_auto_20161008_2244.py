# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-09 05:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_importer', '0006_auto_20161007_0317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importfile',
            name='cycle',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, to='seed.Cycle'),
        ),
    ]
