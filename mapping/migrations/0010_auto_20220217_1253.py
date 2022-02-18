# Generated by Django 3.2.12 on 2022-02-17 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0009_auto_20220217_1240'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plate',
            old_name='plate_type',
            new_name='type',
        ),
        migrations.AlterField(
            model_name='plate',
            name='crust_type',
            field=models.CharField(choices=[('c', 'continental'), ('o', 'oceanic')], max_length=2),
        ),
    ]