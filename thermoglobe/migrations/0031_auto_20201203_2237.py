# Generated by Django 3.1.3 on 2020-12-03 12:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thermoglobe', '0030_auto_20201203_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsite',
            name='seafloor_age',
            field=models.FloatField(blank=True, help_text='Age of the sea floor', null=True, validators=[django.core.validators.MaxValueValidator(220), django.core.validators.MinValueValidator(0)], verbose_name='sea floor age'),
        ),
        migrations.AlterField(
            model_name='site',
            name='seafloor_age',
            field=models.FloatField(blank=True, help_text='Age of the sea floor', null=True, validators=[django.core.validators.MaxValueValidator(220), django.core.validators.MinValueValidator(0)], verbose_name='sea floor age'),
        ),
    ]