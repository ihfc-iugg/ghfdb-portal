from django.db import models
from django.utils.translation import gettext as _

#------------ SAMPLE GEOLOGY -----------#
class Description(models.Model):
    grain_size = models.FloatField(null=True, blank=True)
    dominant_mineral_phase = models.CharField(max_length=50,blank=True)
    colour = models.CharField(max_length=50,blank=True)
    fabric = models.CharField(max_length=50,blank=True)
    texture = models.CharField(max_length=50,blank=True)

    class Meta:
        db_table = 'sample_description'

    def __str__(self):
        return '{}'.format(self.dominant_mineral_phase)

#------------ SITE GEOLOGY -----------#

# Create your models here.
class AbstractCharRelation(models.Model):
    name = models.CharField(max_length=150,unique=True)
    
    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        abstract=True

class Basin(AbstractCharRelation):
    class Meta:
        db_table = 'basin'

class Formation(AbstractCharRelation):
    class Meta:
        db_table = 'formation'

class TectonicEnvironment(AbstractCharRelation):

    class Meta:
        db_table = 'tectonic_environment'

class GeologicalProvince(AbstractCharRelation):

    class Meta:
        db_table = 'geological_province'

class GeologicalUnit(AbstractCharRelation):

    class Meta:
        db_table = 'geological_unit'

class AbstractFloatRelation(models.Model):
    site = models.ForeignKey('thermoglobe.Site',verbose_name=_("site"),on_delete=models.CASCADE)
    value = models.FloatField(_("value"))
    reference = models.OneToOneField("reference.Reference",
            verbose_name=_("reference"),
            on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.value)

    class Meta:
        abstract=True

class SedimentThickness(AbstractFloatRelation):

    class Meta:
        db_table = 'sediment_thickness'

class CrustalThickness(AbstractFloatRelation):

    class Meta:
        db_table = 'crustal_thickness'

class OutcropDistance(AbstractFloatRelation):

    class Meta:
        db_table = 'outcrop_distance'