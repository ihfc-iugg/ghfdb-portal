from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from django.contrib.gis.utils import LayerMapping
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
import os

class SiteAbstract(models.Model):

    site_name = models.CharField(max_length=200)
    latitude = models.DecimalField(
        max_digits=7, 
        decimal_places=5,
        validators=[MaxValueValidator(90),
                    MinValueValidator(-90)],)
    longitude = models.DecimalField(
        max_digits=8, 
        decimal_places=5,
        validators=[MaxValueValidator(180),
            MinValueValidator(-180)],)
    geom = models.PointField(blank=True)
    elevation = models.FloatField(blank=True, null=True)
    continent = models.ForeignKey("mapping.Continent", 
            verbose_name=_("continent"),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    country = models.ForeignKey("mapping.Country", 
            verbose_name=_("country"),
            related_name='sites', 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    sea = models.ForeignKey("mapping.Sea",
            verbose_name=_("sea name"),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    CGG_basin = models.ForeignKey("mapping.Basin",
            verbose_name=_("CGG Robertson Basin"),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])

    class Meta:
        abstract=True

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.longitude),float(self.latitude))
        super().save(*args, **kwargs)

class Country(models.Model):
    region_choices = (
        (2,'Africa'),
        (19,'Americas'),
        (142,'Asia'),
        (150,'Europe'),
        (9,'Oceania'),
    )

    subregion_choices = (
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
    )

    fips = models.CharField(max_length=2)
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
        verbose_name_plural = _('countries')
        ordering = ['name',]

class Continent(models.Model):
    objectid = models.BigIntegerField()
    name = models.CharField(max_length=13)
    sqmi = models.FloatField()
    sqkm = models.FloatField()
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        ordering = ['name',]


    def __str__(self):
        return '{}'.format(self.name)

class Sea(models.Model):
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

    def __str__(self):
        return '{}'.format(self.name)

class Margin(models.Model):
    id = models.IntegerField(primary_key=True)
    area = models.FloatField()
    perimetre = models.FloatField()
    superficie = models.FloatField()
    poly = models.MultiPolygonField(srid=4326)

class Basin(models.Model):
    name = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    sed_thickness = models.FloatField()
    exploration_status = models.CharField(max_length=25)
    location = models.CharField(max_length=50)
    sub_regime_group = models.CharField(max_length=100)
    sub_regime = models.CharField(max_length=100)
    system_status = models.CharField(max_length=50)
    poly = models.MultiPolygonField(srid=4326)

    class Meta:
        db_table = 'CGG_basin'

    def __str__(self):
        return '{}'.format(self.name)