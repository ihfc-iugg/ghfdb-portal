# Generated by Django 3.1.3 on 2020-12-03 08:49

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0011_margin_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('thermoglobe', '0029_auto_20201201_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpublication',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
        migrations.AlterField(
            model_name='site',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='site description'),
        ),
        migrations.AlterField(
            model_name='site',
            name='seafloor_age',
            field=models.FloatField(blank=True, help_text='Total depth of the hole in metres.', null=True, validators=[django.core.validators.MaxValueValidator(220), django.core.validators.MinValueValidator(0)], verbose_name='well depth'),
        ),
        migrations.CreateModel(
            name='HistoricalSite',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('site_name', models.CharField(help_text='The name given to the site.', max_length=200, verbose_name='site name')),
                ('latitude', models.FloatField(db_index=True, help_text='Latitude in decimal degrees. WGS84 preferred but not enforced.', validators=[django.core.validators.MaxValueValidator(90), django.core.validators.MinValueValidator(-90)], verbose_name='latitude')),
                ('longitude', models.FloatField(db_index=True, help_text='Longitude in decimal degrees. WGS84 preferred but not enforced.', validators=[django.core.validators.MaxValueValidator(180), django.core.validators.MinValueValidator(-180)], verbose_name='longitude')),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, srid=4326)),
                ('elevation', models.FloatField(blank=True, help_text='Site elevation', null=True, verbose_name='elevation')),
                ('well_depth', models.FloatField(blank=True, help_text='Total depth of the hole in metres.', null=True, validators=[django.core.validators.MaxValueValidator(12500), django.core.validators.MinValueValidator(0)], verbose_name='well depth')),
                ('cruise', models.CharField(blank=True, help_text='For oceanic measurements - the name of the cruise on which the measurements were taken.', max_length=150, null=True, verbose_name='name of cruise')),
                ('seafloor_age', models.FloatField(blank=True, help_text='Total depth of the hole in metres.', null=True, validators=[django.core.validators.MaxValueValidator(220), django.core.validators.MinValueValidator(0)], verbose_name='well depth')),
                ('sediment_thickness', models.FloatField(blank=True, help_text='Sediment thickness at the site.', null=True, verbose_name='calculated sediment thickness')),
                ('sediment_thickness_type', models.CharField(blank=True, help_text='How sediment thickness was determined.', max_length=250, null=True, verbose_name='type of sediment thickness')),
                ('seamount_distance', models.FloatField(blank=True, help_text='Distance in Km to the nearest seamount.', null=True, verbose_name='distance to seamount')),
                ('outcrop_distance', models.FloatField(blank=True, help_text='Distance in Km to the nearest outcrop.', null=True, verbose_name='distance to outcrop')),
                ('crustal_thickness', models.FloatField(blank=True, help_text='Calculated crustal thickness at the site.', null=True, verbose_name='calculated crustal thickness')),
                ('year_drilled', models.IntegerField(blank=True, null=True, verbose_name='year drilled')),
                ('description', models.TextField(blank=True, null=True, verbose_name='site description')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from=['site_name', 'latitude', 'longitude'])),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('basin', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.basin', verbose_name='basin')),
                ('bottom_water_temp', models.ForeignKey(blank=True, db_constraint=False, help_text='Temperature at the bottom of the water column.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='thermoglobe.temperature', verbose_name='bottom water temperature')),
                ('continent', models.ForeignKey(blank=True, db_constraint=False, help_text='As calculated using the <a href="https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351d">ESRI World Continents shapefile</a>.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.continent', verbose_name='continent')),
                ('country', models.ForeignKey(blank=True, db_constraint=False, help_text='As calculated using the <a href="http://www.mappinghacks.com/data/">World Borders shapefile</a>.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.country', verbose_name='country')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('political', models.ForeignKey(blank=True, db_constraint=False, help_text='As calculated using the Flanders Marine Institute (2018)<a href="http://www.marineregions.org/">Marine and Land Zones</a>. DOI: <a href="https://doi.org/10.14284/403">10.14284/403</a>', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.political', verbose_name='political region')),
                ('province', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.province', verbose_name='geological province')),
                ('sea', models.ForeignKey(blank=True, db_constraint=False, help_text='As calculated using the Flanders Marine Institute (2018)<a href="http://www.marineregions.org/">Oceans and Seas shapefile</a>. DOI: <a href="https://doi.org/10.14284/323">10.14284/323</a>', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mapping.sea', verbose_name='sea/ocean')),
                ('surface_temp', models.ForeignKey(blank=True, db_constraint=False, help_text='Temperature at the surface. Can be either a top of hole temperature or bottom of water temperature for oceanic measurements', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='thermoglobe.temperature', verbose_name='surface temperature')),
            ],
            options={
                'verbose_name': 'historical site',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]