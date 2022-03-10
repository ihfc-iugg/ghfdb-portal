from django.db import models
from django.utils.translation import gettext_lazy as _
from ..models.abstract import WellLog, RawData


class TemperatureLog(WellLog):
    circ_time = models.FloatField(_("circulation time (hrs)"), blank=True,null=True)
    lag_time = models.FloatField(_("lag time (hrs)"), blank=True,null=True)
    correction = models.CharField(_("correction type"),
            max_length=150, 
            blank=True, null=True)

    class Meta:
        default_related_name='temperature'
        verbose_name = _('temperature')
        verbose_name_plural = _('temperature')
        db_table = 'temp_meta'
        ordering = ['added']

class Temperature(RawData):
    log = models.ForeignKey("well_logs.TemperatureLog", 
        verbose_name=_("log"), 
        related_name='data',
        on_delete=models.CASCADE,
        null=True,
        )

    class Meta:
        verbose_name_plural = _('temperature data')
        verbose_name = _('temperature data')
        db_table = 'temperature'

