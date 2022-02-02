from django.contrib.gis.db import models
from django.contrib.gis.utils import LayerMapping
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext as _
import os
from django.utils.html import mark_safe
from django.apps import apps
from thermoglobe.models import Site

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class GISManager(models.Manager):

    def load(self, data_dir, verbose=True, strict=True, transform=False):
        data_folder = os.path.join(DATA_DIR, data_dir)
        shp_file = [f for f in os.listdir(data_folder) if f.endswith('.shp')]
        if len(shp_file) == 1:
            lm = LayerMapping(self.model, 
            os.path.join(
                data_folder,
                shp_file[0]), 
                self.model.mapping, 
                transform=transform)
            lm.save(strict=strict, verbose=verbose)
        elif len(shp_file) > 1:
            raise ValueError('Multiple shapefiles found in directory')
        else:
            raise ValueError('No shapefiles found in directory')

class Base(models.Model):
    slug = AutoSlugField(populate_from='name')
    objects = GISManager()

    class Meta:
        abstract=True

    def get_data(self):
        query = {f'site__{self._meta.model_name}':self}
        return dict(
            intervals=apps.get_model('thermoglobe','interval').heat_flow.filter(**query),
            temperature=apps.get_model('thermoglobe','temperature').objects.filter(**query),
            conductivity=apps.get_model('thermoglobe','conductivity').objects.filter(**query),
            heat_production=apps.get_model('thermoglobe','heatproduction').objects.filter(**query),
        )

    def get_bibtex(self):
        refs = apps.get_model('thermoglobe','publications').objects.none()
        for qs in self.get_data().values():
            refs = refs | qs.references.values_list('bibtex')
        return refs

class Country(Base):
    model_description = "<p>All country names in ThermoGlobe are determined using the World Borders Dataset provided by Bjorn Sandvik and accessible at <a href='http://thematicmapping.org/'>thematicmapping.org</a>.</p>"

    mapping = {
            'iso3' : 'ISO3',
            'name' : 'NAME',
            'region' : 'REGION',
            'subregion' : 'SUBREGION',
            'poly' : 'MULTIPOLYGON',
        }

    region_choices = [
        (2,'Africa'),
        (19,'Americas'),
        (142,'Asia'),
        (150,'Europe'),
        (9,'Oceania'),
    ]

    subregion_choices = [
        (14,'Eastern Africa'),
        (17,'Middle Africa'),
        (15,'Northern Africa'),
        (18,'Southern Africa'),
        (11,'Western Africa'),
        (29,'Caribbean'),
        (13,'Central America'),
        (5,'South America'),
        (21,'Northern America'),
        (143,'Central Asia'),
        (30,'Eastern Asia'),
        (34,'Southern Asia'),
        (35,'South-Eastern Asia'),
        (145,'Western Asia'),
        (151,'Eastern Europe'),
        (154,'Northern Europe'),
        (39,'Southern Europe'),
        (155,'Western Europe'),
        (53,'Australia and New Zealand'),
        (54,'Melanesia'),
        (57,'Micronesia'),
        (61,'Polynesia'),
    ]

    iso3 = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    region = models.IntegerField(choices=region_choices)
    subregion = models.IntegerField(choices=subregion_choices)
    poly = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        db_table = 'country'
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ['name',]

class Continent(Base):
    model_description = "<p>Continents are determined using the World Continents layer package developed by ESRI and freely available online at <a href='https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351darcsgis.com'>arcgis.com</a>. The files downloaded for use in this web application were accesses at some point in early 2019."

    mapping = {
        'objectid': 'OBJECTID',
        'name': 'CONTINENT',
        'poly': 'MULTIPOLYGON',
    }

    objectid = models.BigIntegerField()
    name = models.CharField(max_length=13)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        ordering = ['name',]
        verbose_name = _('continent')
        verbose_name_plural = _('continents')

    def __str__(self):
        return f'{self.name}'

