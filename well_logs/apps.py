from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WellLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'well_logs'
    verbose_name = _('Well Logs')
    verbose_name_plural = _('Well Logs')
