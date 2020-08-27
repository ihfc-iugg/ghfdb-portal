from django.db import models
from django.db.models import F
from .abstract import AgeAbstract, IntervalProperty, SiteProperty, Measurements
from django.utils.translation import gettext as _
from . import choices, units
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models as geomodels
from django_extensions.db.fields import AutoSlugField
from django.contrib.gis.geos import Point
import uuid

# Create your models here.
class Site(AgeAbstract):
    SITE_TYPE = choices.SITE_TYPE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    site_name = models.CharField(_('site name'),
        help_text=_('The name given to the site.'),
        max_length=200)
    latitude = models.DecimalField(_('latitude'),
        help_text=_('Latitude in decimal degrees - maximum 5 decimal places. Precision approximately 1m at the equator. WGS84 preferred but not always the case.'),
        max_digits=7, 
        decimal_places=5,
        validators=[MaxValueValidator(90),
                    MinValueValidator(-90)],)
    longitude = models.DecimalField(_('longitude'),
        help_text=_('Longitude in decimal degrees - maximum 5 decimal places. Precision &tilde; 1m at the equator. WGS84 preferred but not always the case.'),
        max_digits=8, 
        decimal_places=5,
        validators=[MaxValueValidator(180),
            MinValueValidator(-180)],)
    geom = geomodels.PointField(blank=True)
    elevation = models.FloatField(_('elevation'),
        help_text=_('Site elevation'),
        blank=True, null=True)

    site_type = models.CharField(_("site type"),
            help_text=_('The type of site at which the measurements were taken.'),
            max_length=1,
            choices=SITE_TYPE,
            blank=True, null=True)
    operator = models.ForeignKey("publications.Operator",
            verbose_name=_("site operator"),
            help_text=_('The operator of the site.'),
            max_length=150, 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    reference = models.ManyToManyField("publications.Publication",
            verbose_name=_("references"),
            help_text=_('The reference or publication from which the data were sourced. Each site may have multiple references.'),
            related_name='sites',
            blank=True)
    cruise = models.CharField(_("name of cruise"),
            help_text=_('For oceanic measurements - the name of the cruise on which the measurements were taken.'),
            max_length=150, 
            blank=True, null=True)  
    sediment_thickness = models.FloatField(_("calculated sediment thickness"),
            help_text=_('Sediment thickness at the site.'),
            null=True, blank=True)
    sediment_thickness_type = models.CharField(_("type of sediment thickness"),
        max_length=250,
        help_text=_('How sediment thickness was determined.'),
        null=True, blank=True)

    #CALCULATED FIELDS
    seamount_distance = models.FloatField(_("distance to seamount"),
            # verbose_name=_("seamount distance [Km]"),
            help_text=_('Distance in Km to the nearest seamount.'),
            blank=True, null=True)
    outcrop_distance = models.FloatField(_("distance to outcrop"),
            help_text=_('Distance in Km to the nearest outcrop.'),
            blank=True, null=True)

    crustal_thickness = models.FloatField(_("calculated crustal thickness"),
            help_text=_('Calculated crustal thickness at the site.'),
            null=True, blank=True)
    continent = models.ForeignKey("mapping.Continent",
            verbose_name=_('continent'),
            help_text=_('As calculated using the <a href="https://www.arcgis.com/home/item.html?id=a3cb207855b348a297ab85261743351d">ESRI World Continents shapefile</a>.'), 
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    country = models.ForeignKey("mapping.Country", 
            verbose_name=_("country"),
            help_text=_('As calculated using the <a href="http://www.mappinghacks.com/data/">World Borders shapefile</a>.'), 
            related_name='sites', 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    political = models.ForeignKey("mapping.Political",
            verbose_name=_("political region"),
            help_text=_('As calculated using the Flanders Marine Institute (2018)<a href="http://www.marineregions.org/">Marine and Land Zones</a>. DOI: <a href="https://doi.org/10.14284/403">10.14284/403</a>'), 
            related_name='sites', 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    sea = models.ForeignKey("mapping.Sea",
            verbose_name=_("sea/ocean"),
            help_text=_('As calculated using the Flanders Marine Institute (2018)<a href="http://www.marineregions.org/">Oceans and Seas shapefile</a>. DOI: <a href="https://doi.org/10.14284/323">10.14284/323</a>'),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    CGG_basin = models.ForeignKey("mapping.Basin",
            verbose_name=_("CGG Robertson Basin"),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)

    # MEASURED FIELDS
    surface_temp = models.OneToOneField("Temperature", 
                verbose_name=_("surface temperature"),
                help_text=_('Temperature at the surface. Can be either a top of hole temperature or bottom of water temperature for oceanic measurements'),
                related_name='surface_temp',
                blank=True,
                null=True,
                on_delete=models.SET_NULL)
    bottom_water_temp = models.OneToOneField("Temperature",
        verbose_name=_("bottom water temperature"),
        help_text=_('Temperature at the bottom of the water column.'),
        related_name='bottom_water_temp',
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    bottom_hole_temp = models.OneToOneField("Temperature",
        verbose_name=_("bottom of hole temperature"),
        help_text=_('Temperature at the bottom of the hole.'),
        related_name='bottom_hole_temp',
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    well_depth = models.FloatField(_("well depth"),
            help_text=_('Total depth of the hole in metres.'),
            blank=True, null=True)
            
    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])

    class Meta:
        unique_together = ('site_name','latitude','longitude')
        db_table = 'site'
        # ordering = ['date_added']

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.longitude),float(self.latitude))
        super().save(*args, **kwargs)

class HeatFlow(Measurements):
    UNITS = '[{}]'.format(units.HTML.get('heat_flow'))

    RELIABILITY_CHOICES = tuple((val,val) for val in ['A','B','C','D','E','R','Z'])
    reliability = models.CharField(_("heat flow reliability"),
            help_text=_('Heat flow reliability code'),
            max_length=1, 
            choices=RELIABILITY_CHOICES, 
            blank=True, null=True)
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                related_name='heat_flow',
                blank=True, null=True,
                on_delete=models.CASCADE)
    tilt = models.FloatField(_("probe tilt"),
            help_text=_('Angle between vertical and the orientation of the probe.'),
            validators=[MaxValueValidator(90),
                    MinValueValidator(0)],
            blank=True, null=True)

    depth_min = models.FloatField(_("minimum depth"),
            help_text=_('Minimum depth of the measurement interval.'),
            blank=True,null=True)
    depth_max = models.FloatField(_("maximum depth"),
            help_text=_('Maximum depth of the measurement interval.'),
            blank=True,null=True)
    number_of_temperatures = models.IntegerField(_("number of temperatures"), 
            help_text=_('Number of temperatures used to determine the estimate.'),
            blank=True, null=True)
    temp_method = models.CharField(_("temperature method"),
            help_text=_('The method used to obtain temperature values.'),
            max_length=200,blank=True)

    heat_flow_corrected = models.FloatField(_("corrected heat flow {}".format(UNITS)),
            help_text=_('The corrected value.'),
            blank=True, null=True)
    heat_flow_corrected_unc = models.FloatField(_("corrected uncertainty {}".format(UNITS)),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected = models.FloatField(_("uncorrected heat flow {}".format(UNITS)),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected_unc = models.FloatField(_("uncorrected uncertainty {}".format(UNITS)),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

    gradient_cor = models.FloatField(_("corrected gradient {}".format(UNITS)),
            help_text=_('The corrected value.'),
            blank=True, null=True)
    gradient_cor_unc = models.FloatField(_("corrected uncertainty {}".format(UNITS)),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    gradient_uncor = models.FloatField(_("uncorrected gradient {}".format(UNITS)),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    gradient_uncor_uncertainty = models.FloatField(_("uncorrected uncertainty {}".format(UNITS)),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

    conductivity = models.FloatField(_("thermal conductivity"),
            help_text=_('Reported thermal conductivity to accompany the heat flow estimate.'),
            blank=True, null=True)
    conductivity_uncertainty = models.FloatField(_("thermal conductivity uncertainty"),
            help_text=_('Uncertainty of the reported thermal conductivity.'),
            blank=True, null=True)
    number_of_conductivities = models.FloatField(_("number of conductivity measurements"),
            help_text=_('Number of thermal conductivities from which the reported thermal conductivity was derived.'),
            blank=True, null=True)
    conductivity_method = models.CharField(_("thermal conductivity method"),
            help_text=_('Method used to measure or derive thermal conductivity.'),
            max_length=150,
            blank=True, null=True)

    heat_gen = models.FloatField(_("average heat generation"),
            help_text=_('Average heat generation to accompany the heat flow estimate.'),
            blank=True, null=True)
    heat_gen_unc = models.FloatField(_("heat generation uncertainty"),
            help_text=_('Uncertainty of the reported heat generation.'),
            blank=True, null=True)
    num_heat_gen = models.FloatField(_("number of heat generation measurements"),
            help_text=_('Number of heat generation values from which the average heat generation was derived.'),
            blank=True, null=True)
    heat_gen_method = models.CharField(_("heat generation method"),
            help_text=_('Method used to measure or derive heat generation.'),
            max_length=150,
            blank=True, null=True)

    global_flag = models.BooleanField(_('global flag'),
        help_text=_('Measurement is suitable for use in global modelling.'),
        null=True, default=None)
    global_reason = models.CharField(_('global reason'),
        max_length=200,
        help_text=_('reason for denoting this measurement as suitable for global modelling'),
        blank=True, null=True)
    global_by = models.CharField(_('global reason'),
        max_length=100,
        help_text=_('reason for denoting this measurement as suitable for global modelling'),
        blank=True, null=True)

    class Meta:
        verbose_name_plural = 'heat flow'
        db_table = 'heat_flow'


    # def __str__(self):
    #     if self.corrected:
    #         if self.corrected_uncertainty:
    #             return '{} ({})'.format(self.corrected,self.corrected_uncertainty)
    #         else:
    #             return '{}'.format(self.corrected)
    #     else:
    #         if self.uncorrected_uncertainty:
    #             return '{} ({})'.format(self.uncorrected,self.uncorrected_uncertainty)
    #         else:
    #             return '{}'.format(self.uncorrected)

    def clean(self):
        if not self.corrected and not self.uncorrected:
            raise ValidationError(
                _('{} entries must contain either a corrected or uncorrected heat flow value.'.format(
                    self._meta.verbose_name.title())), code='invalid') 
        super().clean()

    def is_corrected(self,obj):
        return True if self.corrected else False
    is_corrected.boolean = True

class Correction(models.Model):
    heatflow = models.OneToOneField("HeatFlow",
        related_name='corrections',
        blank=True, null=True, 
        on_delete=models.CASCADE)
    
    climate_flag = models.BooleanField(_('climate corrected'),null=True, default=None)
    climate = models.FloatField(_('value'),
            help_text=_('Value of a climatic correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    topographic_flag = models.BooleanField(_('topographic corrected'),null=True, default=None)
    topographic = models.FloatField(_('value'),
            help_text=_('Value of a topographic correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    refraction_flag = models.BooleanField(_('refraction corrected'),null=True, default=None)
    refraction = models.FloatField(_('value'),
            help_text=_('Value of a refraction correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    sed_erosion_flag = models.BooleanField(_('sedimentation corrected'),null=True, default=None)
    sed_erosion = models.FloatField(_('value'),
            help_text=_('Value of a sedimentation correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    fluid_flag = models.BooleanField(_('fluid corrected'),null=True, default=None)
    fluid = models.FloatField(_('value'),
            help_text=_('Value of a fluid correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    bottom_water_variation_flag = models.BooleanField(_('BWV corrected'),null=True, default=None)
    bottom_water_variation = models.FloatField(_('value'),
            help_text=_('Value of a bottom water variation correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    compaction_flag = models.BooleanField(_('compaction corrected'),null=True, default=None)
    compaction = models.FloatField(_('value'),
            help_text=_('Value of a compaction correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    other_flag = models.BooleanField(_('other'),null=True, default=None)
    other_type = models.CharField(_('type of correction'),
            help_text=_('Specifies the type of correction if the type does not belong to one of the other categories.'),
            max_length=100,blank=True, null=True)
    other = models.FloatField(_('value'),
            help_text=_('Value of any other correction applied to the associated heat flow and thermal gradient estimates.'),
            blank=True, null=True)

    class Meta:
        db_table = 'correction'

    def save(self, *args, **kwargs):
        corrections = ['climate','topographic','refraction','sed_erosion','fluid','bottom_water_variation','compaction','other']
        for correction in corrections:
            if getattr(self,correction):
                setattr(self,correction+'_flag',True)

        super().save(*args, **kwargs)

# class ThermalGradient(IntervalProperty):
#     UNITS = '[{}]'.format(units.HTML.get('gradient'))

#     site = models.ForeignKey("Site",
#                 related_name='gradients',
#                 verbose_name=_("site"),
#                 blank=True, null=True,
#                 on_delete=models.CASCADE)

#     # number_of_temperatures
#     corrected = models.FloatField(_("corrected gradient {}".format(UNITS)),
#             help_text=_('The corrected value.'),
#             blank=True, null=True)
#     corrected_uncertainty = models.FloatField(_("corrected uncertainty {}".format(UNITS)),  
#             help_text=_('Uncertainty on the corrected value.'),
#             blank=True, null=True)
#     uncorrected = models.FloatField(_("uncorrected gradient {}".format(UNITS)),
#             help_text=_('The uncorrected value.'),
#             blank=True, null=True)
#     uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty {}".format(UNITS)),
#             help_text=_('Uncertainty on the uncorrected value.'),
#             blank=True, null=True)

#     heatflow = models.OneToOneField("HeatFlow",
#             related_name='gradient',
#             verbose_name=_("heat flow"),
#             null=True,blank=True,
#             on_delete=models.SET_NULL)
    
#     class Meta:
#         db_table = 'thermal_gradient'

class Conductivity(SiteProperty):
    UNITS = '[{}]'.format(units.HTML.get('conductivity'))

    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    value = models.FloatField(_("thermal conductivity {}".format(UNITS)),
            help_text=_('The reported value of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty {}".format(UNITS)),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    
    
    orientation = models.FloatField(_("orientation"),
            help_text=_('The angle relative to the foliation or bedding where 0 is along foliation and 90 is perpendicular to foliation. Values can be a floating point number anywhere between 0 and 90.'),
            validators=[MaxValueValidator(90), MinValueValidator(0)],
            blank=True, null=True)

    class Meta:
        verbose_name_plural = 'thermal conductivity'
        verbose_name = 'thermal conductivity'
        db_table = 'thermal_conductivity'
        unique_together = ['value','depth','site','reference']

class HeatGeneration(SiteProperty):
    UNITS = '[{}]'.format(units.HTML.get('heat_generation'))

    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    value = models.FloatField(_("heat generation {}".format(UNITS)),
            help_text=_('The reported value of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty {}".format(UNITS)),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    class Meta:
        verbose_name_plural = 'heat generation'
        db_table = 'heat_generation'
        unique_together = ['value','depth','site','reference']

class Temperature(Measurements):
    UNITS = '[{}]'.format(units.HTML.get('temperature'))

    site = models.ForeignKey("Site",
        verbose_name=_("site"),
        blank=True, null=True,
        on_delete=models.CASCADE)
    value = models.FloatField(_("temperature {}".format(UNITS)),
        help_text=_('The reported temperature value at the given depth.')
        )
    depth = models.FloatField(_("depth [m]"),
        help_text=_('The reported depth of the value.'),
        blank=True, null=True)
    method = models.CharField(_("method"),
        help_text=_('The method used to measure the temperature.'),
        max_length=200, blank=True)
    lag_time = models.FloatField(_("lag time"),
        help_text=_('The time waited between drilling and measuring temperature.'),
        blank=True,null=True)
    is_bottom_of_hole = models.BooleanField(_("is bottom?"),
        help_text=_('A boolean flag denoting the measurement was taken at the bottom of the hole.'),
        default=False)

    class Meta:
        verbose_name_plural = 'temperature'
        db_table = 'temperature'
        unique_together = ['value','depth','site','reference']

    def __str__(self):
        return '{}'.format(self.value)