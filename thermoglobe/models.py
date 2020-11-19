import time, os, uuid
from django.db import models
from django.db.models import F, Q, Avg, Count, Case, When, Value
from django.db.models.functions import Coalesce

from .abstract import SiteProperty
from django.utils.translation import gettext as _
from django.urls import reverse
from . import choices, units
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models as geomodels
from django_extensions.db.fields import AutoSlugField
from django.contrib.gis.geos import Point
from publications.models import PublicationAbstract, AuthorAbstract
from meta.models import ModelMeta
from simple_history.models import HistoricalRecords
from bibtexparser.bibdatabase import BibDatabase
import bibtexparser
from itertools import chain
from collections import Counter
from thermoglobe.managers import SiteManager, HeatFlowManager, GradientManager, SiteQS
from ckeditor.fields import RichTextField

class Site(models.Model):

    objects = SiteQS().as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    site_name = models.CharField(_('site name'),
        help_text=_('The name given to the site.'),
        max_length=200)
    latitude = models.FloatField(_('latitude'),
        help_text=_('Latitude in decimal degrees. WGS84 preferred but not enforced.'),
        validators=[MaxValueValidator(90),
                    MinValueValidator(-90)],)
    longitude = models.FloatField(_('longitude'),
        help_text=_('Longitude in decimal degrees. WGS84 preferred but not enforced.'),
        validators=[MaxValueValidator(180),
            MinValueValidator(-180)],)
    geom = geomodels.PointField(blank=True)
    elevation = models.FloatField(_('elevation'),
        help_text=_('Site elevation'),
        blank=True, null=True)
    well_depth = models.FloatField(_("well depth"),
            help_text=_('Total depth of the hole in metres.'),
            validators=[MaxValueValidator(12500),
                    MinValueValidator(0)],
            blank=True, null=True)
    reference = models.ManyToManyField("thermoglobe.Publication",
            verbose_name=_("references"),
            help_text=_('The reference or publication from which the data were sourced. Each site may have multiple references.'),
            related_name='sites',
            blank=True)
    cruise = models.CharField(_("name of cruise"),
            help_text=_('For oceanic measurements - the name of the cruise on which the measurements were taken.'),
            max_length=150, 
            blank=True, null=True)  
    seafloor_age = models.FloatField(_("well depth"),
            help_text=_('Total depth of the hole in metres.'),
            validators=[MaxValueValidator(90),
                    MinValueValidator(0)],
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
    province = models.ForeignKey("mapping.Province",
        verbose_name=_("geological province"),
        related_name='sites', 
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    sea = models.ForeignKey("mapping.Sea",
            verbose_name=_("sea/ocean"),
            help_text=_('As calculated using the Flanders Marine Institute (2018)<a href="http://www.marineregions.org/">Oceans and Seas shapefile</a>. DOI: <a href="https://doi.org/10.14284/323">10.14284/323</a>'),
            related_name='sites', 
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    basin = models.ForeignKey("mapping.Basin",
            verbose_name=_("basin"),
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

    description = RichTextField(_("site description"),
            null=True, blank=True)
    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])

    class Meta:
        unique_together = ('site_name','latitude','longitude')
        db_table = 'site'
        # ordering = ['date_added']

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.longitude),float(self.latitude))
        # self.type = 'C' if self.province else 'O'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("thermoglobe:site", kwargs={"slug": self.slug})

    def get_data(self):
        return {
            'interval' : self.intervals.all(),
            'temperature': self.temperature.all(),
            'conductivity': self.conductivity.all(),
            'heat_generation': self.heat_generation.all(),
        }

