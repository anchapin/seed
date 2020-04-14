# Generated by Django 2.2.10 on 2020-04-13 23:03

from django.db import migrations, models

def forwards(apps, schema_editor):
    Rule = apps.get_model('seed', 'Rule')
    rule = Rule.objects.exclude(id=None)

    # r_condition = []
    for r in rule.values():
        if r['min'] is None and r['max'] is None:
            if r['required']: r['condition'] = 'required'
            else: r['condition'] = 'not_null'
        else:
            if r['data_type'] == 1: r['condition'] = 'range'
            else: r['condition'] = 'include'

        # if (r['condition'] != ''): r_condition.append(r['condition'])

    # print('\nAll rules included? ', len(r_condition) == Rule.objects.count())


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0122_auto_20200303_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='condition',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='rule',
            name='placeholder',
            field=models.CharField(default='(field must contain this text)', max_length=200),
        ),
        migrations.RunPython(forwards)
    ]
