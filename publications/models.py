import uuid
from django.db import models
from django.utils.http import urlquote_plus
from django.utils.translation import gettext as _
from string import ascii_uppercase
from django.utils.html import mark_safe
from taggit.managers import TaggableManager
from taggit.utils import _parse_tags
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase
from django.db.models import F, Avg
from django.urls import reverse

class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class PublicationBase(models.Model):
    """Model representing a publication."""

    class Meta:
        app_label = 'publications'
        # ordering = ['-year', 'citekey']
        verbose_name_plural = ' Publications'
        abstract = True
        ordering = [F('year').desc(nulls_last=True),'citekey']

    ENTRYTYPE = models.CharField(max_length=64, blank=True, null=True)
    citekey = models.CharField(max_length=512, blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True)
    author = models.CharField(max_length=2048, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    journal = models.CharField(max_length=256, blank=True)
    booktitle = models.CharField(max_length=256, blank=True)
    url = models.URLField(blank=True, verbose_name='URL')
    doi = models.CharField(max_length=128, verbose_name='DOI', blank=True)
    abstract = models.TextField(blank=True)
    pdf = models.FileField(upload_to='publications/', verbose_name='PDF', blank=True, null=True)
    keywords = TaggableManager(through=UUIDTaggedItem, verbose_name=_('key words'), help_text=None)
    bibtex = models.TextField(blank=True,null=True)

    def __str__(self):

        if self.title:
            if len(self.title) < 64:
                return self.title
            else:
                index = self.title.rfind(' ', 40, 62)

                if index < 0:
                    return self.title[:61] + '...'
                else:
                    return self.title[:index] + '...'
        else:
            return ''


    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


    def _produce_author_lists(self):
        """
        Parse authors string to create lists of authors.
        """

        # post-process author names
        # self.author = self.author.replace(', and ', ', ')
        # self.author = self.author.replace(',and ', ', ')
        # self.author = self.author.replace(' and ', ', ')
        # self.author = self.author.replace(';', ',')

        # list of authors
        self.authors_list = [author.strip() for author in self.author.split(',')]

        # simplified representation of author names
        self.authors_list_simple = []

        # author names represented as a tuple of given and family name
        self.authors_list_split = []

        # tests if title already ends with a punctuation mark
        self.title_ends_with_punct = self.title[-1] in ['.', '!', '?'] \
            if len(self.title) > 0 else False

        suffixes = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', "Jr.", "Sr."]
        prefixes = ['Dr.']
        prepositions = ['van', 'von', 'der', 'de', 'den']

        # further post-process author names
        for i, author in enumerate(self.authors_list):
            if author == '':
                continue

            names = author.split(' ')

            # check if last string contains initials
            if (len(names[-1]) <= 3) \
                and names[-1] not in suffixes \
                and all(c in ascii_uppercase for c in names[-1]):
                # turn "Gauss CF" into "C. F. Gauss"
                names = [c + '.' for c in names[-1]] + names[:-1]

            # number of suffixes
            num_suffixes = 0
            for name in names[::-1]:
                if name in suffixes:
                    num_suffixes += 1
                else:
                    break

            # abbreviate names
            for j, name in enumerate(names[:-1 - num_suffixes]):
                # don't try to abbreviate these
                if j == 0 and name in prefixes:
                    continue
                if j > 0 and name in prepositions:
                    continue

                if (len(name) > 2) or (len(name) and (name[-1] != '.')):
                    k = name.find('-')
                    if 0 < k + 1 < len(name):
                        # take care of dash
                        names[j] = name[0] + '.-' + name[k + 1] + '.'
                    else:
                        names[j] = name[0] + '.'

            if len(names):
                self.authors_list[i] = ' '.join(names)

                # create simplified/normalized representation of author name
                if len(names) > 1:
                    for name in names[0].split('-'):
                        name_simple = self.simplify_name(' '.join([name, names[-1]]))
                        self.authors_list_simple.append(name_simple)
                else:
                    self.authors_list_simple.append(self.simplify_name(names[0]))

                # number of prepositions
                num_prepositions = 0
                for name in names:
                    if name in prepositions:
                        num_prepositions += 1

                # splitting point
                sp = 1 + num_suffixes + num_prepositions
                self.authors_list_split.append(
                    (' '.join(names[:-sp]), ' '.join(names[-sp:])))

        # list of authors in BibTex format
        self.authors_bibtex = ' and '.join(self.authors_list)

        # overwrite authors string
        if len(self.authors_list) > 2:
            self.author = ', and '.join([
                ', '.join(self.authors_list[:-1]),
                self.authors_list[-1]])
        elif len(self.authors_list) > 1:
            self.author = ' and '.join(self.authors_list)
        else:
            self.author = self.authors_list[0]


    def type(self):
        return self.ENTRYTYPE


    def keywords_escaped(self):
        return [(keyword.strip(), urlquote_plus(keyword.strip()))
            for keyword in self.keywords.split(',')]


    def authors_escaped(self):
        return [(author, author.lower().replace(' ', '+')) for author in self.authors_list if author]


    def key(self):
        # this publication's first author
        if self.authors_list:
            author_lastname = self.authors_list[0].split(' ')[-1]

            publications = Publication.objects.filter(
                year=self.year,
                author__icontains=author_lastname)

            # character to append to BibTex key
            char = ord('a')

            # augment character for every publication 'before' this publication
            for publication in publications:
                if publication == self:
                    break

                if publication.authors_list[0].split(' ')[-1] == author_lastname:
                    char += 1

            return self.authors_list[0].split(' ')[-1] + str(self.year) + chr(char)
        return ''


    def title_bibtex(self):
        return self.title.replace('%', r'\%')


    def month_bibtex(self):
        return self.MONTH_BIBTEX.get(self.month, '')


    def month_long(self):
        for month_int, month_str in self.MONTH_CHOICES:
            if month_int == self.month:
                return month_str
        return ''


    def first_author(self):
        return self.authors_list[0]


    def journal_or_book_title(self):
        if self.journal:
            return self.journal
        # else:
        #     return self.book_title


    def first_page(self):
        return self.pages.split('-')[0]


    def last_page(self):
        return self.pages.split('-')[-1]


    def clean(self):
        if not self.citekey:
            self._produce_author_lists()
            self.citekey = self.key()

        # remove unnecessary whitespace
        self.title = self.title.strip()
        self.journal = self.journal.strip()
        self.booktitle = self.booktitle.strip()


    def authors_display_long(self):
        if len(self.authors_list) > 2:
            start = ', '.join(self.authors_list[:-1])
            last = self.authors_list[-1]
            return f'{start} & {last}'
        elif len(self.authors_list) == 1:
            return self.authors_list[0]
        else:
            return ' & '.join(self.authors_list)



    def authors_display(self):
        if len(self.authors_list) > 2:
            return '{} et. al.'.format(self.authors_list[0])
        elif len(self.authors_list) == 1:
            return self.authors_list[0]
        else:
            return ' & '.join(self.authors_list)


    @property
    def authors_list(self):
        if self.author:
            return self.author.split(' and ')
        else:
            return []

    @staticmethod
    def simplify_name(name):
        name = name.lower()
        name = name.replace(u'ä', u'ae')
        name = name.replace(u'ö', u'oe')
        name = name.replace(u'ü', u'ue')
        name = name.replace(u'ß', u'ss')
        return name


class Publication(PublicationBase):
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=128,
        default='User Upload',
        blank=True)
    is_verified = models.BooleanField(_('verified'),default=False)
    verified_by = models.ForeignKey("users.CustomUser",
        related_name='verifications',
        blank=True, null=True, 
        on_delete=models.SET_NULL)
    date_verified = models.DateTimeField(blank=True, null=True)

    _metadata = {
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'authors': 'display_authors',
        'year': 'year',
        }

    class Meta(PublicationBase.Meta):
        db_table = 'publications'

    @property
    def avg_heat_flow(self):
        return self.heatflow_data.aggregate(avg_corrected=Avg('corrected'),avg_uncorrected=Avg('uncorrected'))

    def data_counts(self):
        return {'heat_flow': self.heatflow.count()}

    def get_meta_title(self):
        return '{} | HeatFlow.org'.format(self.cite_key)

    def get_data(self,data_type=None):
        sites = self.sites.all()
        return dict(
            intervals=apps.get_model('thermoglobe','interval').heat_flow.filter(site__in=sites),
            temperature= apps.get_model('thermoglobe','temperature').objects.filter(site__in=sites),
            conductivity= apps.get_model('thermoglobe','conductivity').objects.filter(site__in=sites),
            heat_production= apps.get_model('thermoglobe','heatproduction').objects.filter(site__in=sites),
            )

    def get_absolute_url(self):
        return reverse("publications:detail", kwargs={"pk": self.pk})

    def article(self):
        if self.doi:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(self.doi))
        else:
            return ''

    def file_download(self):
        if self.file:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(self.doi))
        else:
            return ''

    # def bibtex(self):
    #     values = [f'\t{k} = "{getattr(self,k)}",' for k in ['authors','title','year','journal','book_title','publisher','volume','institution','number','pages','month','keywords','doi','url','note','isbn'] if getattr(self,k)]
    #     joiner='\n'
    #     return f"""@{ self.type.bibtex_type }{{{ self.citekey },
    #         {joiner.join(values)}
    #         }}"""