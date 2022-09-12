from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MappingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mapping'
    verbose_name = _('Mapping')
    verbose_name_plural = _('Mapping')
