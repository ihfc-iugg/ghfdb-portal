# Generated by Django 3.1.3 on 2020-12-14 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0011_margin_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sea',
            name='area',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='max_x',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='max_y',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='min_x',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='min_y',
        ),
        migrations.RemoveField(
            model_name='sea',
            name='mrgid',
        ),
    ]