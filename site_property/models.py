from django.db import models

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