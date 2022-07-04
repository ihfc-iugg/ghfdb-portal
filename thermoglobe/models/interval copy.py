import uuid
from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import mark_safe
from thermoglobe.models import managers 
import thermoglobe.models.custom_fields as custom
from .choices import *

class Interval(models.Model):
    objects = managers.IntervalManager()

    heat_flow_units = mark_safe('mW m<sup>2</sup>')
    gradient_units = mark_safe('&deg;C / Km')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



    site = models.ForeignKey("Site",
                verbose_name=_("site"),
                related_name='intervals',
                blank=True, null=True,
                on_delete=models.CASCADE)
    
 
    



    # HEAT FLOW DENSITY FIELDS
    q = models.FloatField(_("heat flow"), help_text=_('heat flow value'))
    q_unc = custom.RangeField(_("heat flow uncertainty"),  
            help_text=_('uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).'),
            range_min=0,
            blank=True, null=True)
    q_method = models.CharField(_("heat flow method"),
            help_text=_('Heat flow reliability code'),
            max_length=8, 
            choices=Q_METHOD_CHOICES, 
            blank=True, null=True)
    interval_top = custom.RangeField(_("heat flow interval top (m)"),
            help_text=_('Describes the true vertical depth of the top end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
            range_min=0, range_max=12500,
            blank=True, null=True)
    interval_bottom = custom.RangeField(_("heat flow interval bottom (m)"),
            help_text=_('Describes the true vertical depth of the bottom end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
            range_min=0, range_max=12500,
            blank=True,null=True)

    # PROBE SENSING
    hf_pen = custom.RangeField(_("penetration depth (m)"),
            help_text=_('Depth of penetration of marine probe into the sediment.'),
            range_min=0, range_max=100,
            blank=True, null=True)
    hf_probe = models.CharField(_("probe type"),
            help_text=_('Type of heat-flow probe used for measurement.'),
            max_length=16, 
            choices=PROBE_TYPE, 
            blank=True, null=True)
    hf_probe_length = custom.RangeField(_("probe length (m)"),
            help_text=_('length of the heat flow probe.'),
            range_max=100, range_min=0,
            blank=True, null=True)



    # METADATA AND FLAGS
    transfer_mechanism = models.CharField(_("transfer mechanism"),
            help_text=_('Specification of the predominant heat transfer mechanism relevant to the reported heat flow value.'),
            max_length=32, 
            choices=HEAT_TRANSFER, 
            blank=True, null=True)

    reference = models.ForeignKey("publications.Publication",
                help_text=_('The publication or other reference from which the measurement was reported.'),
                verbose_name=_("reference"),
                related_name='intervals', 
                blank=True,null=True, 
                on_delete=models.CASCADE)

    method = models.CharField(_("exploration method"),
            help_text=_('Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry.'),
            max_length=32, 
            choices=EXPLORATION_METHOD, 
            blank=True, null=True)

    exploration_purpose = models.CharField(_("exploration purpose"),
            help_text=_('Main purpose of the original excavation providing access for the temperature sensors.'),
            max_length=32, 
            choices=EXPLORATION_PURPOSE, 
            blank=True, null=True)


    lithology

    strat_age



    # Temperature Fields
    T_method_top = models.CharField(_("temperature method top"),
            help_text=_('Method used to determine temperature at the top of the heat flow interval.'),
            max_length=16, 
            choices=TEMP_METHOD, 
            blank=True, null=True)
    T_method_bot = models.CharField(_("temperature method top"),
            help_text=_('Method used to determine temperature at the bottom of the heat flow interval.'),
            max_length=16, 
            choices=TEMP_METHOD, 
            blank=True, null=True)




    T_tilt = custom.RangeField(_("probe tilt (deg)"),
        help_text=_('Tilt of the marine heat flow probe.'),
        range_max=90,range_min=0,
        blank=True, null=True)





    num_temp = models.IntegerField(_("number of temperatures"), 
            help_text=_('Number of temperatures used to determine the estimate.'),
            blank=True, null=True)
    temp_method = models.CharField(_("temperature method"),
            help_text=_('The method used to obtain temperature values.'),
            max_length=200,blank=True)

    gradient_corrected = models.FloatField(_("corrected gradient"),
            help_text=_('The corrected value.'),
            blank=True, null=True)
    gradient_corrected_uncertainty = models.FloatField(_("corrected uncertainty"),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    gradient_uncorrected = models.FloatField(_("uncorrected gradient"),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    gradient_uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty"),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

    cond_ave = models.FloatField(_("conductivity"),
            help_text=_('Reported thermal conductivity to accompany the heat flow estimate.'),
            blank=True, null=True)
    cond_unc = models.FloatField(_("thermal conductivity uncertainty"),
            help_text=_('Uncertainty of the reported thermal conductivity.'),
            blank=True, null=True)
    num_cond = models.FloatField(_("number of conductivity measurements"),
            help_text=_('Number of thermal conductivities from which the reported thermal conductivity was derived.'),
            blank=True, null=True)
    cond_method = models.CharField(_("cond. method"),
            help_text=_('Method used to measure or derive thermal conductivity.'),
            max_length=150,
            blank=True, null=True)

    heat_prod = models.FloatField(_("heat prod."),
            help_text=_('Average heat production to accompany the heat flow estimate.'),
            blank=True, null=True)
    heat_prod_unc = models.FloatField(_("heat production uncertainty"),
            help_text=_('Uncertainty of the reported heat production.'),
            blank=True, null=True)
    num_heat_prod = models.FloatField(_("number of heat production measurements"),
            help_text=_('Number of heat production values from which the average heat production was derived.'),
            blank=True, null=True)
    heat_prod_method = models.CharField(_("heat production method"),
            help_text=_('Method used to measure or derive heat production.'),
            max_length=150,
            blank=True, null=True)


    comment = models.TextField(_("comment"),
            help_text=_('Information supplied with the measurement either by the original author/researcher or the compiler.'),
            blank=True,null=True)
    source = models.CharField(max_length=50,blank=True,null=True)

    global_flag = models.BooleanField(_('global flag'),
        help_text=_('Measurement is suitable for use in global modelling.'),
        null=True, default=False)
    global_reason = models.CharField(_('reason'),
        max_length=200,
        help_text=_('reason for denoting this measurement as suitable for global modelling'),
        blank=True, null=True)
    global_by = models.ForeignKey("user.User",
        related_name='declared_global',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    
    date_added = models.DateTimeField(_('added'),
            auto_now_add=True,
        )

    class Meta:
        db_table = 'interval'
        ordering = ['date_added']
    def interval(self, obj):
        return '{}-{}'.format(obj.depth_min, obj.depth_max)


class HeatFlow(Interval):

    class Meta:
        proxy=True
        verbose_name = _('heat flow')
        verbose_name_plural = _('heat flow')

    def _corrected(self):
        return True if self.heat_flow_corrected else False
    _corrected.boolean = True

class Gradient(Interval):

    class Meta:
        proxy=True
        verbose_name = _('thermal gradient')
        verbose_name_plural = _('thermal gradients')


    def _corrected(self):
        return True if self.gradient_corrected else False
    _corrected.boolean = True

class Correction(models.Model):
    
    class Type(models.TextChoices):
        CLIMATE = 'CLIM', _('Climate')
        TOPOGRAPHIC = 'TOPO', _('Topographic')
        REFRACTION = 'REFR', _('Refraction')
        FLUID = 'FLUI', _('Fluid')
        BWV = 'BWV', _('Bottom Water Variation')
        EROSION = 'EROS', _('Erosion')
        COMPACTION = 'COMP', _('Compaction')
        OTHER = 'OTH', _('Other')
        COMPOSITE = 'CMPS', _('composite')
        TILT = 'TILT', _('tilt')

    interval = models.ForeignKey("thermoglobe.Interval",
            verbose_name=_("interval"),
            related_name='corrections', 
            on_delete=models.CASCADE)
    type = models.CharField(_('correction type'),
        max_length=4, choices= Type.choices)
    value = models.FloatField(_('value'), blank=True, null=True)

    class Meta:
        db_table = 'heat_flow_correction'