# Generated by Django 3.2.12 on 2022-02-17 02:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0008_auto_20220212_1710'),
    ]

    operations = [
        migrations.RenameField(
            model_name='province',
            old_name='crust_type',
            new_name='crust',
        ),
        migrations.RemoveField(
            model_name='province',
            name='reference',
        ),
        migrations.RemoveField(
            model_name='plate',
            name='references',
        ),
    ]