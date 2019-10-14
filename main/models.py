from django.db import models
from django_extensions.db.fields import AutoSlugField
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from site_property.models import SiteProperty, IntervalProperty
from mapping.models import SiteAbstract
from geomodels.models import GeoModelSample
from django.db.models import F
# Abstract models
class TimeStampAbstract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.CharField(max_length=150,blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=150,blank=True,null=True)
    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.OneToOneField("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

class AgeAbstract(models.Model):

    age_min = models.FloatField(blank=True,null=True)
    age_max = models.FloatField(blank=True,null=True)
    age_method = models.CharField(max_length=200,blank=True)

    class Meta:
        abstract=True

# Create your models here.
class Site(SiteAbstract,TimeStampAbstract):
    
    top_hole_temp = models.OneToOneField("Temperature", related_name='top_hole_temp', blank=True, null=True, on_delete=models.CASCADE)
    bottom_hole_temp = models.OneToOneField("Temperature",related_name='bottom_hole_temp', blank=True, null=True, on_delete=models.CASCADE)
    well_depth = models.FloatField(blank=True, null=True)
    dip = models.FloatField(blank=True, null=True)
    operator = models.CharField(max_length=150, blank=True, null=True)
    cruise = models.CharField(max_length=150, blank=True, null=True)  

    #geology information
    sediment_thickness = models.FloatField(null=True, blank=True)
    province = models.ForeignKey("geomodels.Province", blank=True, null=True, on_delete=models.SET_NULL)
    domain = models.ForeignKey("geomodels.Domain", blank=True, null=True, on_delete=models.SET_NULL)
    basin = models.ForeignKey("geomodels.Basin",related_name='basin_name',blank=True,null=True,on_delete=models.SET_NULL)
    sub_basin = models.ForeignKey("geomodels.Basin",related_name='sub_basin_name',blank=True,null=True,on_delete=models.SET_NULL)
    tectonic_environment = models.ForeignKey("geomodels.TectonicEnvironment", blank=True, null=True, on_delete=models.SET_NULL)

    #REFERENCE SET TO CASCADE - be warned - this will delete any associated sites, heatflow or other data when the linked reference is deleted
    reference = models.ForeignKey("reference.Reference", blank=True, null=True,  on_delete=models.CASCADE)

    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])

    class Meta:
        unique_together = ('site_name','latitude','longitude','reference')
        db_table = 'site'
        ordering = [F('site_name').desc(nulls_last=True)]

    def __str__(self):
        return self.site_name

# Belongs to 'Site'
class DepthInterval(TimeStampAbstract,AgeAbstract):
    """Contains all physical measurements as well as geological and age date related to a given depth interval specified by depth_min and depth_max. Has a foreign key relationship with "Site" in which a single site may contain many depth intervals.
    """
    # Specifies that many depth intervals can belong to a single Site
    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)

    # Specifies the reference that this interval came from
    reference = models.ForeignKey("reference.Reference", blank=True, null=True, on_delete=models.CASCADE)

    # model fields
    depth_min = models.FloatField(blank=True,null=True)
    depth_max = models.FloatField(blank=True,null=True)

    # not the same as rock_type lithology, this is a simple description
    lithology = models.ManyToManyField("geomodels.Lithology", blank=True)

    comment = models.TextField(blank=True,null=True)

    class Meta:
        db_table = 'depth_interval'
        ordering = [F('depth_min').desc(nulls_last=True)]


    def __str__(self):
        return '{}-{}'.format(self.depth_min,self.depth_max)

# ManyToMany with 'HeatFlow.correction'
class HeatFlowCorrection(models.Model):
    correction = models.CharField(max_length=200)
    value = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'heat_flow_correction'

    def __str__(self):
        return self.correction

# Belongs to 'DepthInterval'
class HeatFlow(IntervalProperty, TimeStampAbstract):

    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)


    RELIABILITY_CHOICES = tuple((val,val) for val in ['A','B','C','D','E','R','Z'])
    reliability = models.CharField(max_length=1, choices=RELIABILITY_CHOICES, blank=True, null=True)
    corrections = models.ManyToManyField("HeatFlowCorrection", blank=True)
    depth_interval = models.OneToOneField("DepthInterval", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'heat flow'
        db_table = 'heat_flow'

# Belongs to 'DepthInterval'
class TemperatureGradient(IntervalProperty,TimeStampAbstract):
    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)


    """Fields taken from abstract class"""
    depth_interval = models.OneToOneField("DepthInterval", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'temperature_gradient'

# Belongs to 'DepthInterval'
class Conductivity(SiteProperty,TimeStampAbstract,AgeAbstract,GeoModelSample):
   # Each Measurement belongs to a single 'Site' and a single 'Reference'
    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)
    reference = models.ForeignKey("reference.Reference",blank=True,null=True, on_delete=models.CASCADE)
    depth_interval = models.OneToOneField("DepthInterval", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'conductivity'
        db_table = 'thermal_conductivity'
        unique_together = ['value','depth','site']

# Belongs to 'DepthInterval'
class HeatGeneration(SiteProperty,TimeStampAbstract,AgeAbstract,GeoModelSample):

   # Each Measurement belongs to a single 'Site' and a single 'Reference'
    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)
    reference = models.ForeignKey("reference.Reference",blank=True,null=True, on_delete=models.CASCADE)
    depth_interval = models.OneToOneField("DepthInterval", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'heat generation'
        db_table = 'heat_generation'
        unique_together = ['value','depth','site']

# Belongs to 'DepthInterval'
class Temperature(SiteProperty,TimeStampAbstract,AgeAbstract,GeoModelSample):
   # Each Measurement belongs to a single 'Site' and a single 'Reference'
    site = models.ForeignKey("Site", blank=True, null=True, on_delete=models.CASCADE)
    reference = models.ForeignKey("reference.Reference",blank=True,null=True, on_delete=models.CASCADE)

    lag_time = models.FloatField(blank=True,null=True)
    is_top_of_hole = models.BooleanField(default=False)
    is_bottom_of_hole = models.BooleanField(default=False)
 
    class Meta:
        verbose_name_plural = 'temperature'
        db_table = 'temperature'
        unique_together = ['value','depth','site']

