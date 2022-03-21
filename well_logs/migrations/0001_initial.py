# Generated by Django 3.2.12 on 2022-03-10 06:52

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('thermoglobe', '0001_initial'),
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rock_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='rock type')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='sample name')),
                ('length', models.FloatField(blank=True, null=True, verbose_name='length (cm)')),
                ('width', models.FloatField(blank=True, null=True, verbose_name='width (cm)')),
                ('diameter', models.FloatField(blank=True, null=True, verbose_name='diameter (cm)')),
                ('thickness', models.FloatField(blank=True, null=True, verbose_name='thickness (cm)')),
            ],
        ),
        migrations.CreateModel(
            name='TemperatureLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('formation', models.CharField(blank=True, max_length=200, null=True, verbose_name='geological formation')),
                ('method', models.CharField(blank=True, max_length=200, null=True, verbose_name='method')),
                ('operator', models.CharField(blank=True, help_text='The operator collecting the measurements', max_length=150, null=True, verbose_name='operator')),
                ('source', models.CharField(blank=True, help_text='Where the data came from', max_length=50, null=True, verbose_name='original source')),
                ('source_id', models.CharField(blank=True, help_text='ID from data source', max_length=64, null=True, verbose_name='original source ID')),
                ('year_logged', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2050)], verbose_name='year')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comments')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='added')),
                ('circ_time', models.FloatField(blank=True, null=True, verbose_name='circulation time (hrs)')),
                ('lag_time', models.FloatField(blank=True, null=True, verbose_name='lag time (hrs)')),
                ('correction', models.CharField(blank=True, max_length=150, null=True, verbose_name='correction type')),
                ('reference', models.ForeignKey(blank=True, help_text='The publications or other reference from which the measurement was reported.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='temperature', to='publications.Publication', verbose_name='reference')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='temperature', to='thermoglobe.site', verbose_name='site')),
            ],
            options={
                'verbose_name': 'temperature',
                'verbose_name_plural': 'temperature',
                'db_table': 'temp_meta',
                'ordering': ['added'],
                'default_related_name': 'temperature',
            },
        ),
        migrations.CreateModel(
            name='Temperature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(verbose_name='value')),
                ('uncertainty', models.FloatField(blank=True, null=True, verbose_name='uncertainty')),
                ('depth', models.FloatField(verbose_name='depth (m)')),
                ('log', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data', to='well_logs.temperaturelog', verbose_name='log')),
            ],
            options={
                'verbose_name': 'temperature data',
                'verbose_name_plural': 'temperature data',
                'db_table': 'temperature',
            },
        ),
        migrations.CreateModel(
            name='HeatProductionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('formation', models.CharField(blank=True, max_length=200, null=True, verbose_name='geological formation')),
                ('method', models.CharField(blank=True, max_length=200, null=True, verbose_name='method')),
                ('operator', models.CharField(blank=True, help_text='The operator collecting the measurements', max_length=150, null=True, verbose_name='operator')),
                ('source', models.CharField(blank=True, help_text='Where the data came from', max_length=50, null=True, verbose_name='original source')),
                ('source_id', models.CharField(blank=True, help_text='ID from data source', max_length=64, null=True, verbose_name='original source ID')),
                ('year_logged', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2050)], verbose_name='year')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comments')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='added')),
                ('reference', models.ForeignKey(blank=True, help_text='The publications or other reference from which the measurement was reported.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='heat_production', to='publications.Publication', verbose_name='reference')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='heat_production', to='thermoglobe.site', verbose_name='site')),
            ],
            options={
                'verbose_name': 'heat production',
                'verbose_name_plural': 'heat production',
                'db_table': 'heat_production_log',
                'default_related_name': 'heat_production',
            },
        ),
        migrations.CreateModel(
            name='HeatProduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(verbose_name='value')),
                ('uncertainty', models.FloatField(blank=True, null=True, verbose_name='uncertainty')),
                ('depth', models.FloatField(verbose_name='depth (m)')),
                ('rock_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='rock type')),
                ('k_pc', models.FloatField(blank=True, null=True, verbose_name='K (wt%)')),
                ('th_ppm', models.FloatField(blank=True, null=True, verbose_name='Th (ppm)')),
                ('u_ppm', models.FloatField(blank=True, null=True, verbose_name='U (ppm)')),
                ('log', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data', to='well_logs.heatproductionlog', verbose_name='log')),
            ],
            options={
                'db_table': 'heat_production',
            },
        ),
        migrations.CreateModel(
            name='ConductivityLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('formation', models.CharField(blank=True, max_length=200, null=True, verbose_name='geological formation')),
                ('method', models.CharField(blank=True, max_length=200, null=True, verbose_name='method')),
                ('operator', models.CharField(blank=True, help_text='The operator collecting the measurements', max_length=150, null=True, verbose_name='operator')),
                ('source', models.CharField(blank=True, help_text='Where the data came from', max_length=50, null=True, verbose_name='original source')),
                ('source_id', models.CharField(blank=True, help_text='ID from data source', max_length=64, null=True, verbose_name='original source ID')),
                ('year_logged', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2050)], verbose_name='year')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comments')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='added')),
                ('reference', models.ForeignKey(blank=True, help_text='The publications or other reference from which the measurement was reported.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conductivity', to='publications.Publication', verbose_name='reference')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conductivity', to='thermoglobe.site', verbose_name='site')),
            ],
            options={
                'verbose_name': 'thermal conductivity',
                'verbose_name_plural': 'thermal conductivity',
                'db_table': 'thermal_conductivity_log',
                'default_related_name': 'conductivity',
            },
        ),
        migrations.CreateModel(
            name='Conductivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(verbose_name='value')),
                ('uncertainty', models.FloatField(blank=True, null=True, verbose_name='uncertainty')),
                ('depth', models.FloatField(verbose_name='depth (m)')),
                ('orientation', models.FloatField(blank=True, help_text='Angle relative to the foliation/bedding where 0 is parallel and 90 is perpendicular', null=True, validators=[django.core.validators.MaxValueValidator(90), django.core.validators.MinValueValidator(0)], verbose_name='orientation')),
                ('log', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data', to='well_logs.conductivitylog', verbose_name='log')),
                ('sample', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='well_logs.sample')),
            ],
            options={
                'db_table': 'thermal_conductivity',
                'ordering': ['depth'],
                'unique_together': {('value', 'sample', 'log')},
            },
        ),
    ]