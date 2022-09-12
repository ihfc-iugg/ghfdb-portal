from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DjangoDataciteCreatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_datacite'
    verbose_name = _('DataCite')
    verbose_name_plural = _('DataCite')
