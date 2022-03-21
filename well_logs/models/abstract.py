import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.query import QuerySet
from io import StringIO
import csv, json, zipfile
from core.querysets import QuerySetExtra


class WellLog(models.Model):

    objects = QuerySetExtra.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    site = models.ForeignKey("thermoglobe.Site",
                verbose_name=_("site"),
                blank=True, null=True,
                on_delete=models.CASCADE)
    reference = models.ForeignKey("publications.Publication",
                help_text=_('The publications or other reference from which the measurement was reported.'),
                verbose_name=("reference"), 
                blank=True,null=True, 
                on_delete=models.CASCADE)
    
    formation = models.CharField(_("geological formation"), max_length=200, blank=True, null=True)
    method = models.CharField(_("method"), max_length=200, blank=True, null=True)
    operator = models.CharField(_("operator"),
            help_text=_('The operator collecting the measurements'),
            max_length=150, 
            blank=True, null=True)
    source = models.CharField(_("original source"), 
        help_text=_('Where the data came from'),
        max_length=50,
        blank=True, null=True)

    source_id = models.CharField(_("original source ID"),
            help_text=_('ID from data source'),
            max_length=64, 
            blank=True, null=True)
    year_logged = models.PositiveSmallIntegerField(_("year"),
        validators=[MinValueValidator(1900),MaxValueValidator(2050)],
        blank=True, null=True,
        )

    comment = models.TextField(_("comments"), blank=True,null=True)

    added = models.DateTimeField(_('added'), auto_now_add=True)
        
    class Meta:
        abstract=True
        ordering = ['site','log_id']
        unique_together = ['site','log_id']


class RawData(models.Model):

    value = models.FloatField(_("value"))
    uncertainty = models.FloatField(_("uncertainty"), null=True, blank=True)   
    depth = models.FloatField(_("depth (m)"))

    class Meta:
        abstract=True
        ordering = ['depth']
        unique_together = ['value', 'depth', 'log']

    def __str__(self):
        return f'{self.value}'