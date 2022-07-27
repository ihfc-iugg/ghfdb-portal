# -*- coding: UTF-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django_extensions.db.fields import AutoSlugField
from django.utils.html import mark_safe
from simple_history.models import HistoricalRecords
from meta.models import ModelMeta
from django.utils.encoding import force_str
from django.contrib.gis.geos import Point
from . import choices
from mapping.models import SiteAbstract
from core.fields import RangeField
from shortuuid.django_fields import ShortUUIDField
from django.core.exceptions import ValidationError

class Site(ModelMeta, SiteAbstract):

    id = ShortUUIDField(
            length=10,
            max_length=15,
            prefix="GHFS-",
            alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
            primary_key=True,
        )

    name = models.CharField(_('name'),
        null=True,
        help_text=_('Specification of the (local) name of the related heat-flow site or the related survey.'),
        max_length=255)
    lat = models.DecimalField(_('latitude'), 
        help_text=_('Latitude in decimal degrees'),
        validators=[MaxValueValidator(90), MinValueValidator(-90)],
        max_digits=7, decimal_places=5,
        db_index=True)
    lng = models.DecimalField(_('longitude'), 
        help_text=_('Longitude in decimal degrees'),
        validators=[MaxValueValidator(180), MinValueValidator(-180)],
        max_digits=8, decimal_places=5,
        db_index=True)
    elevation = RangeField(_('elevation (m)'),
        help_text=_('site elevation with reference to mean sea level (m)'),
        max_value=9000, min_value=-12000,
        blank=True, null=True)
    
    q = models.FloatField(_("heat flow"), help_text=_('site heat flow value'))
    q_unc = RangeField(_("heat flow uncertainty"),  
        help_text=_('uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).'),
        min_value=0,
        blank=True, null=True)
    q_acq = models.DateField(_('date acquired'),
        help_text=_('Year of acquisition of the heat-flow data in the form "YYYY-MM" (may differ from publication year)'),
        null=True,
    )
    env = models.CharField(_("basic geographical environment"),
            help_text=_('Describes the general geographical setting of the heat-flow site (not the applied methodology).'),
            max_length=22, 
            default='unspecified',
            choices=choices.GeographicEnvironment.choices)
    wat_temp = models.FloatField(_('bottom water temperature (°C)'),
        help_text=_('Seafloor temperature where heat-flow measurements were taken.'),
        null=True, blank=True,
    )
    method = models.CharField(_("exploration method"),
            help_text=_('Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry.'),
            max_length=15, 
            choices=choices.ExplorationMethod.choices, 
            blank=True, null=True)
    expl = models.CharField(_("exploration purpose"),
            help_text=_('Main purpose of the original excavation providing access for the temperature sensors.'),
            max_length=19, 
            choices=choices.ExplorationPurpose.choices, 
            blank=True, null=True)


    references = models.ManyToManyField("publications.Publication",
        verbose_name=_("references"),
        help_text=_('The reference or publication from which the data were sourced. Each site may have multiple references.'),
        blank=True)
    q_comment = models.TextField(_("general comments"),
            help_text=_('General comments regarding the heat flow site/measurement'),
            blank=True, null=True)

    # META FIELDS
    # slug = AutoSlugField(populate_from=['name'])
    date_added = models.DateTimeField(_('date added'),
            auto_now_add=True,)
    history = HistoricalRecords()
    _metadata = {
        'title': 'get_meta_title',
        'description': 'description',
        'year': 'year',
        }

    class Meta:
        default_related_name = 'sites'
        unique_together = ('name','lat','lng')
        db_table = 'site'
        ordering = ['-date_added']

    def __unicode__(self):
        return u'%s' %(self.name)

    def __str__(self):
        if self.name:
            return force_str(self.name)
        else:
            return self.coordinates()

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.lng),float(self.lat))
        super().save(*args, **kwargs)

    def coordinates(self):
        return f"{self.lat}, {self.lng}"
       
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
        return f"{self.name} | HeatFlow.org"


