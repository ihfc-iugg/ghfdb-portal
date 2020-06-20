from django.db import models
from thermoglobe.models import TimeStampAbstract
import os
import time
from django.db.models import F, Max, Min, Q, Count, Sum, Func
import bibtexparser as bib
from pprint import pprint 
from .widgets import get_author_objects
from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from django_extensions.db.fields import AutoSlugField

# Create your models here.
class Author(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100,blank=True)
    middle_name = models.CharField(max_length=100,blank=True)
    slug = AutoSlugField(populate_from='last_name')

    class Meta:
        db_table = 'authors'
        ordering = ['last_name', 'first_name','middle_name']

    @staticmethod
    def autocomplete_search_fields():
        return ("last_name__icontains",) #the fields you want here

    def __str__(self):
        name = self.last_name
        if self.first_name:
            name += ', ' + self.first_name[0] + '. '
        if self.middle_name:
            name += self.middle_name[0] + '.'
        return name

    def slugify_function(self,content):
        name = self.last_name
        if self.first_name:
            name += '-' + self.first_name[0]
        if self.middle_name:
            name += self.middle_name[0]
        return name.lower()

    def save(self, *args, **kwargs):
        if self.pk:
            old = Author.objects.get(id=self.pk)
            for name in ['first','middle']:
                name += '_name'
                if len(getattr(self,name)) < len(getattr(old,name)):
                    setattr(self,name,getattr(old,name))

        super().save(*args, **kwargs)

    def get_publications(self):
        pubs = self.as_first_author.all() | self.as_coauthor.all()
        return pubs.distinct().annotate(
            _sites=Count('sites',distinct=True),
            _heat_flow=Count('heatflow',distinct=True),
            _thermal_gradient=Count('thermalgradient',distinct=True),
            _temperature=Count('temperature',distinct=True),
            _thermal_conductivity=Count('conductivity',distinct=True),
            _heat_generation=Count('heatgeneration',distinct=True),
        )

    def years_active(self):
        return self.get_publications().aggregate(start=Min('year'),finish=Max('year'),total=Max('year')+1-Min('year'))

    def data_counts(self):
        return self.get_publications().aggregate(
            # sites=Sum('_sites'),
            heat_flow=Sum('_heat_flow'),
            thermal_gradient=Sum('_thermal_gradient'),
            temperature=Sum('_temperature'),
            thermal_conductivity=Sum('_thermal_conductivity'),
            heat_generation=Sum('_heat_generation'),
        )

class Reference(TimeStampAbstract):
    entry_type = models.CharField(max_length=100,blank=True)
    year = models.IntegerField(null=True,blank=True)
    title = models.CharField(max_length=200,blank=True)
    first_author = models.ForeignKey(Author, related_name='as_first_author', blank=True, null=True, on_delete=models.PROTECT)
    co_authors = models.ManyToManyField(Author,related_name='as_coauthor',blank=True)
    doi = models.CharField(blank=True, max_length=200)
    bibtex = models.TextField(blank=True)
    bib_id = models.CharField(max_length=100,unique=True,blank=True)
    abstract = models.TextField(blank=True)
    journal = models.CharField(max_length=250,blank=True)
    source = models.CharField(max_length=100,
    default='User Upload',
    blank=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='bib_id')

    class Meta:
        db_table = 'references'
        ordering = [F('year').desc(nulls_last=True)]
        unique_together = ['first_author','year','bib_id']

    def __str__(self):
        return '{}'.format(self.bib_id)

    def save(self, *args, **kwargs):
        if self.bibtex:
            self.parse_bibtex()

        super().save(*args, **kwargs)

    def parse_bibtex(self):
        entry = bib.loads(self.bibtex).entries[0]

        self.doi = entry.get('doi','')
        self.year = entry.get('year',None)
        self.title = entry.get('title','')
        self.abstract = entry.get('abstract','')

        self.bib_id = entry.get('ID','')
        self.journal = entry.get('journal','')
        self.entry_type = entry.get('ENTRYTYPE','')

        authors = get_author_objects(entry, Author)
        if authors:
            self.first_author = authors[0]

            if len(authors) > 1:
                self.co_authors_list = authors[1:]
            else:
                self.co_authors_list = None

    @property
    def _co_authors(self):
        return ', '.join([str(author) for author in self.co_authors.all()])

    @staticmethod
    def autocomplete_search_fields():
        return ("first_author__last_name__icontains", "year__exact")

    def get_reference_dict(self):
        if self.bibtex:
            fields = ['author','title','year','journal','doi','abstract']
            reference = bib.loads(self.bibtex).entries[0]
            if reference.get('author',False):
                author_list = reference.get('author').split(' and ') 
                reference['author'] = '{} and {}'.format(', '.join(author_list[:-1]),author_list[-1])
            return reference

    @property
    def avg_heat_flow(self):
        return self.heatflow_data.aggregate(avg_corrected=Avg('corrected'),avg_uncorrected=Avg('uncorrected'))
        
    def data_counts(self):
        return {
            'heat_flow': self.heatflow.count()
        }
        # return self.aggregate(
        #     # sites=Sum('_sites'),
        #     heat_flow=Sum('heatflow'),
        #     thermal_gradient=Sum('thermalgradient'),
        #     _temperature=Sum('temperature'),
        #     thermal_conductivity=Sum('conductivity'),
        #     heat_generation=Sum('heatgeneration'),
        # )

class Operator(models.Model):
    name = models.CharField(_("operator"),max_length=150,unique=True)
    
    def __str__(self):
        return '{}'.format(self.name)

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
    imported_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)
    date_imported = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Upload'
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.data.name



