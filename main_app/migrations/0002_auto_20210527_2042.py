# Generated by Django 3.2.2 on 2021-05-27 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pools',
            name='pool_KD1',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='pools',
            name='pool_KD2',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='pools',
            name='pool_r_rate',
            field=models.FloatField(default=0.0),
        ),
    ]
