from django.db import models
from django.utils.translation import gettext as _


class CorrectionApplied(models.TextChoices):
    YES = 'yes', _('Yes')
    NO = 'no', _('No')
    MENTIONED = 'mentioned', _('Mentioned in-text but unclear if applied')
