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
    description = RichTextField(_("decsription"),
            help_text=_("Description to include in the page <head> tags"),
            blank=True,null=True)

    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['id',]

class Field(models.Model):
    field_name = models.CharField(_("field name"),
            max_length=100,
            help_text='This is how the field should appear in any download files.')
    description = RichTextField(_("field description"),
            help_text='A description of the field')

    units = models.CharField(_("units"),
            max_length=15,
            null=True, blank=True,
            help_text='Default unit of measurement')

    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['field_name',]

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