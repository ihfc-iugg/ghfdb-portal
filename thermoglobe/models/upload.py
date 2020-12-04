import time, os, uuid, re
from django.db import models
from django.db.models import F, Q, Avg, Count, Case, When, Value, Sum, Max, Min
from django.utils.translation import gettext as _
from django.urls import reverse
from thermoglobe import choices
from django_extensions.db.fields import AutoSlugField
from meta.models import ModelMeta
from simple_history.models import HistoricalRecords
import bibtexparser as bib
from itertools import chain
from collections import Counter
from sortedm2m.fields import SortedManyToManyField

def file_storage_path(instance, filename):
    path = 'data/{}'.format(time.strftime("%Y/%m/"))
    name = '{}_{}.{}'.format(instance.last_name,instance.first_name,filename.split('.')[1])
    return os.path.join(path, name)


class Upload(models.Model):
    data_choices = (
        (0,'Heat Flow'),
        (1,'Thermal Gradient'),
        (2,'Temperature'),
        (3,'Thermal Conductivity'),
        (4,'Heat Generation'),
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    data_type = models.IntegerField(choices=data_choices,default=0)
    data = models.FileField(upload_to=file_storage_path)
    bibtex = models.TextField(blank=True, null=True)

    date_uploaded = models.DateTimeField(auto_now_add=True)
    imported = models.BooleanField(default=False)
    date_imported = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Upload'
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.data.name