class Sea(Base):
    
    model_description = "<p>Sea&nbsp;and ocean names&nbsp;in ThermoGlobe are calculated from reported site locations using the IHO Sea Areas, version 3 shapefile downloaded from <a href='https://www.marineregions.org/sources.php'>marineregions.org</a> in August of 2019. The source for the actual boundaries is the publication <em>Limits of Oceans, Seas, Special Publication No. 23</em> published by the IHO in 1953. The dataset was composed by the Flanders Marine Data and Information Centre.</p>"
    mapping = {
        'id': 'ID',
        'name': 'NAME',
        'poly': 'MULTIPOLYGON',
    }

    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=100)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        db_table = 'sea'
        ordering = ['name',]
        verbose_name = _('Sea/Ocean')
        verbose_name_plural = _('Seas/Oceans')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)

class Political(Base):

    model_description = '<p>Political regions in ThermoGlobe are determined using the Marine and Land Zones shapefile which is freely available at <a href="https://www.marineregions.org/sources.php">marineregions.org</a>. It was created by the Flanders Marine Institute using the union of the ESRI world country database adn the EEZ V11 dataset.</p>'
    
    mapping = {
        'name': 'UNION',
        'territory': 'TERRITORY1',
        'iso_territory': 'ISO_TER1',
        'un_territory': 'UN_TER1',
        'sovereign': 'SOVEREIGN1',
        'iso_sovereign': 'ISO_SOV1',
        'un_sovereign': 'UN_SOV1',
        'poly': 'MULTIPOLYGON',
    }

    name = models.CharField(max_length=254)

    territory = models.CharField(max_length=254)
    iso_territory = models.CharField(max_length=254, null=True, blank=True)
    un_territory = models.BigIntegerField(null=True, blank=True)

    sovereign = models.CharField(max_length=254)
    iso_sovereign = models.CharField(max_length=254,null=True, blank=True)
    un_sovereign = models.BigIntegerField(null=True, blank=True)

    area_km2 = models.BigIntegerField(null=True, blank=True)
    poly = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Political Region')
        verbose_name_plural = _('Political Regions')

class Province(Base):

    model_description = "<p>Geological provinces are determined using the shapefiel of Hasterok (2021), in prep. It contains polygon features for over 600 geological provinces world wide as well as detailed attributes including minimum and maximum juvenile and thermotectonic age, tectonic environment, last orogenic event and more. Plus a list of references for the data within. Keep your eyes open for it's eventual publication as it is an incredibly useful package for those dealing with tectonics and geology on a global scale!</p>"

    mapping = {
        'source_id': 'id',
        'name': 'prov_name',
        'type': 'prov_type',
        'reference': 'prov_ref',
        'group': 'prov_group',
        'juvenile_age_min': 'juviagemin',
        'juvenile_age_max': 'juviagemax',
        'thermotectonic_age_min': 'tectagemin',
        'thermotectonic_age_max': 'tectagemax',
        'last_orogen': 'lastorogen',
        'continent': 'continent',
        'plate': 'plate',
        'juvenile_age_ref': 'juviageref',
        'thermotectonic_age_ref': 'tectageref',
        'conjugate_province': 'conjugate',
        'poly': 'MULTIPOLYGON',
    }

    source_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=254)
    type = models.CharField(max_length=80,blank=True, null=True)
    reference = models.CharField(max_length=80,blank=True, null=True)
    group = models.CharField(max_length=80,blank=True, null=True)
    juvenile_age_min = models.FloatField(blank=True, null=True)
    juvenile_age_max = models.FloatField(blank=True, null=True)
    thermotectonic_age_min = models.FloatField(blank=True, null=True)
    thermotectonic_age_max = models.FloatField(blank=True, null=True)
    last_orogen = models.CharField(max_length=80,blank=True, null=True)
    continent = models.CharField(max_length=80,blank=True, null=True)
    plate = models.CharField(max_length=80,blank=True, null=True)
    juvenile_age_ref = models.CharField(max_length=128,blank=True, null=True)
    thermotectonic_age_ref = models.CharField(max_length=128,blank=True, null=True)
    conjugate_province = models.CharField(max_length=128,blank=True, null=True)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        db_table = 'geological_province'
        verbose_name = _('Geological Province')
        verbose_name_plural = _('Geological Provinces')

    def __str__(self):
        return '{}'.format(self.name)

