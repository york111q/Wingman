# Generated by Django 3.2.2 on 2021-06-08 14:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_auto_20210528_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='pools',
            name='pool_skipped',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=32), default=list, size=None),
        ),
    ]
