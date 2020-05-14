from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from . import choices
from geomodels.utils import geologic_age
# Abstract models
class TimeStampAbstract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.CharField(max_length=150,blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=150,blank=True,null=True)
    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.OneToOneField("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

class AgeAbstract(models.Model):

    age_min = models.FloatField(_("minimum age"),
            blank=True,null=True)
    age_max = models.FloatField(_("maximum age"),
            blank=True,null=True)
    age_method = models.CharField(_("age method"),
            max_length=200,
            blank=True, null=True)
    tectonothermal_min = models.CharField(_("minimum thermo-tectonic age"),
            max_length=150, 
            blank=True, null=True)
    tectonothermal_max = models.CharField(_("maximum thermo-tectonic age"),
		max_length=150, 
		blank=True, null=True)
    juvenile_age_min = models.CharField(_("minimum juvenile age"),
            max_length=150, 
            blank=True, null=True)
    juvenile_age_max = models.CharField(_("minimum juvenile age"),
            max_length=150, 
            blank=True, null=True)

    class Meta:
        abstract=True

    def age(self):
        if self.age_min == self.age_max:
            return self.age_min
        else:
            return '{}-{}'.format(self.age_min,self.age_max)
        
    def tectonothermal_age(self):
        if self.tectonothermal_min == self.tectonothermal_max:
            return self.tectonothermal_min
        else:
            return '{}-{}'.format(self.tectonothermal_min,self.tectonothermal_max)

    def juvenile_age(self):
        if self.juvenile_age_min == self.juvenile_age_max:
            return self.juvenile_age_min
        else:
            return '{}-{}'.format(self.juvenile_age_min,self.juvenile_age_max)

    def strat_age(self):
        # returns an ordered dict containing stratigraphic age info.
        return geologic_age([self.age_min,self.age_max])

class Measurements(TimeStampAbstract):
    reference = models.ForeignKey("reference.Reference",
                verbose_name=("reference"),
                blank=True,null=True, 
                on_delete=models.CASCADE)
    comment = models.TextField(_("comment"),
            blank=True,null=True)
    source = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        abstract=True

class SiteProperty(Measurements):
    """This is an abstract base class that contains shared fields between the different site measurements. Required to avoid repetition"""
    ROCK_GROUPS = choices.ROCK_GROUPS
    ROCK_ORIGIN = choices.ROCK_ORIGIN

    sample_name = models.CharField(_("sample name"),
            max_length=200,blank=True)
    value = models.FloatField(_("value"))
    uncertainty = models.FloatField(_("uncertainty"),
            null=True,blank=True)
    method = models.CharField(_("method"),
            max_length=200,blank=True)
    depth = models.FloatField(_("depth"),
            blank=True, null=True)
    
    rock_group = models.CharField(_("rock group"),
                max_length=2,
                choices=ROCK_GROUPS, 
                blank=True,null=True)
    rock_origin = models.CharField(_("rock origin"),
                max_length=2,
                choices=ROCK_ORIGIN, 
                blank=True,null=True)
    rock_type = models.CharField(_("rock type"),
                max_length=100, 
                blank=True,null=True)
    geo_unit = models.ForeignKey("geomodels.GeologicalUnit",
            verbose_name=_("geological unit"),
            blank=True,null=True,
            on_delete=models.SET_NULL)
    
    age = models.FloatField(_("age"),
                blank=True,null=True)
    age_min = models.FloatField(_("minimum age"),
            blank=True,null=True)
    age_max = models.FloatField(_("maximum age"),
            blank=True,null=True)
    age_method = models.CharField(_("age method"),
            max_length=200,
            blank=True, null=True)

    is_core = models.BooleanField(_("is drill core"),default=False)


    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.value)

class IntervalProperty(Measurements):

    depth_min = models.FloatField(_("minimum depth"),
            blank=True,null=True)
    depth_max = models.FloatField(_("maximum depth"),
            blank=True,null=True)
    corrected = models.FloatField(_("corrected value"),
            blank=True, null=True)
    corrected_uncertainty = models.FloatField(_("corrected uncertainty"),  
            blank=True, null=True)
    uncorrected = models.FloatField(_("uncorrected value"),
            blank=True, null=True)
    uncorrected_uncertainty = models.FloatField(_("uncorrected uncertainty"),
            blank=True, null=True)
    number_of_temperatures = models.IntegerField(_("number of temperatures"), 
            blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.corrected:
            if self.corrected_uncertainty:
                return '{} ({})'.format(self.corrected,self.corrected_uncertainty)
            else:
                return '{}'.format(self.corrected)
        else:
            if self.uncorrected_uncertainty:
                return '{} ({})'.format(self.uncorrected,self.uncorrected_uncertainty)
            else:
                return '{}'.format(self.uncorrected)

    def clean(self):
        if not self.corrected and not self.uncorrected:
            raise ValidationError(
                _('{} entries must contain either a corrected or uncorrected heat flow value.'.format(
                    self._meta.verbose_name.title())), code='invalid') 
        super().clean()

    def is_corrected(self,obj):
        return True if self.corrected else False
    is_corrected.boolean = True