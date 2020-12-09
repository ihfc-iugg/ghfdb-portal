from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from PIL import Image, ExifTags
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

# Create your models here.
class CustomUser(AbstractUser):

    def save(self,*args, **kwargs):
        if self.first_name and self.last_name:
            self.username = '{}{}'.format(str(self.first_name).capitalize(),str(self.last_name).capitalize()[0])
        
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.username)

    def full_name(self):
        return '{} {}'.format(self.first_name,self.last_name)

