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

    def count_in(self, model, field='geom'):
        for instance in self.model.objects.all():
            sites = model.objects.filter(**{f'{field}__within':instance.poly})
            print(f"{sites.count()} {model._meta.verbose_name}/s within {instance}")
            instance.sites.add(*sites)


    def load(self, data_dir, verbose=True, strict=True, transform=False):
        data_folder = os.path.join(DATA_DIR, data_dir)
        # data_folder = data_dir
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
    """All country names in ThermoGlobe are determined using the `World Borders Dataset <http://thematicmapping.org>`_ provided by Bjorn Sandvik."""

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

    iso3 = models.CharField(max_length=3) #set to primary key
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
    """Continents are determined using the `World Continents <https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351darcsgis.com>`_ layer package developed by ESRI"""

    model_description = "<p>Continents are determined using the World Continents layer package developed by ESRI and freely available online at <a href='https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351darcsgis.com'>arcgis.com</a>. The files downloaded for use in this web application were accesses at some point in early 2019."

    mapping = {
        'id': 'OBJECTID',
        'name': 'CONTINENT',
        'poly': 'MULTIPOLYGON',
    }

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=13)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        ordering = ['name',]
        verbose_name = _('continent')
        verbose_name_plural = _('continents')

    def __str__(self):
        return f'{self.name}'

class Political(Base):
    """Political regions from the `Marine and Land Zones <https://www.marineregions.org/sources.php>`_ package created by the `Flanders Marine Institute <http://www.vliz.be/en>`_ using the union of the ESRI world country database and the EEZ V11 dataset."""
    
    mapping = {
        'id': 'OBJECTID',
        'iso': 'ISO_3digit',
        'name': 'Country',
        'poly': 'MULTIPOLYGON',
    }

    mapping_old = {
        'name': 'UNION',
        'territory': 'TERRITORY1',
        'iso_territory': 'ISO_TER1',
        'un_territory': 'UN_TER1',
        'sovereign': 'SOVEREIGN1',
        'iso_sovereign': 'ISO_SOV1',
        'un_sovereign': 'UN_SOV1',
        'poly': 'MULTIPOLYGON',
    }
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    iso = models.CharField(max_length=5,blank=True,null=True)

    poly = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Political Region')
        verbose_name_plural = _('Political Regions')

class Province(Base):

    model_description = "<p>Geological provinces are determined using the shapefiel of Hasterok (2021), in prep. It contains polygon features for over 600 geological provinces world wide as well as detailed attributes including minimum and maximum juvenile and thermotectonic age, tectonic environment, last orogenic event and more. Plus a list of references for the data within. Keep your eyes open for it's eventual publication as it is an incredibly useful package for those dealing with tectonics and geology on a global scale!</p>"

    mapping = {
    'name': 'prov_name',
    'type': 'prov_type',
    'group': 'prov_group',
    'last_orogen': 'lastorogen',
    'crust_type': 'crust_type',
    'poly': 'MULTIPOLYGON',
    }

    name = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    group = models.CharField(max_length=254, blank=True, null=True)
    last_orogen = models.CharField(max_length=254, blank=True, null=True)
    crust = models.CharField(max_length=254, blank=True, null=True)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        db_table = 'geological_province'
        verbose_name = _('Geological Province')
        verbose_name_plural = _('Geological Provinces')

    def __str__(self):
        return f'{self.name}'

class Plate(Base):
    crust_choices = [
        ('C', _('Continental')),
        ('O', _('Oceanic')),
    ]

    mapping = {
        'id': 'id',
        'plate_id': 'plate_id',
        'plate': 'plate',
        'name': 'subplate',
        'poly_name': 'poly_name',
        'plate_type': 'plate_type',
        'crust_type': 'crust_type',
        'domain': 'domain',
        'poly': 'MULTIPOLYGON',
    }

    id = models.BigIntegerField(primary_key=True)
    plate_id = models.IntegerField()
    plate = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    poly_name = models.CharField(max_length=100)
    type = models.CharField(max_length=64)
    crust_type = models.CharField(max_length=1,choices=crust_choices)
    domain = models.CharField(max_length=64, blank=True, null=True)
    poly = models.MultiPolygonField(srid=4236)

    class Meta:
        db_table='tectonic_plates'
        verbose_name = _('tectonic plate')
        verbose_name_plural = _('tectonic plates')

    def __str__(self):
        return f'{self.name} ({self.plate})'

class Ocean(Base):

    mapping = {
        'name': 'name',
        'poly': 'MULTIPOLYGON',
    }
    name = models.CharField(max_length=254)
    poly = models.MultiPolygonField(srid=4236)

    class Meta:
        db_table='global_oceans'
        verbose_name = _('Ocean/Sea')
        verbose_name_plural = _('Oceans/Seas')

    def __str__(self):
        return f'{self.name}'