from django.db import models
from django.utils.translation import gettext as _


class ConductivitySource(models.TextChoices):
    OUTCROP = 'outcrop samples', _('Outcrop samples')
    CORE = 'core samples', _('Core samples')
    CUTTINGS = 'cutting samples', _('Cutting samples')
    MINERAL_COMP = 'mineral computation', _('Mineral computation')
    WELL_LOG_INTERP = 'well log interpretation', _('Well log interpretation')
    CORE_LOG_INT = 'core-log integration', _('Core-log integration')
    IN_SITU_PROBE = 'in-situ probe', _('In-situ probe')
    OTHER = 'other', _('Other (specify in comments field)')
    NOT_SPECIFIED = 'unspecified', _('Unspecified')
