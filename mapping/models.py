from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from django.contrib.gis.utils import LayerMapping
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
import time, os, uuid
from django.utils.html import mark_safe
from django.apps import apps

class Base(models.Model):
    slug = AutoSlugField(populate_from='name')

    class Meta:
        abstract=True

    def get_data(self):
        query = {f'site__{self._meta.model_name}':self}
        return dict(
            intervals=apps.get_model('thermoglobe','interval').heat_flow.filter(**query),
            temperature=apps.get_model('thermoglobe','temperature').objects.filter(**query),
            conductivity=apps.get_model('thermoglobe','conductivity').objects.filter(**query),
            heat_generation=apps.get_model('thermoglobe','heatgeneration').objects.filter(**query),
        )

    def get_bibtex(self):
        refs = apps.get_model('thermoglobe','publications').objects.none()
        for qs in self.get_data().values():
            refs = refs | qs.references.values_list('bibtex')
        return refs

class Country(Base):
    model_description = "<p>All country names in ThermoGlobe are determined using the World Borders Dataset provided by Bjorn Sandvik and accessible at <a href='http://thematicmapping.org/'>thematicmapping.org</a>.</p>"

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

    fips = models.CharField(max_length=2, null=True)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    un = models.IntegerField()
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.BigIntegerField()
    region = models.IntegerField(choices=region_choices)
    subregion = models.IntegerField(choices=subregion_choices)
    lon = models.FloatField()
    lat = models.FloatField()
    poly = models.MultiPolygonField(srid=4326)


    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        db_table = 'country'
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        # ordering = ['name',]

class Continent(Base):
    model_description = "<p>Continents are determined using the World Continents layer package developed by ESRI and freely available online at <a href='https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351darcsgis.com'>arcgis.com</a>. The files downloaded for use in this web application were accesses at some point in early 2019."

    objectid = models.BigIntegerField()
    name = models.CharField(max_length=13)
    sqmi = models.FloatField()
    sqkm = models.FloatField()
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        ordering = ['name',]
        verbose_name = _('continent')
        verbose_name_plural = _('continents')

    def __str__(self):
        return '{}'.format(self.name)

class Sea(Base):
    
    model_description = "<p>Sea&nbsp;and ocean names&nbsp;in ThermoGlobe are calculated from reported site locations using the IHO Sea Areas, version 3 shapefile downloaded from <a href='https://www.marineregions.org/sources.php'>marineregions.org</a> in August of 2019. The source for the actual boundaries is the publication <em>Limits of Oceans, Seas, Special Publication No. 23</em> published by the IHO in 1953. The dataset was composed by the Flanders Marine Data and Information Centre.</p>"


    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    min_x = models.FloatField()
    min_y = models.FloatField()
    max_x = models.FloatField()
    max_y = models.FloatField()
    area = models.BigIntegerField()
    mrgid = models.BigIntegerField()
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

class Margin(Base):
    id = models.IntegerField(primary_key=True)
    area = models.FloatField()
    perimetre = models.FloatField()
    superficie = models.FloatField()
    poly = models.MultiPolygonField(srid=4326)

class Basin(Base):
    model_description = "<p>This layer is taken from the CGG Robertson New Ventures product suite. It is a carefully and regularly maintained layer from the Robertson Basins & Plays (formerly Tellus) product. The basin classification has been formulated over 20 years based on an understanding of hard rock outcrop, sediment thickness, structural elements, basin evolution and petroleum systems, with basin definitions refined to fit new information and data from both the public domain and from Robertson’s multi-client studies (Red Books).</p><p>...okay that excerpt was taken straight from the <a href='https://www.arcgis.com/home/item.html?id=528eb519d6114f4c82718870c284b722'>download page</a>. This is a very useful and freely available dataset by CGG Robertson</p>"

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    province = models.CharField(max_length=100, null=True)
    max_fill = models.FloatField()
    exploration_status = models.CharField(max_length=25)
    location = models.CharField(max_length=50)
    sub_regime_group = models.CharField(max_length=100, null=True)
    sub_regime = models.CharField(max_length=100, null=True)
    petsys_status = models.CharField(max_length=50, null=True)
    poly = models.MultiPolygonField(srid=3857)

    class Meta:
        db_table = 'basin'
        verbose_name = _('Sedimentary Basin')
        verbose_name_plural = _('Sedimentary Basins')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)

class Political(Base):

    model_description = '<p>Political regions in ThermoGlobe are determined using the Marine and Land Zones shapefile which is freely available at <a href="https://www.marineregions.org/sources.php">marineregions.org</a>. It was created by the Flanders Marine Institute using the union of the ESRI world country database adn the EEZ V11 dataset.</p>'
    
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
    area_km2 = models.BigIntegerField(blank=True, null=True)
    conjugate_province = models.CharField(max_length=128,blank=True, null=True)
    comments = models.CharField(max_length=254,blank=True, null=True)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        db_table = 'geological_province'
        verbose_name = _('Geological Province')
        verbose_name_plural = _('Geological Provinces')

    def __str__(self):
        return '{}'.format(self.name)