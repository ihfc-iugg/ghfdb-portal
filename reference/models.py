from django.db import models
from main.models import TimeStampAbstract

# Create your models here.
class Author(models.Model):
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200,blank=True)

    class Meta:
        db_table = 'authors'

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
    source = models.CharField(blank=True, max_length=200)

    class Meta:
        db_table = 'references'

    def __str__(self):
        return '{}'.format(self.reference)

    @property
    def reference(self):
        if self.year:
            return '{}{}'.format(self.first_author.last_name,self.year)
        else:
            return '{}'.format(self.first_author.last_name)

    @property
    def co_authors_display(self):
        return ', '.join([author.last_name for author in self.co_authors.all()])

    @property
    def site_count(self):
        return Count("site",distinct=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("first_author__last_name__icontains", "year__exact")
