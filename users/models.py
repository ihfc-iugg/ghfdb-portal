from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
# Create your models here.
class CustomUser(AbstractUser):

    university = models.CharField(max_length=200, blank=True, null=True)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.IntegerField(null=True, blank=True)
    country = CountryField(null=True, blank=True)

    def save(self,*args, **kwargs):
        if self.first_name and self.last_name:
            self.username = '{}{}'.format(str(self.first_name).capitalize(),str(self.last_name).capitalize()[0])
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.username)