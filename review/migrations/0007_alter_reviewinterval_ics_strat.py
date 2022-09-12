# Generated by Django 3.2.15 on 2022-08-23 11:16

from django.db import migrations
import django.db.models.deletion
import geologic_time.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geologic_time', '0009_auto_20220818_1253'),
        ('review', '0006_reviewinterval_ics_strat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewinterval',
            name='ics_strat',
            field=geologic_time.fields.GeologicTimeOneToOne(blank=True, help_text='Stratigraphic age of the depth range involved in the reported heat-flow determination based on the official geologic timescale of the International Commission on Stratigraphy.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review_intervals', to='geologic_time.geologictime', verbose_name='ICS stratigraphy'),
        ),
    ]