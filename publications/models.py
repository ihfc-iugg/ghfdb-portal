import os, time, re, uuid
from django.db import models
from django.db.models import F, Max, Min, Q, Count, Sum, Func
import bibtexparser as bib
from .widgets import get_author_objects
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django_extensions.db.fields import AutoSlugField
from sortedm2m.fields import SortedManyToManyField
from django.db import IntegrityError

# Create your models here.
class AuthorAbstract(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100,blank=True)
    middle_name = models.CharField(max_length=100,blank=True)
    slug = AutoSlugField(populate_from=['last_name','first_name','middle_name'])

    class Meta:
        abstract=True
        ordering = ['last_name', 'first_name','middle_name']

    def __str__(self):
        name = self.last_name
        if self.first_name:
            name += ', ' + self.first_name[0] + '. '
        if self.middle_name:
            name += self.middle_name[0] + '.'
        return name

    def get_full_name(self):
        """Of the format Jennings, Samuel S"""
        if self.middle_name:
            return '{}, {} {}'.format(self.last_name,self.first_name,self.middle_name[0])
        else:
            return '{}, {}'.format(self.last_name,self.first_name)

    def get_short_name(self):
        """Of the format S. S. Jennings"""
        return '{} {}. {}'.format(self.first_name,self.middle_name,self.last_name)

    def get_reference_display_name(self):
        """ Jennings, SS """
        names = [getattr(self, name)[0] for name in ['first_name','middle_name'] if getattr(self, name)]
        return '{}, {}'.format(self.last_name,''.join(names))

    def get_publications(self):
        return self.publications.all()

    def years_active(self):
        return self.get_publications().aggregate(start=Min('year'),finish=Max('year'),total=Max('year')+1-Min('year'))

class PublicationAbstract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bib_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    type = models.CharField(max_length=100,blank=True)
    year = models.IntegerField(null=True,blank=True)
    title = models.CharField(max_length=200,blank=True)
    authors = SortedManyToManyField("Author",related_name='publications',blank=True)
    doi = models.CharField(blank=True, max_length=200)
    bibtex = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    journal = models.CharField(max_length=250,blank=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract=True

    def __str__(self):
        return self.bib_id

    def save(self, *args, **kwargs):
        authors = None
        if self.bib_id:
            self.bib_id = self.bib_id.strip()
        if self.bibtex:
            authors = self.parse_bibtex()

        self.bibtex = self.bibtex.replace('\n','').replace('\r','').replace(' = ','=')

        # if not self.id:
            # self.id = self.authors.first()
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # pass
            self.bib_id = self.bib_id + 'a'
            super().save(*args, **kwargs)
            
        # if authors:
            # self.authors.add(*authors)

    def display_authors(self):
        authors = [a.get_reference_display_name() for a in self.authors.all()]
        if len(authors) > 2:
            return '{} et. al.'.format(authors[0])
        elif len(authors) == 1:
            return authors[0]
        else:
            return ' & '.join(authors)

    def parse_bibtex(self):
        entry = bib.loads(self.bibtex).entries[0]       
        self.doi = entry.get('doi','')
        self.year = entry.get('year',None)
        self.title = re.sub('[}{]', '', entry.get('title',''))
        self.abstract = entry.get('abstract','')
        self.bib_id = entry.get('ID','').strip()

        if len(self.bib_id) < 4:
            authors = entry.get('author')
            if authors is not None and authors != '':
                new_id = entry.get('author').split(' ')[0] + str(self.year)
                self.bib_id = new_id
            # print(self.bib_id)

            # print(new_id)
            # self.bib_id = new_id

        self.journal = entry.get('journal','')
        self.type = entry.get('ENTRYTYPE','')
        # if self.Meta.author_model:
        return get_author_objects(entry, self.get_author_model())
  
# class Operator(models.Model):
#     name = models.CharField(_("operator"),max_length=150,unique=True)
    
#     def __str__(self):
#         return '{}'.format(self.name)





