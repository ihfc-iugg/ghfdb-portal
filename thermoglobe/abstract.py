from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

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

    age_min = models.FloatField(blank=True,null=True)
    age_max = models.FloatField(blank=True,null=True)
    age_method = models.CharField(max_length=200,blank=True)

    class Meta:
        abstract=True

# Abstract class for site property measurements
class SiteProperty(models.Model):
    """This is an abstract base class that contains shared fields between the different site measurements. Required to avoid repetition"""

    sample_name = models.CharField(max_length=200,blank=True)
    value = models.FloatField()
    uncertainty = models.FloatField(null=True,blank=True)
    method = models.CharField(max_length=200,blank=True)
    number_of_measurements = models.IntegerField(default=1)

    depth = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.value)

# Abstract class that gives field to both 'HeatFlow' and 'TemperatureGradient'
class IntervalProperty(models.Model):
    # Each Heatflow belongs to a single 'DepthInterval'

    # model fields 
    corrected = models.FloatField(blank=True, null=True)
    corrected_uncertainty = models.FloatField(blank=True, null=True)
    
    uncorrected = models.FloatField(blank=True, null=True)
    uncorrected_uncertainty = models.FloatField(blank=True, null=True)

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