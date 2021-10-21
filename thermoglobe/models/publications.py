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
import bibtexparser.customization as custom
from itertools import chain
from collections import Counter
from sortedm2m.fields import SortedManyToManyField
from django.apps import apps
import plotly.graph_objects as go
from django.utils.html import mark_safe
from .querysets import options

def getnames(names):
    """Convert people names as surname, firstnames
    or surname, initials.

    :param names: a list of names
    :type names: list
    :returns: list -- Correctly formated names

    .. Note::
        This function is known to be too simple to handle properly
        the complex rules. We would like to enhance this in forthcoming
        releases.
    """
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        else:
            namesplit = namestring.split()
            last = namesplit.pop()
            firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()

        prefixes = ['von', 'ben', 'van', 'der', 'de', 'la', 'le']
        
        for item in firsts:
            if item.lower() in prefixes:
                last = firsts.pop().lower() + ' ' + last
        if len(last.split(' ')) > 1:
            tmp = []
            for item in last.split(' '):
                if item.lower() in prefixes:
                    tmp.append(item.lower())
                else:
                    tmp.append(item)
            last = ' '.join(tmp)

        tidynames.append(last + ", " + ' '.join(firsts))
    return tidynames

def get_author_list(entry_dict):
    """
    Split author field into a list of "Name, Surname".

    :param entry_dict: the record.
    :returns: list of dicts containing author information. returns empty list if no author information is present

    """
    if "author" in entry_dict:

        if entry_dict["author"]:
            # remove these characters from the author entry for consistency
            for char in ['{','}','.']:
                entry_dict['author'] = entry_dict['author'].replace(char,'')

            # entry_dict['author'] = entry_dict['author'].replace('Von','von')

            author_list = getnames([i.strip() for i in entry_dict["author"].replace('\n', ' ').split(" and ")])
            authors = []
            for name in author_list:
                # split the current author into first, middle and last names
                name = custom.splitname(name, strict_mode=False)
                # append to author list
                # if name['von']
                first = name['first']
                if first:
                    first = first[0]
                
                middle = ''
                if len(name['first']) > 1:
                    middle = ' '.join(name['first'][1:])

                last = name['last'][0]
                if name['von']:
                    last = name['von'][0] + ' ' +  last

                authors.append({
                    'first_name': first,
                    'middle_name': middle,
                    'last_name': last
                })

            return authors
        else:
            del entry_dict["author"]
            return []

def get_author_objects(entry_dict):
    model = apps.get_model('thermoglobe','author')
    authors = get_author_list(entry_dict)
    if not authors:
        return
    author_list = []
    for author in authors:
        try:
            author_list.append(model.objects.update_or_create(last_name=author['last_name'],defaults=author)[0])
        except model.MultipleObjectsReturned:
            try: 
                author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                    first_name__startswith=author['first_name'][0],
                                                                    defaults=author)[0])
            except model.MultipleObjectsReturned:
                try:
                    author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                        first_name=author['first_name'],
                                                                        defaults=author)[0])
                except model.MultipleObjectsReturned:

                    try:
                        author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                            first_name=author['first_name'],
                                                                            middle_name__startswith=author['middle_name'][0],
                                                                            defaults=author)[0])

                    except model.MultipleObjectsReturned:
                        raise ValueError('Found more than one author by the name {} {}. Please double check'.format(author['last_name'],author['first_name'][0]))

    return author_list

def pdf_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'publications/{instance.bib_id} - {instance.title}'[:100]

class PublicationeQS(models.QuerySet):

    def histogram(self):
        data = (
            self.exclude(bibtex='')
            .values_list('year',flat=True)      
        )
        fig = go.Figure(go.Histogram(
                x = list(data),
            ))
        fig.update_layout(dict(
            yaxis_title="Count",
            xaxis_title="Year published",
            margin={"r":0,"t":0,"l":0,"b":0}
        ))
        return mark_safe(fig.to_html(**options('publicationss_histogram')))

