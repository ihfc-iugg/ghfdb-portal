# Generated by Django 3.1.1 on 2020-09-25 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0005_province'),
        ('thermoglobe', '0011_auto_20200925_1252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='CGG_basin',
        ),
        migrations.AddField(
            model_name='site',
            name='basin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='mapping.basin', verbose_name='basin'),
        ),
        migrations.AddField(
            model_name='site',
            name='province',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='mapping.province', verbose_name='geological province'),
        ),
    ]