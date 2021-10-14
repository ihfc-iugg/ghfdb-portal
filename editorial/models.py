from django.db import models
from cms.models.pluginmodel import CMSPlugin
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
# from publications.models import Publication

class Section(CMSPlugin):
    placement_choices = (
        ('top','Top'),
        ('left','Left'),
        ('right','Right'),
    )
    section_id = models.CharField(max_length=32, null=True, blank=True)
    image = FilerImageField(on_delete=models.SET_NULL,null=True,blank=True)
    image_placement  = models.CharField(choices=placement_choices,max_length=5,null=True,default='r')

class Heading(CMSPlugin):
    heading = models.CharField(max_length=256)
    sub_heading = models.TextField(null=True, blank=True)

class Image(CMSPlugin):
    placement_choices = (
        ('top','Top'),
        ('left','Left'),
        ('right','Right'),
    )
    image = FilerImageField(on_delete=models.SET_NULL,null=True,blank=True)
    image_placement  = models.CharField(choices=placement_choices,max_length=5,null=True,default='r')

class Feature(CMSPlugin):
    heading = models.CharField(max_length=256)
    content = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=64)
    
class PageHeading(CMSPlugin):
    title = models.CharField(max_length=128)
    sub_title = models.CharField(max_length=256, null=True, blank=True)

# class PublicationPlugin(CMSPlugin):
    # publication = models.ForeignKey("publications.Publication",on_delete=models.SET_NULL)