from django.db import models
from django.utils.translation import gettext_lazy as _
from well_logs.models import Log, Data
from geoluminate.fields import RangeField
from . import choices
from shortuuid.django_fields import ShortUUIDField


class AbstractLog(models.Model):
    site = models.ForeignKey("database.HeatFlow",
                             verbose_name=_("site"),
                             blank=True, null=True,
                             on_delete=models.CASCADE)
    reference = models.ForeignKey("literature.Publication",
                                  help_text=_(
                                      'The publications or other reference from which the measurement was reported.'),
                                  verbose_name=("reference"),
                                  blank=True, null=True,
                                  on_delete=models.CASCADE)

    method = models.CharField(
        _("method"),
        max_length=200,
        blank=True,
        null=True)

    source = models.CharField(_("original source"),
                              help_text=_('Where the data came from'),
                              max_length=50,
                              blank=True, null=True)

    source_id = models.CharField(_("original source ID"),
                                 help_text=_('ID from data source'),
                                 max_length=64,
                                 blank=True, null=True)

    class Meta:
        abstract = True


class ConductivityLog(AbstractLog, Log):
    uuid = ShortUUIDField(
        length=10,
        max_length=15,
        prefix="GHFLOG-TC",
        alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
        primary_key=True
    )

    class Meta:
        default_related_name = 'conductivity_logs'
        verbose_name_plural = _('conductivity logs')
        verbose_name = _('conductivity log')
        db_table = 'thermal_conductivity_log'


class Conductivity(Data):

    sample_type = models.CharField(_("sample_type"),
                                   help_text=_(
                                       'Type of sample used to determine conductivity'),
                                   max_length=23,
                                   choices=choices.ConductivitySource.choices)
    method = models.CharField(_("thermal conductivity method"),
                              help_text=_(
                                  'Method used to determine the mean thermal conductivity over the given interval'),
                              max_length=100, blank=True, null=True)
    saturation_state = models.CharField(_("thermal conductivity saturation"),
                                        help_text=_(
                                            'Saturation state of the sample'),
                                        max_length=100)

    lithology = models.OneToOneField('earth_science.EarthMaterial',
                                     verbose_name=_("lithology"),
                                     on_delete=models.SET_NULL,
                                     help_text=_('BGS rock classification.'),
                                     blank=True, null=True)

    name = models.CharField(_("sample name/ID"),
                            max_length=200, blank=True)
    length = models.FloatField(_("length (cm)"),
                               null=True, blank=True)
    width = models.FloatField(_("width (cm)"),
                              null=True, blank=True)
    diameter = models.FloatField(_("diameter (cm)"),
                                 null=True, blank=True)
    thickness = models.FloatField(_("thickness (cm)"),
                                  null=True, blank=True)

    orientation = RangeField(_("orientation"),
                             help_text=_(
                                 'Angle relative to the foliation/bedding where 0 is parallel and 90 is perpendicular'),
                             min_value=0, max_value=90,
                             blank=True, null=True)
    IGSN = models.CharField(_('IGSN sample number'),
                            help_text=_(
                                'International Geo Sample Numbers (IGSN, semicolon separated) for rock samples used for laboratory measurements of thermal conductivity'),
                            max_length=100,
                            )

    class Meta:
        db_table = 'thermal_conductivity'
        ordering = ['depth']


class TemperatureLog(AbstractLog, Log):
    uuid = ShortUUIDField(
        length=8,
        max_length=13,
        prefix="GHFT-",
        alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
        primary_key=True,
    )
    method = models.CharField(
        _("method"),
        max_length=200,
        blank=True,
        null=True)

    circ_time = models.FloatField(
        _("circulation time (hrs)"),
        blank=True,
        null=True)
    lag_time = models.FloatField(_("lag time (hrs)"), blank=True, null=True)
    correction = models.CharField(_("correction type"),
                                  max_length=150,
                                  blank=True, null=True)

    class Meta:
        default_related_name = 'temperature_logs'
        verbose_name = _('temperature log')
        verbose_name_plural = _('temperature logs')
        db_table = 'temp_meta'
        ordering = ['added']


class Temperature(Data):

    class Meta:
        db_table = 'temperature'
        verbose_name = _('temperature')
        verbose_name_plural = _('temperature data')
