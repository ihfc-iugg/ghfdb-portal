from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from . import choices
from thermoglobe.utils import geologic_age

class SiteProperty(models.Model):
    """This is an abstract base class that contains shared fields between the different site measurements. Required to avoid repetition"""
    ROCK_GROUPS = choices.ROCK_GROUPS
    ROCK_ORIGIN = choices.ROCK_ORIGIN

    sample_name = models.CharField(_("sample name"),
            help_text=_('The reported name of the sample if applicable.'),
            max_length=200,blank=True)
    
    rock_group = models.CharField(_("rock group"),
                help_text=_('The encompassing rock group of the sample.'),
                max_length=2,
                choices=ROCK_GROUPS, 
                blank=True,null=True)
    rock_origin = models.CharField(_("rock origin"),
                help_text=_('The geological origin of the sample.'),
                max_length=2,
                choices=ROCK_ORIGIN, 
                blank=True,null=True)
    rock_type = models.CharField(_("rock type"),
                help_text=_('The reported rock type.'),
                max_length=100, 
                blank=True,null=True)
    
    age = models.FloatField(_("age"),
                help_text=_('The reported age of the sample.'),
                blank=True,null=True)
    age_type = models.CharField(_("age type"),
            help_text=_('The type of age given.'),
            max_length=200,
            blank=True, null=True)

    class Meta:
        abstract = True

    # def __str__(self):
    #     return '{}'.format(self.value)




