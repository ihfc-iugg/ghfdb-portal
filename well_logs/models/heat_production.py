from django.db import models
from django.utils.translation import gettext_lazy as _
from ..models.abstract import WellLog, RawData


class HeatProductionLog(WellLog):
 
    class Meta:
        default_related_name='heat_production_logs'
        verbose_name = _('heat production')
        verbose_name_plural = _('heat production')
        db_table = 'heat_production_log'

class HeatProduction(RawData):
    log = models.ForeignKey("well_logs.HeatProductionLog", 
        verbose_name=_("log"), 
        related_name='data',
        on_delete=models.CASCADE,
        null=True,
        )

    rock_type = models.CharField(_("rock type"), max_length=100, 
            blank=True,null=True)
    k_pc = models.FloatField(_('K (wt%)'),
        null=True, blank=True)
    th_ppm = models.FloatField(_('Th (ppm)'),
        null=True, blank=True)
    u_ppm = models.FloatField(_('U (ppm)'),
        null=True, blank=True)

    class Meta:
        # verbose_name_plural = _('heat production')
        # verbose_name = _('heat production')
        db_table = 'heat_production'


