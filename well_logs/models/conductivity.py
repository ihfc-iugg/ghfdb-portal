from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from django.core.validators import MaxValueValidator, MinValueValidator
from ..models.abstract import WellLog, RawData

class Sample(models.Model):
    rock_type = models.CharField(
            _("rock type"),
            max_length=100, 
            blank=True,null=True)
    name = models.CharField(_("sample name"),
            max_length=200,blank=True)
    length = models.FloatField(_("length (cm)"),
            null=True,blank=True)
    width = models.FloatField(_("width (cm)"),
            null=True,blank=True)
    diameter = models.FloatField(_("diameter (cm)"),
            null=True,blank=True)
    thickness = models.FloatField(_("thickness (cm)"),
            null=True,blank=True)

class ConductivityLog(WellLog):

    class Meta:
        default_related_name='conductivity'
        verbose_name_plural = _('thermal conductivity')
        verbose_name = _('thermal conductivity')
        db_table = 'thermal_conductivity_log'

class Conductivity(RawData):
    log = models.ForeignKey("well_logs.ConductivityLog", 
        verbose_name=_("log"), 
        related_name='data',
        on_delete=models.CASCADE,
        null=True,
        )
    
    sample = models.OneToOneField("well_logs.Sample", on_delete=models.CASCADE, null=True, blank=True)
    orientation = models.FloatField(_("orientation"),
            help_text=_('Angle relative to the foliation/bedding where 0 is parallel and 90 is perpendicular'),
            validators=[MaxValueValidator(90), MinValueValidator(0)],
            blank=True, null=True)  

    class Meta:
        db_table = 'thermal_conductivity'
        unique_together = ['value', 'sample', 'log']
        ordering = ['depth']
