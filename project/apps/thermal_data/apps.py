from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ThermalDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thermal_data'
    verbose_name = _('Thermal Data')
    verbose_name_plural = _('Thermal Data')