class Author(ModelMeta,models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100,blank=True)
    middle_name = models.CharField(max_length=100,blank=True)
    slug = AutoSlugField(populate_from=['last_name','first_name','middle_name'])
    _metadata = {
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'author':'get_name',
        }
    date_added = models.DateTimeField(_('date added to ThermoGlobe'),
            auto_now_add=True,
        )
    class Meta:
        ordering = ['last_name', 'first_name','middle_name']
        db_table = 'authors'

    def __str__(self):
        name = self.last_name
        if self.first_name:
            name += ', ' + self.first_name[0] + '. '
        if self.middle_name:
            name += self.middle_name[0] + '.'
        return name

    def get_name(self):
        """Of the format Samuel Jennings"""
        return f'{self.first_name} {self.last_name}'

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

    @staticmethod
    def autocomplete_search_fields():
        return ("last_name__icontains",) #the fields you want here

    def data_counts(self):
        return self.get_publications().aggregate(
            heat_flow=Sum('_heat_flow'),
            thermal_gradient=Sum('_thermal_gradient'),
            temperature=Sum('_temperature'),
            thermal_conductivity=Sum('_thermal_conductivity'),
            heat_generation=Sum('_heat_generation'),
        )

    def get_meta_title(self):
        return f'{self.get_full_name()} | HeatFlow.org'

    def get_absolute_url(self):
        return reverse("publications:author_details", kwargs={"slug": self.slug})

    def total_sites(self):
        return self.get_publications().aggregate(Count('sites',distinct=True))

    def sites(self):
        return apps.get_model('thermoglobe','site').objects.filter(reference__in=self.get_publications()).distinct()

    def as_first_author(self):
        """Returns the number of publications where the current author is listed as first author""" 
        return list(self.publications.through.objects.filter(author=self).values_list('sort_value',flat=True)).count(1)
    
    def as_co_author(self):
        """Returns the number of publications where the current author is listed as a co-author""" 
        return self.get_publications().count() - self.as_first_author()

    def related_authors(self):
        authors = self._meta.model.objects.none()
        for pub in self.get_publications():
            authors = authors | pub.authors.all()

        return Counter(list(authors.exclude(id=self.id))).most_common()[:5]

    def get_data(self):
        return {
            'intervals' : apps.get_model('thermoglobe','interval').heat_flow.filter(reference__in=self.get_publications()),
            'temperature': apps.get_model('thermoglobe','temperature').objects.filter(reference__in=self.get_publications()),
            'conductivity': apps.get_model('thermoglobe','conductivity').objects.filter(reference__in=self.get_publications()),
            'heat_generation': apps.get_model('thermoglobe','heatgeneration').objects.filter(reference__in=self.get_publications()),
        }         

    def get_meta_description(self):
        return f"Get access to all heat flow and thermal data published by {self.get_name()} on ThermoGlobe"

class Publication(ModelMeta,models.Model):
    objects = PublicationeQS.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bib_id = models.CharField(max_length=128, unique=True, blank=True, null=True)
    type = models.CharField(max_length=128,blank=True)
    year = models.IntegerField(null=True,blank=True)
    title = models.CharField(max_length=512,blank=True)
    authors = SortedManyToManyField("Author",related_name='publications',blank=True)
    doi = models.CharField(blank=True, max_length=128)
    bibtex = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    journal = models.CharField(max_length=256,blank=True)
    added = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from=['id','title'])
    source = models.CharField(max_length=128,
        default='User Upload',
        blank=True)
    is_verified = models.BooleanField(_('verified'),default=False)
    verified_by = models.ForeignKey("users.CustomUser",
        related_name='verifications',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    date_verified = models.DateTimeField(blank=True, null=True)

    file = models.FileField(_("file"),
        upload_to=pdf_path,
        null=True,
        blank=True,
    )
    date_added = models.DateTimeField(_('date added to ThermoGlobe'),
            auto_now_add=True,
        )

    history = HistoricalRecords()
    _metadata = {
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'authors': 'display_authors',
        'year': 'year',
        }

    class Meta:
        db_table = 'publications'
        ordering = [F('year').desc(nulls_last=True),'bib_id']

    def __str__(self):
        return f"{self.bib_id}"

    def save(self, *args, **kwargs):
        authors = None
        if self.bib_id:
            self.bib_id = self.bib_id.strip()
        if self.bibtex:
            authors = self.parse_bibtex()

        self.bibtex = self.bibtex.replace('\n','').replace('\r','').replace(' = ','=')

        super().save(*args, **kwargs)
            
        if authors:
            self.authors.add(*authors)

    def display_authors(self):
        authors = [a.get_reference_display_name() for a in self.authors.all()]
        if len(authors) > 2:
            return '{} et. al.'.format(authors[0])
        elif len(authors) == 1:
            return authors[0]
        else:
            return ' & '.join(authors)

    def author_last_names(self):
        return ", ".join([a.last_name for a in self.authors.all()])

    def parse_bibtex(self):
        entry = self.get_bibtex_entry()
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

        self.journal = entry.get('journal','')
        self.type = entry.get('ENTRYTYPE','')
        return get_author_objects(entry)
  
    def get_bibtex_entry(self,bibtex=None):
        if bibtex:
            entry = bib.loads(bibtex).entries
        else:
            entry = bib.loads(self.bibtex).entries
        # malformed or non-existent bibtex entries will return none
        if not entry:
            return []
        else:
            return entry[0]  

    @property
    def avg_heat_flow(self):
        return self.heatflow_data.aggregate(avg_corrected=Avg('corrected'),avg_uncorrected=Avg('uncorrected'))

    def data_counts(self):
        return {
            'heat_flow': self.heatflow.count()
        }

    def get_meta_title(self):
        return '{} | HeatFlow.org'.format(self.bib_id)

    def get_data(self,data_type=None):
        sites = self.sites.all()
        return dict(
            intervals=apps.get_model('thermoglobe','interval').heat_flow.filter(site__in=sites),
            temperature= apps.get_model('thermoglobe','temperature').objects.filter(site__in=sites),
            conductivity= apps.get_model('thermoglobe','conductivity').objects.filter(site__in=sites),
            heat_generation= apps.get_model('thermoglobe','heatgeneration').objects.filter(site__in=sites),
            )

    def get_absolute_url(self):
        return reverse("thermoglobe:publication_details", kwargs={"slug": self.slug})
    
    def get_meta_description(self):
        return f"Get access to all data from the publication {self.title} by {self.authors.first().get_full_name()} on ThermoGlobe"