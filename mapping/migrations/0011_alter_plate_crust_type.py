# Generated by Django 3.2.12 on 2022-02-17 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0010_auto_20220217_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plate',
            name='crust_type',
            field=models.CharField(choices=[('continental', 'continental'), ('oceanic', 'oceanic')], max_length=12),
        ),
    ]