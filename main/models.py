from django.db import models
from django.utils.translation import gettext as _
from ckeditor.fields import RichTextField

# Create your models here.
class Page(models.Model):

    heading = models.CharField(_("heading"),
            help_text=_("The heading on the page."),
            max_length=150)
    sub_heading = models.CharField(_("sub heading"),
            help_text=_("Appears as a sub heading under the main heading. Slightly smaller font."),
            max_length=250,
            null=True,blank=True)
    content = RichTextField(_("content"),
            help_text=_("Page content that appears underneath the headings."),
            blank=True,null=True)
    title = models.CharField(_("title"),
            help_text=_('Appears in the browser tab before "| HeatFlow.org". If blank, heading will be used instead.'),
            max_length=50,
            blank=True, null=True)
    keywords = models.CharField(_("keywords"),
            help_text=_("Keywords to include in the page <head> tags"),
            max_length=250)
    description = models.TextField(_("decsription"),
            help_text=_("Description to include in the page <head> tags"),
            blank=True,null=True)

    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['id',]

class Field(models.Model):

    table_choices = [
        ('S','Site'),
        ('I','Interval'),
        ('C','Corrections'),
        ('T','Temperature'),
        ('TC','Thermal Conductivity'),
        ('HG','Heat Generation'),
    ]

    table = models.CharField(_('database table'),
        max_length=2,
        choices=table_choices,
        help_text=_("The database table to which this measurement belongs"),
        )
    field_name = models.CharField(_("DB field name"),
            max_length=128,
            help_text='This is how the field should appear in any download files.')
    verbose_field_name = models.CharField(_("field"),
            max_length=128,
            help_text='A verbose version of the field name')
    description = RichTextField(_("field description"),
            help_text='A description of the field')
    units = models.CharField(_("units"),
            max_length=32,
            null=True, blank=True,
            help_text='Standard unit of measurement. Can be written in LaTex format by surrounding units with \\\( latex here \\\).')
    required = models.BooleanField(_('required field'),
        help_text=_('Is the field required during upload of data into this table'),
        default=False,
    )
    download_only = models.BooleanField(_('download only'),
        help_text=_('This should be set to true if it is avaliable but users cannot supply data for it. Reserverd for fields calculated by the application.'),
        default=False,
    )

    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-table','-required','download_only','field_name',]

    def __str__(self):
        return f"{self.table} - {self.field_name}"

class FAQ(models.Model):
    question = models.CharField(_("question"),
            max_length=100,
            help_text='Input the question here.')
    answer = RichTextField(_("answer"),
            help_text='The answer to the question.')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'FAQ'
        ordering = ['question',]

class News(models.Model):
    headline = models.CharField(_("headline"),
            max_length=150,
            help_text='The headline display for this news.')
    content = RichTextField(_("content"),
            help_text='A description of the field')
    published = models.DateTimeField(auto_now=True)
    published_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'news'
        ordering = ['-published',]
        verbose_name_plural = 'news'