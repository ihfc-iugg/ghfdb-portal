import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from django.core.validators import MaxValueValidator, MinValueValidator
from .querysets import TemperatureQS

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
    date_added = models.DateTimeField(_('date added to ThermoGlobe'),
            auto_now_add=True,
        )
        
    class Meta:
        abstract=True

class Conductivity(SharedProperties):
    units = mark_safe('W m<sup>-1</sup> K<sup>-1</sup>')

    sample_name = models.CharField(_("sample name"),
            help_text=_('The reported name of the sample if applicable.'),
            max_length=200,blank=True)
    site = models.ForeignKey("Site",
                related_name='conductivity',
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    reference = models.ForeignKey("publications.Publication",
                related_name='conductivity',
                help_text=_('The publications or other reference from which the measurement was reported.'),
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    conductivity = models.FloatField(_("thermal conductivity"),
            help_text=_('The reported thermal conductivity in of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty"),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    
    rock_type = models.CharField(_("rock type"),
            help_text=_('The reported rock type.'),
            max_length=100, 
            blank=True,null=True)
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
        verbose_name_plural = _('thermal conductivity')
        verbose_name = _('thermal conductivity')
        db_table = 'thermal_conductivity'
        unique_together = ['conductivity','depth','site','log_id','reference']

    def __str__(self):
        return '{}'.format(self.conductivity)

class HeatProduction(SharedProperties):
    units = mark_safe('&micro;W m<sup>3</sup>')
    site = models.ForeignKey("Site",
                related_name='heat_production',
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    reference = models.ForeignKey("publications.Publication",
                help_text=_('The publications or other reference from which the measurement was reported.'),
                related_name='heat_production',
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    
    rock_type = models.CharField(_("rock type"),
            help_text=_('The reported rock type.'),
            max_length=100, 
            blank=True,null=True)

    heat_production = models.FloatField(_("heat production"),
            help_text=_('The reported value of the sample.'),
        )
    uncertainty = models.FloatField(_("uncertainty"),
            help_text=_('The uncertainty on the reported value.'),
            null=True,blank=True)
    k_pc = models.FloatField(_('K (wt%)'),
        null=True, blank=True)
    th_ppm = models.FloatField(_('Th (ppm)'),
        null=True, blank=True)
    u_ppm = models.FloatField(_('U (ppm)'),
        null=True, blank=True)

    class Meta:
        default_related_name = 'heat_production'
        verbose_name_plural = _('heat production')
        verbose_name = _('heat production')
        db_table = 'heat_production'
        unique_together = ['log_id','heat_production','k_pc','th_ppm','u_ppm','depth','site','reference']

    def __str__(self):
        return '{}'.format(self.heat_production)

class Temperature(SharedProperties):
    objects = TemperatureQS.as_manager()
    
    units = mark_safe('&deg;C')
    site = models.ForeignKey("Site",
        related_name='temperature',
        verbose_name=_("site"),
        blank=True, null=True,
        on_delete=models.CASCADE)
    reference = models.ForeignKey("publications.Publication",
                related_name='temperature',
                help_text=_('The publications or other reference from which the measurement was reported.'),
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)

    temperature = models.FloatField(_("temperature"),
        help_text=_('The reported temperature in at the given depth.')
        )
    uncertainty = models.FloatField(_("uncertainty"),
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
        verbose_name_plural = _('temperature')
        verbose_name = _('temperature')
        db_table = 'temperature'
        unique_together = ['temperature','depth','site','log_id','reference']

    def __str__(self):
        return '{}'.format(self.temperature)
