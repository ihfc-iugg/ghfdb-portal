from django.db import models
from thermoglobe.models import TimeStampAbstract
import os
import time
from django.db.models import F
import bibtexparser as bib
from pprint import pprint 
from .widgets import get_authors

# Create your models here.
class Author(models.Model):
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200,blank=True)

    class Meta:
        db_table = 'authors'
        ordering = ['last_name', 'first_name']

    @staticmethod
    def autocomplete_search_fields():
        return ("last_name__icontains",) #the fields you want here

    def __str__(self):
        if self.first_name:
            return '{}, {}'.format(self.last_name,self.first_name[0])
        else:
            return '{}'.format(self.last_name)

class Reference(TimeStampAbstract):
    first_author = models.ForeignKey(Author, related_name='first_author', blank=True, null=True, on_delete=models.PROTECT)
    co_authors = models.ManyToManyField(Author,related_name='co_authors',blank=True)
    title = models.CharField(max_length=200,blank=True)
    year = models.IntegerField(null=True,blank=True)
    doi = models.CharField(blank=True, max_length=200)
    bibtex = models.TextField(blank=True)
    bib_id = models.CharField(max_length=100,blank=True)
    abstract = models.TextField(blank=True)
    journal = models.CharField(max_length=250,blank=True)

    class Meta:
        db_table = 'references'
        ordering = [F('year').desc(nulls_last=True)]

    def __str__(self):
        return '{}'.format(self.reference)

    def save(self, *args, **kwargs):
        if self.bibtex:
            self.parse_bibtex()

        super().save(*args, **kwargs)

    def parse_bibtex(self):
        bib_obj = bib.loads(self.bibtex).entries[0]

        self.doi = bib_obj.get('doi','')
        self.year = bib_obj.get('year',None)
        self.title = bib_obj.get('title','')
        self.abstract = bib_obj.get('abstract','')
        self.bib_id = bib_obj.get('ID','')
        self.journal = bib_obj.get('journal','')

        authors = get_authors(bib_obj.get('author',None), Author)
        if authors:
            self.first_author = authors[0]

    @property
    def reference(self):
        if self.bib_id:
            return self.bib_id
        elif self.year:
            return '{}{}'.format(self.first_author.last_name,self.year)
        else:
            return '{}'.format(self.first_author.last_name)

    @property
    def _co_authors(self):
        return ', '.join([author.last_name for author in self.co_authors.all()])

    @property
    def site_count(self):
        return Count("site",distinct=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("first_author__last_name__icontains", "year__exact")



def file_storage_path(instance, filename):
    path = 'data/{}'.format(time.strftime("%Y/%m/"))
    name = '{}_{}.{}'.format(instance.last_name,instance.first_name,filename.split('.')[1])
    return os.path.join(path, name)

class FileStorage(models.Model):

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)

    data = models.FileField(upload_to=file_storage_path)
    description = models.TextField(blank=True, null=True)

    date_uploaded = models.DateTimeField(auto_now_add=True)

    added = models.BooleanField(default=False)
    added_by = models.OneToOneField("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)
    date_added = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.data.name



