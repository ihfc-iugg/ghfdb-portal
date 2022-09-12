from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext as _
from datetime import datetime
from .utils import ISO_LANGUAGES

def current_year():
    return datetime.now().year


class Right(models.Model):
    name = models.CharField(_('name'), max_length=32)
    about = models.TextField(_('about'))
    snippet = models.TextField(_('html snippet'),)

    def __str__(self):
        return self.name


class Subject(MP_Node):
    mapping = {
            'provided_id' : 'id',
            'name' : 'name',
            'keyword' : 'keyword',
            'help' : 'qtip',
        }
    
    provided_id = models.CharField(_('provided ID'), max_length=128)
    name = models.CharField(_('name'), max_length=128)
    
    keyword = models.CharField(_('keyword'), max_length=128,
        null=True, blank=True)
    help = models.TextField(_('additional information'),
        null=True, blank=True)


    def __str__(self):
        return self.name


class Schema(models.Model):
    title = models.CharField(max_length=32, blank=True)
    description = models.TextField(null=True, blank=True)
    schema = models.JSONField()
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-title', ]


class Configuration(SingletonModel):

    # Allows admin to set a default value for the publisher field
    publisher = models.CharField(_('Publisher'), max_length=256,
        help_text=_('Name of the publisher. This value will be sent with all forms submitted to Datacite via this application.')
        )

    # will need to handle having a NULL schema value
    schema = models.OneToOneField(Schema, on_delete=models.SET_NULL, null=True, blank=True)

    # allows admin to set default subjects to be included with all submissions
    subjects = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)


    # set a default resource type 
    resourceTypeGeneral = models.CharField(max_length=256,
        help_text=_('By setting this option, you can limit submissions through this application to a single resource type.')
        )


    # show (True) or hide (False) the lang fields on all forms
    show_lang_fields = models.BooleanField(default=True)



    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configuration")
    
    def __str__(self):
        return "Configuration"


class Submission(models.Model):
    publisher = models.CharField(_('Publisher'), 
        max_length=256, 
        # default=DataCiteOptions.objects.first().publisher
        )
    publicationYear = models.PositiveSmallIntegerField(_('Publication Year'), 
            help_text=_('The year when the data was or will be made publicly available. In the case of resources such as software or dynamic data where there may be multiple releases in one year, include the Date/dateType/ dateInformation property and sub-properties to provide more information  about the publication or release date details.'),
            default=current_year)
    language = models.CharField(choices=ISO_LANGUAGES, max_length=256, help_text=_('Primary language of the resource'))
    version = models.CharField(max_length=4, default="1.0")
    schemaVersion = models.CharField(max_length=4)
    resourceTypeGeneral = models.CharField(max_length=256)
    resourceType = models.CharField(_('Title'), max_length=256,)

    rightsList = models.ManyToManyField(Right, verbose_name=_('Rights/Licensing'))