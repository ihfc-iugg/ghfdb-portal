from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.utils.safestring import mark_safe
from PIL import Image, ExifTags
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

# Create your models here.
class CustomUser(AbstractUser):
    TITLES_CHOICES = [
    ('MR', 'Mr'),
    ('MS', 'Ms'),
    ('MRS', 'Mrs'),
    ('DR', 'Dr'),
    ]
    title = models.CharField(
        max_length=3,
        choices=TITLES_CHOICES,
        
    )
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    address3 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.IntegerField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_image', blank=True)
    bio = models.TextField(blank=True,null=True)

    def save(self,*args, **kwargs):
        if self.first_name and self.last_name:
            self.username = '{}{}'.format(str(self.first_name).capitalize(),str(self.last_name).capitalize()[0])
        
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.username)

    def image_tag(self):
        from django.utils.html import escape
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))

    image_tag.short_description = 'Image'



# def rotate_image(filepath):
#     print('Rotating image')
#     try:
#         image = Image.open(filepath)
#         # image = image.rotate(270)
#         image = image.transpose(Image.ROTATE_270)
#         image.save(filepath)
#         image.close()
#     except (AttributeError, KeyError, IndexError):
#         # cases: image don't have getexif
#         pass





# @receiver(post_save, sender=CustomUser, dispatch_uid="update_image_profile")
# def update_image(sender, instance, **kwargs):
#   if instance.image:
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     fullpath = BASE_DIR + instance.image.url
#     rotate_image(fullpath)