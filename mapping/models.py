from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gismodels
# import reverse_geocoder as rg
from django_countries.fields import CountryField

# class Location(models.Model):

#     location = models.CharField(max_length=150,blank=True,null=True)
#     country = CountryField(blank=True,null=True)
#     admin1 = models.CharField(max_length=150,blank=True,null=True)
#     admin2 = models.CharField(max_length=150,blank=True,null=True)

#     class Meta:
#         db_table = 'Locations'

# Create your models here.
class SiteAbstract(models.Model):

    site_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    geom = gismodels.PointField(blank=True)
    elevation = models.FloatField(blank=True, null=True)
    # location = models.ForeignKey(Location,null=True,blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract=True

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.geom = Point(float(self.longitude),float(self.latitude))
            # loc = rg.search((self.latitude,self.longitude))[0]
            # loc['country'] = loc['cc']
            # loc['']
            # print(loc)

            # self.location = Location.objects.get_or_create(**loc)
        super().save(*args, **kwargs)