from django.db import models
from mapping.models import SiteAbstract
from django.db.models import F
from .abstract import TimeStampAbstract, AgeAbstract, IntervalProperty, SiteProperty, Measurements
from django.utils.translation import gettext as _
from . import choices

# Create your models here.
class Site(SiteAbstract,TimeStampAbstract, AgeAbstract):
    SITE_TYPE = choices.SITE_TYPE
    site_type = models.CharField(_("site type"),
            max_length=1,
            choices=SITE_TYPE,
            blank=True, null=True)
    operator = models.ForeignKey("reference.Operator",
            verbose_name=_("site operator"),
            max_length=150, 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    reference = models.ManyToManyField("reference.Reference",
            verbose_name=_("references"),
            related_name='sites',
            blank=True)
    cruise = models.CharField(_("name of cruise"),
            max_length=150, 
            blank=True, null=True)  

    #CALCULATED FIELDS
    seamount_distance = models.FloatField(_("distance to seamount"),
                blank=True, null=True)
    outcrop_distance = models.FloatField(_("distance to outcrop"),
            blank=True, null=True)
    ruggedness = models.IntegerField(_("ruggedness"),
            blank=True, null=True)
    sediment_thickness = models.FloatField(_("calculated sediment thickness"),
            null=True, blank=True)
    crustal_thickness = models.FloatField(_("calculated crustal thickness"),
            null=True, blank=True)

    # MEASURED FIELDS
    surface_temp = models.OneToOneField("Temperature", 
                        verbose_name=_("surface temperature"),
                        related_name='surface_temp',
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL)
    bottom_hole_temp = models.OneToOneField("Temperature",
        verbose_name=_("bottom of hole temperature"),
        related_name='bottom_hole_temp',
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    well_depth = models.FloatField(_("well depth"),
            blank=True, null=True)
    dip = models.FloatField(_("well dip"),
            blank=True, null=True)
     
    # GEOLOGICAL FIELDS
    basin = models.ForeignKey("geomodels.Basin",
            verbose_name=_("geological basin"),
            help_text=_("The geological basin in which the site is situated."),
            related_name='basin',
            blank=True,null=True,
            on_delete=models.SET_NULL)
    sub_basin = models.ForeignKey("geomodels.Basin",
            verbose_name=_("geological sub-basin"),
            help_text=_("The geological sub-basin in which the site is situated. More specific than basin."),
            related_name='sub_basin',
            blank=True,null=True,
            on_delete=models.SET_NULL)
    tectonic_environment = models.ForeignKey("geomodels.TectonicEnvironment",
            verbose_name=_("tectonic environment"),
            help_text=_("The tectonic environment in which the site is situated."),
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    lithology = models.CharField(_("lithology"),
            help_text=_("The general lithology of the site."),
        	max_length=150,blank=True,null=True)
    geological_province = models.ForeignKey("geomodels.GeologicalProvince",
            verbose_name=_("geological province"),
            help_text=_("The geological province in which the site is situated."),
            blank=True,null=True,
            on_delete=models.SET_NULL)
    EOH_geo_unit = models.ForeignKey("geomodels.GeologicalUnit",
            verbose_name=_("EOH geological unit"),
            help_text=_("The geologial unit at the bottom of the hole."),
            blank=True,null=True,
            on_delete=models.SET_NULL)
    EOH_rock_type = models.CharField(_("EOH rock type"),
            help_text=_("The rock type at the bottom of the hole."),
            max_length=150, 
            blank=True, null=True)  
    site_status = models.CharField(_("site status"),
            help_text=_("Last known status of the well."),
            max_length=150, 
            blank=True, null=True) 

    USGS_code = models.CharField(_("USGS stratigraphic code"),
            help_text=_("USGS stratigraphic code (Legacy)."),
            max_length=15, 
            blank=True, null=True)

    class Meta:
        unique_together = ('site_name','latitude','longitude')
        db_table = 'site'
        ordering = ['date_added']

    def __str__(self):
        return self.site_name

class HeatFlow(IntervalProperty):

    RELIABILITY_CHOICES = tuple((val,val) for val in ['A','B','C','D','E','R','Z'])
    reliability = models.CharField(_("heat flow reliability"),
            max_length=1, 
            choices=RELIABILITY_CHOICES, 
            blank=True, null=True)
    

    site = models.ForeignKey("Site",
                # related_name='heat_flow_data',
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)

    # model fields 
    conductivity = models.FloatField(_("thermal conductivity"),
            blank=True, null=True)
    conductivity_uncertainty = models.FloatField(_("thermal conductivity uncertainty"),
            blank=True, null=True)
    number_of_conductivities = models.FloatField(_("number of conductivity measurements"),
            blank=True, null=True)
    conductivity_method = models.CharField(_("thermal conductivity method"),
            max_length=150,
            blank=True, null=True)

    class Meta:
        verbose_name_plural = 'heat flow'
        db_table = 'heat_flow'

class Correction(models.Model):
    heatflow = models.OneToOneField("HeatFlow",blank=True, null=True, on_delete=models.CASCADE)
    gradient = models.OneToOneField("ThermalGradient",blank=True, null=True, on_delete=models.CASCADE)
    
    has_climatic = models.BooleanField(default=False)
    climatic = models.FloatField(blank=True, null=True)

    has_topographic = models.BooleanField(default=False)
    topographic = models.FloatField(blank=True, null=True)

    has_refraction = models.BooleanField(default=False)
    refraction = models.FloatField(blank=True, null=True)

    has_sedimentation = models.BooleanField(default=False)
    sedimentation = models.FloatField(blank=True, null=True)

    has_fluid = models.BooleanField(default=False)
    fluid = models.FloatField(blank=True, null=True)

    has_bottom_water_variation = models.BooleanField(default=False)
    bottom_water_variation = models.FloatField(blank=True, null=True)

    has_compaction = models.BooleanField(default=False)
    compaction = models.FloatField(blank=True, null=True)

    has_other = models.BooleanField(default=False)
    other_type = models.CharField(max_length=100,blank=True, null=True)
    other = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'correction'

    def save(self, *args, **kwargs):
        corrections = ['climatic','topographic','refraction','sedimentation','fluid','bottom_water_variation','compaction','other']
        for correction in corrections:
            if getattr(self,correction):
                setattr(self,'has_'+correction,True)


        super().save(*args, **kwargs)

class ThermalGradient(IntervalProperty):
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)


    heatflow = models.OneToOneField("HeatFlow",
            verbose_name=_("heat flow"),
            null=True,blank=True,
            on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'thermal_gradient'

class Conductivity(SiteProperty):
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'conductivity'
        db_table = 'thermal_conductivity'
        unique_together = ['value','depth','site','reference']

class HeatGeneration(SiteProperty):
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'heat generation'
        db_table = 'heat_generation'
        unique_together = ['value','depth','site','reference']

class Temperature(Measurements):
    site = models.ForeignKey("Site",
        verbose_name=_("site"),
        blank=True, null=True,
        on_delete=models.CASCADE)
    value = models.FloatField()
    depth = models.FloatField(blank=True, null=True)
    method = models.CharField(max_length=200,blank=True)
    lag_time = models.FloatField(blank=True,null=True)
    is_bottom_of_hole = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'temperature'
        db_table = 'temperature'
        unique_together = ['value','depth','site','reference']

    def __str__(self):
        return '{}'.format(self.value)