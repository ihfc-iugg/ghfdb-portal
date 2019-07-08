from django.db import models
# from .choices import ROCK_GROUPS, ROCK_ORIGIN

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

class Lithology(models.Model):
    lithology = models.CharField(max_length=150,unique=True)

    class Meta:
        db_table = 'lithology'

    def __str__(self):
        return self.lithology

class GeoModelSample(models.Model):
    ROCK_GROUPS = ( ('metamorphic','Metamorphic'),
                    ('igneous','Igneous'),
                    ('sedimentary','Sedimentary'),
                    ('metaigneous','Meta-Igneous'),
                    ('metasedimentary','Meta-Sedimentary'),)
    ROCK_ORIGIN = ( ('plutonic','Plutonic'),
                    ('volcanic','Volcanic'),)
    
    lithology = models.ForeignKey(Lithology,blank=True, null=True, on_delete=models.SET_NULL)
    rock_group = models.CharField(max_length=15,choices=ROCK_GROUPS, blank=True)
    rock_origin = models.CharField(max_length=8,choices=ROCK_ORIGIN, blank=True)
    description = models.ForeignKey(Description,blank=True,null=True,on_delete=models.SET_NULL)

    class Meta:
        abstract = True
#------------ SITE GEOLOGY -----------#

class Basin(models.Model):
    basin = models.CharField(max_length=100,unique=True)

    class Meta:
        db_table = 'geological_basin'

    def __str__(self):
        return '{}'.format(self.basin)

class Formation(models.Model):
    formation = models.CharField(max_length=100,unique=True)

    class Meta:
        db_table = 'geological_formation'

    def __str__(self):
        return '{}'.format(self.formation)

class TectonicEnvironment(models.Model):
    tectonic_environment = models.CharField(max_length=100,unique=True)

    class Meta:
        db_table = 'tectonic_environment'

    def __str__(self):
        return '{}'.format(self.tectonic_environment)

class Province(models.Model):
    province = models.CharField(max_length=100,unique=True)

    class Meta:
        db_table = 'geological_province'

    def __str__(self):
        return '{}'.format(self.province)

class Domain(models.Model):
    domain = models.CharField(max_length=100,unique=True)

    class Meta:
        db_table = 'geological_domain'

    def __str__(self):
        return '{}'.format(self.domain)



# class SuperEon(models.Model):
#     SUPEREON = (('precambrian','Precambrian'))
#     name = models.CharField(max_length=11,choices=SUPEREON)

# class Eon(models.Model):
#     EON = (('precambrian','Precambrian'))
#     name = models.CharField(max_length=11,choices=EON)



# class Geochronology(models.Model):
#     supereon
#     eon
