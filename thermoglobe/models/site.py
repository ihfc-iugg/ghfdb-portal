import os, uuid
from django.db import models
from django.db.models import F, Q, Avg, Count, Max, Min, StdDev
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models as geomodels
from django_extensions.db.fields import AutoSlugField
from django.contrib.gis.geos import Point
from django.utils.html import mark_safe
from thermoglobe.utils import Round
from simple_history.models import HistoricalRecords
from collections import Counter
from ckeditor.fields import RichTextField
import plotly.graph_objects as go
from .querysets import PlotQueryset
from django.apps import apps 
from meta.models import ModelMeta
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str

class SiteQS(PlotQueryset):
    
    def pie_country(self):
        return self.pie('country')

    def pie_sea(self):
        return self.pie('sea')

    def heat_flow(self):
        return self.annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        }).exclude(heat_flow__isnull=True)

    def gradient(self):
        return self.annotate(**{           
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        }).exclude(gradient__isnull=True)
        # return self.annotate(value=F('gradient')).distinct()

    def temperature(self):
        return self.exclude(temperature__isnull=True).annotate(
            count=Count('temperature'),
            min_temperature=Min('temperature__temperature'),
            max_temperature=Max('temperature__temperature'),
            depth_min=Min('temperature__depth'),
            depth_max=Max('temperature__depth'),
            )

    def conductivity(self):
        return self.exclude(conductivity__isnull=True).annotate(
            count=Count('conductivity'),
            std=StdDev('conductivity__conductivity'),
            avg_conductivity=Round(Avg('conductivity__conductivity')),
            min_conductivity=Min('conductivity__conductivity'),
            max_conductivity=Max('conductivity__conductivity'),
            depth_min=Min('conductivity__depth'),
            depth_max=Max('conductivity__depth'),
            )

    def heat_generation(self):
        return self.exclude(heat_generation__isnull=True).annotate(
            count=Count('heat_generation'),
            avg_heat_generation=Round(Avg('heat_generation__heat_generation')),
            min_heat_generation=Min('heat_generation__heat_generation'),
            max_heat_generation=Max('heat_generation__heat_generation'),
            depth_min=Min('heat_generation__depth'),
            depth_max=Max('heat_generation__depth'),
            )

    def table(self,data_type):
        return getattr(self,data_type)()

    def intervals(self):
        return self.annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        })

class SiteManager(models.Manager):

    def get_queryset(self):
        return SiteQS(self.model, using=self._db).annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        })

    @property
    def heat_flow(self):
        return self.get_queryset().heat_flow()

    @property
    def gradient(self):
        return self.get_queryset().gradient()

    @property
    def temperature(self):
        return self.get_queryset().temperature()

    @property
    def conductivity(self):
        return self.get_queryset().conductivity()

    @property
    def heat_generation(self):
        return self.get_queryset().heat_generation()

class Site(ModelMeta,models.Model):
    objects = SiteQS().as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    site_name = models.CharField(_('site name'),
        help_text=_('The name given to the site.'),
        max_length=200)
    latitude = models.FloatField(_('latitude'),
        help_text=_('Latitude in decimal degrees. WGS84 preferred but not enforced.'),
        validators=[MaxValueValidator(90),
                    MinValueValidator(-90)],
        db_index=True)
    longitude = models.FloatField(_('longitude'),
        help_text=_('Longitude in decimal degrees. WGS84 preferred but not enforced.'),
        validators=[MaxValueValidator(180),
            MinValueValidator(-180)],
        db_index=True)
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
    seafloor_age = models.FloatField(_("sea floor age"),
            help_text=_('Age of the sea floor'),
            validators=[MaxValueValidator(220),
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

    # # MEASURED FIELDS
    # surface_temp = models.OneToOneField("Temperature", 
    #             verbose_name=_("surface temperature"),
    #             help_text=_('Temperature at the surface. Can be either a top of hole temperature or bottom of water temperature for oceanic measurements'),
    #             related_name='surface_temp',
    #             blank=True,
    #             null=True,
    #             on_delete=models.SET_NULL)
    # bottom_water_temp = models.OneToOneField("Temperature",
    #     verbose_name=_("bottom water temperature"),
    #     help_text=_('Temperature at the bottom of the water column.'),
    #     related_name='bottom_water_temp',
    #     blank=True,
    #     null=True,
    #     on_delete=models.SET_NULL)

    bwt = models.FloatField(_('bottom_water_temperature'),
        help_text=_('Temperature at the bottom of the water column.'),
        null=True, blank=True,
    )

    year_drilled = models.IntegerField(_('year drilled'),
        blank=True, null=True)

    description = models.TextField(_("site description"),
            null=True, blank=True)
    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])
    history = HistoricalRecords()

    _metadata = {
        'title': 'get_meta_title',
        'description': 'description',
        'authors': 'year_drilled',
        'year': 'year',
        }

    class Meta:
        unique_together = ('site_name','latitude','longitude')
        db_table = 'site'
        # ordering = ['date_added']
        # indexes = [
        #     models.Index(fields=['latitude']),
        #     models.Index(fields=['longitude']),
        # ]
    def __str__(self):
        return force_str(self.site_name if self.site_name else self.pk)

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.longitude),float(self.latitude))
        # self.type = 'C' if self.province else 'O'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("thermoglobe:site", kwargs={"slug": self.slug})

    def get_data(self):
        return {
            # 'interval' : self.intervals.all(),
            'intervals' : apps.get_model('thermoglobe','interval').heat_flow.filter(site=self),
            'temperature': self.temperature.all(),
            'conductivity': self.conductivity.all(),
            'heat_generation': self.heat_generation.all(),
        }

    def get_meta_title(self):
        return f"{self.site_name} | HeatFlow.org"

    # def clean(self):
    #     # save to this and reraise at the end if errors are encountered
    #     errors_dict = {}

    #     # Validate coordinates
    #     if not -90 <= self.latitude <= 90:
    #         errors_dict['latitude'] = ValidationError(_('latitude must be between -90 and 90 degrees'),code='invalid')
    #     if not -180 <= self.longitude <= 180:
    #         errors_dict['longitude'] = ValidationError(_('Longitude must be between -90 and 90 degrees'),code='invalid')

    #     if self.well_depth >12200:
    #         errors_dict['well_depth'] = ValidationError(_('Well depth cannot be deeper than 12,200 m. Have you supplied the correct units?'),code='invalid')

    #     # challenger deep to mt everest
    #     if not -11034 <= self.elevation > 8848:
    #         errors_dict['elevation'] = ValidationError(_('Your elevation value looks wrong. Have you supplied this data in the correct units?'),code='invalid')

    #     if errors_dict:
    #         raise ValidationError(errors_dict)