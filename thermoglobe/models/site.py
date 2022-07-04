import uuid
from django.db import models
from django.db.models import Avg, Count, Max, Min, StdDev, Func
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models as geomodels
from django_extensions.db.fields import AutoSlugField
from django.contrib.gis.geos import Point
from django.utils.html import mark_safe
from simple_history.models import HistoricalRecords
from .querysets import PlotQueryset
from django.apps import apps 
from meta.models import ModelMeta
from django.utils.encoding import force_str
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance 

class Round(Func):
    function = 'ROUND'
    template="%(function)s(%(expressions)s::numeric, 2)"

class SiteQS(PlotQueryset):
    
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

class Site(ModelMeta,models.Model):
    objects = SiteQS().as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    site_name = models.CharField(_('site name'),
        null=True,
        help_text=_('The name given to the site.'),
        max_length=200)
    latitude = models.FloatField(_('latitude'),
        help_text=_('Latitude in decimal degrees'),
        validators=[MaxValueValidator(90),
                    MinValueValidator(-90)],
        db_index=True)
    longitude = models.FloatField(_('longitude'),
        help_text=_('Longitude in decimal degrees'),
        validators=[MaxValueValidator(180),
            MinValueValidator(-180)],
        db_index=True)
    geom = geomodels.PointField(blank=True)
    elevation = models.FloatField(_('elevation (m)'),
        help_text=_('Site elevation'),
        blank=True, null=True)
    well_depth = models.FloatField(_("well depth (m)"),
            help_text=_('Total depth of the hole in metres.'),
            validators=[MaxValueValidator(12500),
                    MinValueValidator(0)],
            blank=True, null=True)
    reference = models.ManyToManyField("publications.Publication",
            verbose_name=_("references"),
            help_text=_('The reference or publication from which the data were sourced. Each site may have multiple references.'),
            blank=True)
    cruise = models.CharField(_("cruise name"),
            help_text=_('For oceanic measurements - the name of the cruise on which the measurements were taken.'),
            max_length=150, 
            blank=True, null=True)  
    seafloor_age = models.FloatField(_("sea floor age"),
            help_text=_('Age of the sea floor'),
            validators=[MaxValueValidator(220),
                    MinValueValidator(0)],
            blank=True, null=True)
    sediment_thickness = models.FloatField(_("sediment thickness"),
            help_text=_('Sediment thickness at the site.'),
            null=True, blank=True)
    sediment_thickness_type = models.CharField(_("sediment thickness"),
        max_length=250,
        help_text=_('How sediment thickness was determined.'),
        null=True, blank=True)

    #CALCULATED FIELDS
    seamount_distance = models.FloatField(_("seamount distance"),
            help_text=_('Distance in Km to the nearest seamount.'),
            blank=True, null=True)
    outcrop_distance = models.FloatField(_("outcrop distance"),
            help_text=_('Distance in Km to the nearest outcrop.'),
            blank=True, null=True)
    crustal_thickness = models.FloatField(_("crustal thickness"),
            help_text=_('Calculated crustal thickness at the site.'),
            null=True, blank=True)
    continent = models.ForeignKey("mapping.Continent",
            verbose_name=_('continent'),
            help_text=_('Continent land boundaries'),
            blank=True, null=True, 
            on_delete=models.SET_NULL)
    country = models.ForeignKey("mapping.Country", 
            verbose_name=_("country"),
            help_text=_('Country land boundaries'), 
            blank=True, null=True,
            on_delete=models.SET_NULL)
    political = models.ForeignKey("mapping.Political",
            verbose_name=_("political region"),
            help_text=_('Countries inclusive of exclusive marine economic zones'),
            blank=True, null=True,
            on_delete=models.SET_NULL)
    province = models.ForeignKey("mapping.Province",
        verbose_name=_("geological province"),
        blank=True, null=True, 
        on_delete=models.SET_NULL)
        
    ocean = models.ForeignKey("mapping.Ocean",
            verbose_name=_("ocean"),
            help_text=_('Global oceans and seas'),
            blank=True, null=True, 
            on_delete=models.SET_NULL)

    plate = models.ForeignKey("mapping.Plate",
            verbose_name=_("plate"),
            help_text=_('tectonic plate'),
            blank=True, null=True, 
            on_delete=models.SET_NULL)

    bottom_water_temp = models.FloatField(_('bottom_water_temperature'),
        help_text=_('Temperature at the bottom of the water column.'),
        null=True, blank=True,
    )

    year_drilled = models.IntegerField(_('year drilled'),
        blank=True, null=True)

    description = models.TextField(_("site description"),
            null=True, blank=True)
    slug = AutoSlugField(populate_from=['site_name','latitude','longitude'])
    date_added = models.DateTimeField(_('date added'),
            auto_now_add=True,
        )
    history = HistoricalRecords()

    _metadata = {
        'title': 'get_meta_title',
        'description': 'description',
        'year': 'year',
        }

    class Meta:
        default_related_name = 'sites'
        unique_together = ('site_name','latitude','longitude')
        db_table = 'site'
        ordering = ['-date_added']

    def __str__(self):
        if self.site_name:
            return force_str(self.site_name)
        else:
            return self.coordinates()

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.longitude),float(self.latitude))
        super().save(*args, **kwargs)

    def coordinates(self):
        return f"{self.latitude}, {self.longitude}"
       
    def get_absolute_url(self):
        return reverse("thermoglobe:site", kwargs={"pk": self.pk})

    def get_data(self):
        return {
            'intervals' : self.intervals.all(),
            'temperature': self.temperature_logs.all(),
            'conductivity': self.conductivity_logs.all(),
            'heat_production': self.heat_production_logs.all(),
        }

    def get_meta_title(self):
        return f"{self.site_name} | HeatFlow.org"


    def nearby(self, radius=25):
        """Gets nearby sites within x km radius"""
        point = Point(self.longitude,self.latitude)
        return Site.objects.filter(geom__distance_lt=(point, Distance(km=radius)))

