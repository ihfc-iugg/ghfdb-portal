import uuid
from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import mark_safe
from .querysets import HFQueryset, GradientQueryset
from thermoglobe.models import managers 

class Interval(models.Model):
    objects = managers.IntervalManager()
    heat_flow = managers.HeatFlowManager()
    gradient = managers.GradientManager()

    heat_flow_units = mark_safe('mW m<sup>2</sup>')
    gradient_units = mark_safe('&deg;C / Km')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    RELIABILITY_CHOICES = tuple((val,val) for val in ['A','B','C','D','E','R','Z'])

    reliability = models.CharField(_("reliability"),
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

    heat_flow_corrected = models.FloatField(_("corrected heat flow"),
            help_text=_('The corrected value.'),
            blank=True, null=True)
    heat_flow_corrected_uncertainty = models.FloatField(_("corrected uncertainty"),  
            help_text=_('Uncertainty on the corrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected = models.FloatField(_("uncorrected heat flow"),
            help_text=_('The uncorrected value.'),
            blank=True, null=True)
    heat_flow_uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty"),
            help_text=_('Uncertainty on the uncorrected value.'),
            blank=True, null=True)

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

    average_conductivity = models.FloatField(_("therm. cond."),
            help_text=_('Reported thermal conductivity to accompany the heat flow estimate.'),
            blank=True, null=True)
    conductivity_uncertainty = models.FloatField(_("thermal conductivity uncertainty"),
            help_text=_('Uncertainty of the reported thermal conductivity.'),
            blank=True, null=True)
    number_of_conductivities = models.FloatField(_("number of conductivity measurements"),
            help_text=_('Number of thermal conductivities from which the reported thermal conductivity was derived.'),
            blank=True, null=True)
    conductivity_method = models.CharField(_("cond. method"),
            help_text=_('Method used to measure or derive thermal conductivity.'),
            max_length=150,
            blank=True, null=True)

    heat_production = models.FloatField(_("heat prod."),
            help_text=_('Average heat production to accompany the heat flow estimate.'),
            blank=True, null=True)
    heat_production_uncertainty = models.FloatField(_("heat production uncertainty"),
            help_text=_('Uncertainty of the reported heat production.'),
            blank=True, null=True)
    number_of_heat_gen = models.FloatField(_("number of heat production measurements"),
            help_text=_('Number of heat production values from which the average heat production was derived.'),
            blank=True, null=True)
    heat_production_method = models.CharField(_("heat production method"),
            help_text=_('Method used to measure or derive heat production.'),
            max_length=150,
            blank=True, null=True)

    reference = models.ForeignKey("publications.Publication",
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
        null=True, default=False)
    global_reason = models.CharField(_('reason'),
        max_length=200,
        help_text=_('reason for denoting this measurement as suitable for global modelling'),
        blank=True, null=True)
    global_by = models.ForeignKey("users.CustomUser",
        related_name='declared_global',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    
    date_added = models.DateTimeField(_('date added to ThermoGlobe'),
            auto_now_add=True,
        )

    class Meta:
        db_table = 'interval'

    def interval(self, obj):
        return '{}-{}'.format(obj.depth_min, obj.depth_max)

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

    bwv_flag = models.BooleanField(_('BWV corrected'),null=True, default=None)
    bwv = models.FloatField(_('value'),
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
        corrections = ['climate','topographic','refraction','sed_erosion','fluid','bwv','compaction','other']
        for correction in corrections:
            if getattr(self,correction):
                setattr(self,correction+'_flag',True)

        super().save(*args, **kwargs)

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