# Generated by Django 2.2.13 on 2021-02-16 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0016_organization_taxlot_display_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='new_user_email_content',
            field=models.CharField(default="Hello {{first_name}},\nYou're receiving this e-mail because you've been registered for a SEED account.\nSEED is easy, flexible, and cost effective software designed to help organizations clean, manage and share information about large portfolios of buildings. SEED is a free, open source web application that you can use privately.  While SEED was originally designed to help cities and States implement benchmarking programs for public or private buildings, it has the potential to be useful for many other activities by public entities, efficiency programs and private companies.\nPlease go to the following page and setup your account:\n{{sign_up_link}}", max_length=1024),
        ),
        migrations.AddField(
            model_name='organization',
            name='new_user_email_from',
            field=models.CharField(default='info@seed-platform.org', max_length=128),
        ),
        migrations.AddField(
            model_name='organization',
            name='new_user_email_signature',
            field=models.CharField(default='The SEED Team', max_length=128),
        ),
        migrations.AddField(
            model_name='organization',
            name='new_user_email_subject',
            field=models.CharField(default='New SEED account', max_length=128),
        ),
    ]