class Interval(models.Model):

    id = ShortUUIDField(
            length=8,
            max_length=15,
            prefix="GHFI-",
            alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
            primary_key=True,
        )
    historic_id = models.PositiveIntegerField(_('Historic ID'),
        help_text=_('This is the numeric identifier used in old forms of the GHFDB to identify measurements'),
        blank=True, null=True)
    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                null=True,
                on_delete=models.SET_NULL)
   
    # HEAT FLOW DENSITY FIELDS
    qc = models.FloatField(_("heat flow"), help_text=_('heat flow value'))
    qc_unc = RangeField(_("uncertainty"),  
            help_text=_('uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).'),
            min_value=0,
            blank=True, null=True)
    q_method = models.CharField(_("method"),
            help_text=_('Principal method of heat-flow density calculation from temperature and thermal conductivity data'),
            max_length=8,
            null=True, blank=True,  
            choices=choices.HeatFlowMethod.choices)
    q_top = RangeField(_("interval top (m)"),
            help_text=_('Describes the true vertical depth of the top end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
            max_value=12500,
            blank=True, null=True)
    q_bot = RangeField(_("interval bottom (m)"),
            help_text=_('Describes the true vertical depth of the bottom end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
            min_value=0, max_value=12500,
            blank=True,null=True)

    # PROBE SENSING
    hf_pen = RangeField(_("penetration depth (m)"),
            help_text=_('Depth of penetration of marine probe into the sediment.'),
            min_value=0, max_value=100,
            blank=True, null=True)
    hf_probe = models.CharField(_("probe type"),
            help_text=_('Type of marine probe used for measurement.'),
            max_length=15, 
            choices=choices.ProbeType.choices, 
            blank=True, null=True)
    hf_probeL = RangeField(_("probe length (m)"),
            help_text=_('length of the marine probe.'),
            max_value=100, min_value=0,
            blank=True, null=True)
    T_tilt = RangeField(_("tilt (deg)"),
        help_text=_('Tilt of the marine probe.'),
        max_value=90, min_value=0,
        blank=True, null=True)

    # METADATA AND FLAGS
    q_tf_mech = models.CharField(_("transfer mechanism"),
            help_text=_('Specification of the predominant heat transfer mechanism relevant to the reported heat flow value.'),
            max_length=22, 
            choices=choices.HeatTransfer.choices, 
            blank=True, null=True)
    reference = models.ForeignKey("publications.Publication",
                help_text=_('The publication or other reference from which the measurement was reported.'),
                verbose_name=_("reference"),
                related_name='intervals',
                on_delete=models.CASCADE)
    q_acq = models.DateField(_('date of acquisition (YYYY-MM)'),
        help_text=_('Year of acquisition of the heat-flow data (may differ from publication year)'),
        null=True, blank=True,  
    )
    childcomp = models.BooleanField(_('Is relevant child?'),
        help_text=_('Specifies whether the child entry is used for computation of representative location heat flow values at the parent level or not.'),
        default=None, null=True, blank=True,  
        )
    geo_lith = models.CharField(_("lithology"),
            help_text=_('Dominant rock type/lithology within the interval of heat-flow determination. Use existing BGS rock classification scheme for naming the lithology.'),
            max_length=255, 
            blank=True, null=True)
    geo_strat = models.CharField(_("stratigraphic age"),
            help_text=_('Stratigraphic age of the depth range involved in the reported heat-flow determination.'),
            max_length=64, 
            # choices=choices.StratigraphicAge.choices, 
            blank=True, null=True)

    # Temperature Fields
    T_grad_mean_meas = models.FloatField(_("measured gradient (K/km)"),  
            help_text=_('measured temperature gradient for the heat-flow determination interval.'),
            null=True, blank=True,)
    T_grad_unc_meas = models.FloatField(_("uncertainty (K/km)"),
            help_text=_('uncertainty (standard deviation) of the measured temperature gradient estimated by error propagation from uncertainty in the top and bottom interval temperatures.'),
            blank=True, null=True)
    T_grad_mean_cor = models.FloatField(_("corrected gradient (K/km)"),
            help_text=_('temperature gradient corrected for borehole and environmental effects. Correction method should be recorded in the relevant field.'),
            blank=True, null=True)
    T_grad_unc_cor = models.FloatField(_("uncertainty (K/km)"),  
            help_text=_('uncertainty (standard deviation) of the corrected temperature gradient estimated by error propagation from uncertainty of the measured gradient and the applied correction approaches.'),
            blank=True, null=True)
    T_method_top = models.CharField(_("temperature method (top)"),
            help_text=_('Method used to determine temperature at the top of the heat flow interval.'),
            max_length=10, 
            null=True, blank=True,
            choices=choices.TempMethod.choices,)
    T_method_bot = models.CharField(_("temperature method (bottom)"),
            help_text=_('Method used to determine temperature at the bottom of the heat flow interval.'),
            max_length=10,
            null=True, blank=True, 
            choices=choices.TempMethod.choices,)
    T_shutin_top = models.PositiveSmallIntegerField(_("Shut-in time (top; hrs)"), 
            help_text=_('Time of measurement at the interval top in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling.'),
            blank=True, null=True)
    T_shutin_bot = models.PositiveSmallIntegerField(_("Shut-in time (bottom; hrs)"), 
            help_text=_('Time of measurement at the interval bottom in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling.'),
            blank=True, null=True)
    T_corr_top = models.CharField(_("correction method (top)"),
            help_text=_('Approach used at the top of the heat flow interval to correct the measured temperature for drilling perturbations.'),
            max_length=13, 
            null=True, blank=True,
            choices=choices.TempCorrectionMethod.choices,)
    T_corr_bot = models.CharField(_("correction method (bottom)"),
            help_text=_('Approach used at the bottom of the heat flow interval to correct the measured temperature for drilling perturbations.'),
            max_length=13, 
            null=True, blank=True,
            choices=choices.TempCorrectionMethod.choices,)
    T_numb = models.PositiveSmallIntegerField(_("number of temperature recordings"), 
            help_text=_('Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth.'),
            blank=True, null=True)

    # Conductivity fields    
    tc_mean = RangeField(_("Mean conductivity (W/mK)"),
            help_text=_('Mean conductivity in the vertical direction representative for the heat-flow determination interval. Value should reflect true in-situ conditions for the interval.'),
            null=True, blank=True,
            min_value=0, max_value=100)
    tc_unc = RangeField(_("uncertainty"),
            help_text=_('Uncertainty of the mean thermal conductivity given as one-sigma standard deviation.'),
            min_value=0, max_value=100,
            blank=True, null=True)
    tc_source = models.CharField(_("source"),
            help_text=_('Nature of the samples from which the mean thermal conductivity was determined'),
            max_length=23, 
            null=True, blank=True,
            choices=choices.ConductivitySource.choices)
    tc_meth = models.CharField(_("method"),
            help_text=_('Method used to determine the mean thermal conductivity over the given interval'),
            max_length=100,blank=True,null=True)
    tc_satur = models.CharField(_("saturation state"),
            help_text=_('Saturation state of the rock sample studied for thermal conductivity'),
            max_length=100,null=True, blank=True,)
    tc_pTcond = models.CharField(_("pT conditions"),
            help_text=_('Pressure and temperature conditions under which the mean thermal conductivity for the given interval was determined. "Recorded" - determined under true conditions at target depths (e.g. sensing in boreholes), "Replicated" - determined in a laboratory under replicated in-situ conditions, "Actual" - under conditions at the respective depth of the heat-flow interval'),
            choices=choices.TC_PT_Conditions.choices,
            null=True, blank=True,
            max_length=100)
    tc_pTfunc = models.CharField(_("assumed pT function"),
            help_text=_('Technique or approach used to correct the measured thermal conductivity towards in-situ pT conditions'),
            blank=True, null=True,
            max_length=255)
    tc_strategy = models.CharField(_("averaging methodoloy"),
            help_text=_('Strategy employed to estimate thermal conductivity over the given interval'),
            max_length=255,
            null=True, blank=True,) 
    tc_numb = models.PositiveSmallIntegerField(_("number of temperature recordings"), 
        help_text=_('Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth.'),
            blank=True, null=True)


    corrections = models.ManyToManyField("database.Correction", 
        verbose_name = _('Applied Corrections'),
        )

    # META
    history = HistoricalRecords()
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)

    class Meta:
        db_table = 'heat_flow_interval'
        ordering = ['date_added']
        default_related_name = 'intervals'

    def clean(self, *args, **kwargs):
        # run the base validation
        super().clean(*args, **kwargs)

        # Don't allow year older than 1900.
        if self.q_acq is not None:
            if self.q_acq.year < 1900:
                raise ValidationError('Acquisition year cannot be less than 1900.')

    def full_clean(self, exclude, validate_unique):
        return super().full_clean(exclude, validate_unique)

    def interval(self, obj):
        return '{}-{}'.format(obj.q_top, obj.q_bot)


class Correction(models.Model):

    id = models.CharField(_('Code'), max_length=4, primary_key=True)
    type = models.CharField(_('correction type'),
        max_length=64)

    class Meta:
        db_table = 'heat_flow_correction'

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "type__icontains",)

    def __str__(self):
        return f"{self.type}"