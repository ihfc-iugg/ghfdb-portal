# Generated by Django 3.2.12 on 2022-02-11 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='continent',
            name='objectid',
        ),
        migrations.RemoveField(
            model_name='political',
            name='area_km2',
        ),
        migrations.RemoveField(
            model_name='political',
            name='iso_sovereign',
        ),
        migrations.RemoveField(
            model_name='political',
            name='iso_territory',
        ),
        migrations.RemoveField(
            model_name='political',
            name='sovereign',
        ),
        migrations.RemoveField(
            model_name='political',
            name='territory',
        ),
        migrations.RemoveField(
            model_name='political',
            name='un_sovereign',
        ),
        migrations.RemoveField(
            model_name='political',
            name='un_territory',
        ),
        migrations.AddField(
            model_name='political',
            name='changes',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='political',
            name='iso',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='continent',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='political',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='political',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]