class Interval(models.Model):
    objects = models.Manager()
    heat_flow = HeatFlowManager()
    gradient = GradientManager()


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UNITS = '[{}]'.format(units.HTML.get('heat_flow'))
    RELIABILITY_CHOICES = tuple((val,val) for val in ['A','B','C','D','E','R','Z'])

    reliability = models.CharField(_("heat flow reliability"),
            help_text=_('Heat flow reliability code'),
            max_length=1, 
            choices=RELIABILITY_CHOICES, 
            blank=True, null=True)
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                related_name='intervals',
                blank=True, null=True,
                on_delete=models.CASCADE)
    tilt = models.FloatField(_("probe tilt"),
            help_text=_('Angle between vertical and the orientation of the probe.'),
            validators=[
                MaxValueValidator(90),
                MinValueValidator(0)],
            blank=True, null=True)

    depth_min = models.FloatField(_("depth min"),
            help_text=_('Minimum depth of the measurement interval.'),
            validators=[
                MaxValueValidator(12500,'Maximum depth may not exceed 12,500m.'),
                MinValueValidator(0, 'Depth cannot be less than 0m.')],
            blank=True,null=True)
    depth_max = models.FloatField(_("depth max"),
            help_text=_('Maximum depth of the measurement interval.'),
            validators=[
                MaxValueValidator(12500,'Maximum depth may not exceed 12,500m.'),
                MinValueValidator(0, 'Depth cannot be less than 0m.')],
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
    heat_flow_corrected_uncertainty = models.FloatField(_("corrected uncertainty {}".format(UNITS)),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected = models.FloatField(_("uncorrected heat flow {}".format(UNITS)),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty {}".format(UNITS)),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

    gradient_corrected = models.FloatField(_("corrected gradient {}".format(UNITS)),
            help_text=_('The corrected value.'),
            blank=True, null=True)
    gradient_corrected_uncertainty = models.FloatField(_("corrected uncertainty {}".format(UNITS)),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    gradient_uncorrected = models.FloatField(_("uncorrected gradient {}".format(UNITS)),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    gradient_uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty {}".format(UNITS)),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

    average_conductivity = models.FloatField(_("thermal conductivity"),
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

    heat_generation = models.FloatField(_("average heat generation"),
            help_text=_('Average heat generation to accompany the heat flow estimate.'),
            blank=True, null=True)
    heat_generation_uncertainty = models.FloatField(_("heat generation uncertainty"),
            help_text=_('Uncertainty of the reported heat generation.'),
            blank=True, null=True)
    number_of_heat_gen = models.FloatField(_("number of heat generation measurements"),
            help_text=_('Number of heat generation values from which the average heat generation was derived.'),
            blank=True, null=True)
    heat_generation_method = models.CharField(_("heat generation method"),
            help_text=_('Method used to measure or derive heat generation.'),
            max_length=150,
            blank=True, null=True)

    reference = models.ForeignKey("thermoglobe.Publication",
                help_text=_('The publication or other reference from which the measurement was reported.'),
                verbose_name=_("reference"),
                related_name='intervals', 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    comment = models.TextField(_("comment"),
            help_text=_('Information supplied with the measurement either by the original author/researcher or the compiler.'),
            blank=True,null=True)
    source = models.CharField(max_length=50,blank=True,null=True)

    global_flag = models.BooleanField(_('global flag'),
        help_text=_('Measurement is suitable for use in global modelling.'),
        null=True, default=None)
    global_reason = models.CharField(_('reason'),
        max_length=200,
        help_text=_('reason for denoting this measurement as suitable for global modelling'),
        blank=True, null=True)
    global_by = models.ForeignKey("users.CustomUser",
        related_name='declared_global',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'interval'

    # def clean(self):
    #     if not self.heat_flow_corrected and not self.heat_flow_uncorrected:
    #         raise ValidationError(
    #             _('{} entries must contain either a corrected or uncorrected heat flow value.'.format(
    #                 self._meta.verbose_name.title())), code='invalid') 
    #     super().clean()

    def is_corrected(self,obj):
        return True if self.corrected else False
    is_corrected.boolean = True

class Correction(models.Model):
    heatflow = models.OneToOneField("Interval",
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

class SharedProperties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formation = models.CharField(_("formation name"),
        help_text=_('The name of the sampled geological formation.'),
        max_length=200,blank=True)
    depth = models.FloatField(_("depth"),
            help_text=_('The depth at which the measurement was taken (if applicable).'),
            blank=True, null=True)
    method = models.CharField(_("method"),
            help_text=_('The method used to obtain the reported value.'),
            max_length=200,blank=True)
    operator = models.CharField(_("operator"),
            help_text=_('The operator collecting the measurements'),
            max_length=150, 
            blank=True, null=True)
    comment = models.TextField(_("comment"),
            help_text=_('Information supplied with the measurement either by the original author/researcher or the compiler.'),
            blank=True,null=True)
    source = models.CharField(max_length=50,blank=True,null=True)
    source_id = models.CharField(_("source ID"),
            help_text=_('This is the ID for the measurement used by the original source'),
            max_length=150, 
            blank=True, null=True)
    log_id = models.CharField(_("log specific ID"),
            help_text=_('This is required for multiple logs to be stored on the same site.'),
            max_length=64, 
            blank=True, null=True)
    year_logged = models.PositiveIntegerField(_("year logged"),
        help_text=_('Year the measurement was made.'),
        validators=[MinValueValidator(1900),MaxValueValidator(2050)],
        blank=True, null=True,
        )
    
    class Meta:
        abstract=True

class Conductivity(SiteProperty,SharedProperties):
    UNITS = '[{}]'.format(units.HTML.get('conductivity'))

    site = models.ForeignKey("Site",
                related_name='conductivity',
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    reference = models.ForeignKey("thermoglobe.Publication",
                related_name='conductivity',
                help_text=_('The publication or other reference from which the measurement was reported.'),
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    conductivity = models.FloatField(_("thermal conductivity {}".format(UNITS)),
            help_text=_('The reported value of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty {}".format(UNITS)),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    
    sample_length = models.FloatField(_("sample length"),
            help_text=_('Length of the sample.'),
            null=True,blank=True)
    sample_width = models.FloatField(_("sample width"),
            help_text=_('Width of the sample.'),
            null=True,blank=True)
    sample_diameter = models.FloatField(_("sample diameter"),
            help_text=_('Diameter of the sample.'),
            null=True,blank=True)
    sample_thickness = models.FloatField(_("sample thickness"),
            help_text=_('Thickness of the sample.'),
            null=True,blank=True)
    orientation = models.FloatField(_("orientation"),
            help_text=_('The angle relative to the foliation or bedding where 0 is along foliation and 90 is perpendicular to foliation. Values can be a floating point number anywhere between 0 and 90.'),
            validators=[MaxValueValidator(90), MinValueValidator(0)],
            blank=True, null=True)

    class Meta:
        verbose_name_plural = 'thermal conductivity'
        verbose_name = 'thermal conductivity'
        db_table = 'thermal_conductivity'
        unique_together = ['conductivity','depth','site','log_id','reference']

    def __str__(self):
        return '{}'.format(self.conductivity)

class HeatGeneration(SiteProperty,SharedProperties):
    UNITS = '[{}]'.format(units.HTML.get('heat_generation'))

    site = models.ForeignKey("Site",
                related_name='heat_generation',
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    reference = models.ForeignKey("thermoglobe.Publication",
                help_text=_('The publication or other reference from which the measurement was reported.'),
                related_name='heat_generation',
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    heat_generation = models.FloatField(_("heat generation {}".format(UNITS)),
            help_text=_('The reported value of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty {}".format(UNITS)),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    
    class Meta:
        verbose_name_plural = 'heat generation'
        db_table = 'heat_generation'
        unique_together = ['heat_generation','depth','site','reference']

    def __str__(self):
        return '{}'.format(self.heat_generation)

class Temperature(SharedProperties):
    UNITS = '[{}]'.format(units.HTML.get('temperature'))
    site = models.ForeignKey("Site",
        related_name='temperature',
        verbose_name=_("site"),
        blank=True, null=True,
        on_delete=models.CASCADE)
    reference = models.ForeignKey("thermoglobe.Publication",
                related_name='temperature',
                help_text=_('The publication or other reference from which the measurement was reported.'),
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    
    temperature = models.FloatField(_("temperature {}".format(UNITS)),
        help_text=_('The reported temperature value at the given depth.')
        )
    uncertainty = models.FloatField(_("uncertainty {}".format(UNITS)),
        help_text=_('Uncertainty on the reported temperature.'),
        null=True,blank=True)
       
    
    circ_time = models.FloatField(_("circulation time"),
        help_text=_('Circulation time in hours.'),
        blank=True,null=True)
    lag_time = models.FloatField(_("lag time"),
        help_text=_('Hours between drilling and measuring temperature.'),
        blank=True,null=True)
    correction = models.CharField(_("correction"),
            help_text=_('Applied temperature correction type.'),
            max_length=150, 
            blank=True, null=True)

    class Meta:
        verbose_name_plural = 'temperature'
        db_table = 'temperature'
        unique_together = ['temperature','depth','site','log_id','reference']

    def __str__(self):
        return '{}'.format(self.temperature)

class Author(ModelMeta, AuthorAbstract):

    _metadata = {
        'title': 'get_meta_title',
        'description': 'get_full_name',
        }

    class Meta:
        db_table = 'authors'
        ordering = ['last_name', 'first_name','middle_name']

    @staticmethod
    def autocomplete_search_fields():
        return ("last_name__icontains",) #the fields you want here

    # def get_publications(self):
    #     return super().get_publications().distinct()
        # .annotate(
        #     _sites=Count('sites',distinct=True),
        #     _heat_flow=Count('intervals',distinct=True),
        #     # _thermal_gradient=Count('thermalgradient',distinct=True),
        #     _temperature=Count('temperature',distinct=True),
        #     _thermal_conductivity=Count('conductivity',distinct=True),
        #     _heat_generation=Count('heatgeneration',distinct=True),
        # )

    def data_counts(self):
        return self.get_publications().aggregate(
            heat_flow=Sum('_heat_flow'),
            thermal_gradient=Sum('_thermal_gradient'),
            temperature=Sum('_temperature'),
            thermal_conductivity=Sum('_thermal_conductivity'),
            heat_generation=Sum('_heat_generation'),
        )


    def get_meta_title(self):
        return '{} | HeatFlow.org'.format(self.get_full_name())

    def get_absolute_url(self):
        return reverse("publications:author_details", kwargs={"slug": self.slug})

    def total_sites(self):
        return self.get_publications().aggregate(Count('sites',distinct=True))

    def sites(self):
        return Site.objects.filter(reference__in=self.get_publications()).distinct()

    def as_first_author(self):
        """Returns the number of publications where the current author is listed as first author""" 
        return list(self.publications.through.objects.filter(author=self).values_list('sort_value',flat=True)).count(1)
    
    def as_co_author(self):
        """Returns the number of publications where the current author is listed as a co-author""" 
        return self.get_publications().count() - self.as_first_author()

    def related_authors(self):
        authors = []
        for pub in self.get_publications():
            authors.append(pub.authors.all())

        return Counter(list(chain(*authors))).most_common()[1:6]

    def get_data(self):
        return {
            'interval' : Interval.objects.filter(reference__in=self.get_publications()),
            'temperature': Temperature.objects.filter(reference__in=self.get_publications()),
            'conductivity': Conductivity.objects.filter(reference__in=self.get_publications()),
            'heat_generation': HeatGeneration.objects.filter(reference__in=self.get_publications()),
        }
        
class Publication(ModelMeta, PublicationAbstract):
    is_featured = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from=['id','title'])
    source = models.CharField(max_length=100,
        default='User Upload',
        blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey("users.CustomUser",
        related_name='verifications',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    date_verified = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.CharField(max_length=150,blank=True,null=True)

    history = HistoricalRecords()
    _metadata = {
        'title': 'get_meta_title',
        'description': 'title',
        'authors': 'display_authors',
        'year': 'year',
        }

    class Meta:
        db_table = 'publications'
        ordering = [F('year').desc(nulls_last=True)]

    @property
    def avg_heat_flow(self):
        return self.heatflow_data.aggregate(avg_corrected=Avg('corrected'),avg_uncorrected=Avg('uncorrected'))

    def data_counts(self):
        return {
            'heat_flow': self.heatflow.count()
        }

    def get_meta_title(self):
        return '{} | HeatFlow.org'.format(self.bib_id)

    def get_author_model(self):
        return Author
        # return self.aggregate(
        #     # sites=Sum('_sites'),
        #     heat_flow=Sum('heatflow'),
        #     thermal_gradient=Sum('thermalgradient'),
        #     _temperature=Sum('temperature'),
        #     thermal_conductivity=Sum('conductivity'),
        #     heat_generation=Sum('heatgeneration'),
        # )

    def get_data(self):
        return {
            'interval' : self.intervals.all(),
            'temperature': self.temperature.all(),
            'conductivity': self.conductivity.all(),
            'heat_generation': self.heat_generation.all(),
        }

    def get_absolute_url(self):
        return reverse("publications:publication_details", kwargs={"pk": self.pk})
    
def file_storage_path(instance, filename):
    path = 'data/{}'.format(time.strftime("%Y/%m/"))
    name = '{}_{}.{}'.format(instance.last_name,instance.first_name,filename.split('.')[1])
    return os.path.join(path, name)

class Upload(models.Model):
    data_choices = (
        (0,'Heat Flow'),
        (1,'Thermal Gradient'),
        (2,'Temperature'),
        (3,'Thermal Conductivity'),
        (4,'Heat Generation'),
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    data_type = models.IntegerField(choices=data_choices,default=0)
    data = models.FileField(upload_to=file_storage_path)
    bibtex = models.TextField(blank=True, null=True)

    date_uploaded = models.DateTimeField(auto_now_add=True)
    imported = models.BooleanField(default=False)
    date_imported = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Upload'
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.data.name