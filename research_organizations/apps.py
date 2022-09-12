from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResearchOrganizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'research_organizations'
    vebose_name = _('Research Organization')
    vebose_name_plural = _('Research Organizations')
