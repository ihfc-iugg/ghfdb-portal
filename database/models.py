# -*- coding: UTF-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from simple_history.models import HistoricalRecords
from meta.models import ModelMeta
from django.utils.encoding import force_str
from geoluminate.gis.models import Site
from geoluminate.fields import RangeField
from shortuuid.django_fields import ShortUUIDField
from django.core.exceptions import ValidationError
from earth_science.fields import EarthMaterialOneToOne, GeologicTimeOneToOne
from django_ckeditor_5.fields import CKEditor5Field
from geoluminate.fields import (
    ChoicesForeignKey,
    ChoicesManyToMany,
    ChoicesForeignKey
)
from django.conf import settings
from database import choices


class HeatFlow(ModelMeta, Site):
    """Abstract base class for the GHFDB HeatFlow model. All fields are stored
    in this abstract class so that multiple tables can be constructed using
    the same field definitions (e.g. for the review app).

    Note: This is the "Parent" class from the GHFDB structure publications.

    Mixins:
        ModelMeta (django-meta.models.ModelMeta): ModelMeta mixin from the
        `Django-Meta` application
        HeatFlowAbstract (mapping.models.HeatFlowAbstract): An abstract base class
        that contains relation fields to geographically enabled models.

    """

    name = models.CharField(
        verbose_name=_('name'),
        null=True,
        help_text=_(
            'Specification of the (local) name of the related heat-flow site or the related survey.'),
        max_length=255)
    q = models.FloatField(_("heat flow"), help_text=_('site heat flow value'))
    q_unc = RangeField(_("heat flow uncertainty"),
                       help_text=_('uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).'),
                       min_value=0,
                       blank=True, null=True)
    q_acq = models.DateField(_('date acquired'),
                             help_text=_(
                                 'Year of acquisition of the heat-flow data in the form "YYYY-MM" (may differ from publication year)'),
                             null=True,
                             )
    env = ChoicesForeignKey(_("basic geographical environment"),
                            help_text=_(
        'Describes the general geographical setting of the heat-flow site (not the applied methodology).'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    wat_temp = models.FloatField(_('bottom water temperature (°C)'),
                                 help_text=_(
                                     'Seafloor temperature where heat-flow measurements were taken.'),
                                 null=True, blank=True,
                                 )
    method = ChoicesForeignKey(_("exploration method"),
                               help_text=_(
        'Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry.'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    expl = ChoicesForeignKey(_("exploration purpose"),
                             help_text=_(
        'Main purpose of the original excavation providing access for the temperature sensors.'),
        null=True, blank=True,
        on_delete=models.SET_NULL)

    references = models.ManyToManyField("literature.Publication",
                                        verbose_name=_("references"),
                                        help_text=_(
                                            'The reference or publication from which the data were sourced. Each site may have multiple references.'),
                                        blank=True)
    q_comment = models.TextField(_("general comments"),
                                 help_text=_(
                                     'General comments regarding the heat flow site/measurement'),
                                 blank=True, null=True)

    # META FIELDS
    # slug = AutoSlugField(populate_from=['name'])
    last_modified = models.DateField(_('last modified'), auto_now=True)
    date_added = models.DateField(_('date added'),
                                  auto_now_add=True,)
    _metadata = {
        'title': 'get_meta_title',
        'description': 'description',
        'year': 'year',
    }
    if not settings.DEBUG:
        history = HistoricalRecords()

    class Meta:
        verbose_name = _('Heat Flow')
        verbose_name_plural = _('Heat Flow (Parent)')
        default_related_name = 'sites'
        ordering = ['-date_added']
        db_table = 'global_heat_flow'

    def __unicode__(self):
        return u'%s' % (self.name)

    def __str__(self):
        if self.name:
            return force_str(self.name)
        else:
            return f"{self.geom.latitude}, {self.geom.longitude}"

    def get_absolute_url(self):
        return reverse("geoluminate:site", kwargs={"pk": self.pk})


class Interval(models.Model):
    """Abstract base class for the GHFDB Interval model. All fields are stored
    in this abstract class so that multiple tables can be constructed using
    the same field definitions (e.g. for the review app).

    Note: This is the "Child" table from the GHFDB structure publications and
    stores a Foreign Key to the Site (parent) table.
    """
    id = ShortUUIDField(
        length=8,
        max_length=15,
        prefix="GHFI-",
        alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
        primary_key=True,
    )
    historic_id = models.PositiveIntegerField(_('Historic ID'),
                                              help_text=_(
                                                  'This is the numeric identifier used in old forms of the GHFDB to identify measurements'),
                                              blank=True, null=True)
    site = models.ForeignKey("database.HeatFlow",
                             verbose_name=_("site"),
                             null=True,
                             on_delete=models.SET_NULL)

    # HEAT FLOW DENSITY FIELDS
    qc = models.FloatField(_("heat flow"), help_text=_('heat flow value'))
    qc_unc = RangeField(_("uncertainty"),
                        help_text=_('uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).'),
                        min_value=0,
                        blank=True, null=True)
    q_method = ChoicesForeignKey(_("method"),
                                 help_text=_(
        'Principal method of heat-flow density calculation from temperature and thermal conductivity data'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    q_top = RangeField(_("interval top (m)"),
                       help_text=_(
                           'Describes the true vertical depth of the top end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
                       max_value=12500,
                       blank=True, null=True)
    q_bot = RangeField(_("interval bottom (m)"),
                       help_text=_(
                           'Describes the true vertical depth of the bottom end of the heat-flow determination interval relative to the land surface/ocean bottom.'),
                       min_value=0, max_value=12500,
                       blank=True, null=True)

    # PROBE SENSING
    hf_pen = RangeField(_("penetration depth (m)"),
                        help_text=_(
                            'Depth of penetration of marine probe into the sediment.'),
                        min_value=0, max_value=100,
                        blank=True, null=True)
    hf_probe = ChoicesForeignKey(_("probe type"),
                                 help_text=_(
        'Type of marine probe used for measurement.'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    hf_probeL = RangeField(_("probe length (m)"),
                           help_text=_('length of the marine probe.'),
                           max_value=100, min_value=0,
                           blank=True, null=True)
    T_tilt = RangeField(_("tilt (deg)"),
                        help_text=_('Tilt of the marine probe.'),
                        max_value=90, min_value=0,
                        blank=True, null=True)

    # METADATA AND FLAGS
    q_tf_mech = ChoicesForeignKey(_("transfer mechanism"),
                                  help_text=_(
        'Specification of the predominant heat transfer mechanism relevant to the reported heat flow value.'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    reference = models.ForeignKey("literature.Publication",
                                  help_text=_(
                                      'The publication or other reference from which the measurement was reported.'),
                                  verbose_name=_("reference"),
                                  on_delete=models.CASCADE)
    q_acq = models.DateField(_('date of acquisition (YYYY-MM)'),
                             help_text=_(
                                 'Year of acquisition of the heat-flow data (may differ from publication year)'),
                             null=True, blank=True,
                             )
    childcomp = models.BooleanField(_('Is relevant child?'),
                                    help_text=_(
                                        'Specifies whether the child entry is used for computation of representative location heat flow values at the parent level or not.'),
                                    default=None, null=True, blank=True,
                                    )
    geo_lith = EarthMaterialOneToOne(
        verbose_name=_("lithology"),
        help_text=_('Dominant rock type/lithology within the interval of heat-flow determination using the British Geological Society Earth Material Class (rock classification) scheme.'),
        on_delete=models.SET_NULL,
        blank=True, null=True)
    geo_strat = GeologicTimeOneToOne(
        verbose_name=_("ICS stratigraphy"),
        help_text=_('Stratigraphic age of the depth range involved in the reported heat-flow determination based on the official geologic timescale of the International Commission on Stratigraphy.'),
        on_delete=models.SET_NULL,
        blank=True, null=True)

    # Temperature Fields
    T_grad_mean_meas = models.FloatField(_("measured gradient (K/km)"),
                                         help_text=_(
                                             'measured temperature gradient for the heat-flow determination interval.'),
                                         null=True, blank=True,)
    T_grad_unc_meas = models.FloatField(_("uncertainty (K/km)"),
                                        help_text=_(
                                            'uncertainty (standard deviation) of the measured temperature gradient estimated by error propagation from uncertainty in the top and bottom interval temperatures.'),
                                        blank=True, null=True)
    T_grad_mean_cor = models.FloatField(_("corrected gradient (K/km)"),
                                        help_text=_(
                                            'temperature gradient corrected for borehole and environmental effects. Correction method should be recorded in the relevant field.'),
                                        blank=True, null=True)
    T_grad_unc_cor = models.FloatField(_("uncertainty (K/km)"),
                                       help_text=_(
                                           'uncertainty (standard deviation) of the corrected temperature gradient estimated by error propagation from uncertainty of the measured gradient and the applied correction approaches.'),
                                       blank=True, null=True)
    T_method_top = ChoicesForeignKey(_("temperature method (top)"),
                                     help_text=_(
        'Method used to determine temperature at the top of the heat flow interval.'),
        choice_type='T_method',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    T_method_bot = ChoicesForeignKey(_("temperature method (bottom)"),
                                     help_text=_(
        'Method used to determine temperature at the bottom of the heat flow interval.'),
        choice_type='T_method',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    T_shutin_top = models.PositiveSmallIntegerField(_("Shut-in time (top; hrs)"),
                                                    help_text=_(
                                                        'Time of measurement at the interval top in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling.'),
                                                    blank=True, null=True)
    T_shutin_bot = models.PositiveSmallIntegerField(_("Shut-in time (bottom; hrs)"),
                                                    help_text=_(
                                                        'Time of measurement at the interval bottom in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling.'),
                                                    blank=True, null=True)
    T_corr_top = ChoicesForeignKey(_("correction method (top)"),
                                   help_text=_(
        'Approach used at the top of the heat flow interval to correct the measured temperature for drilling perturbations.'),
        choice_type='T_corr_method',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    T_corr_bot = ChoicesForeignKey(_("correction method (bottom)"),
                                   help_text=_(
        'Approach used at the bottom of the heat flow interval to correct the measured temperature for drilling perturbations.'),
        choice_type='T_corr_method',
        null=True, blank=True,
        on_delete=models.SET_NULL)
    T_numb = models.PositiveSmallIntegerField(_("number of temperature recordings"),
                                              help_text=_(
                                                  'Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth.'),
                                              blank=True, null=True)

    # Conductivity fields
    tc_mean = RangeField(_("Mean conductivity (W/mK)"),
                         help_text=_(
                             'Mean conductivity in the vertical direction representative for the heat-flow determination interval. Value should reflect true in-situ conditions for the interval.'),
                         null=True, blank=True,
                         min_value=0, max_value=100)
    tc_unc = RangeField(_("uncertainty"),
                        help_text=_(
                            'Uncertainty of the mean thermal conductivity given as one-sigma standard deviation.'),
                        min_value=0, max_value=100,
                        blank=True, null=True)
    tc_source = ChoicesForeignKey(_("source"),
                                  help_text=_(
        'Nature of the samples from which the mean thermal conductivity was determined'),
        null=True, blank=True,
        on_delete=models.SET_NULL)
    tc_meth = models.CharField(_("method"),
                               help_text=_(
                                   'Method used to determine the mean thermal conductivity over the given interval'),
                               max_length=100, blank=True, null=True)
    tc_satur = models.CharField(_("saturation state"),
                                help_text=_(
                                    'Saturation state of the rock sample studied for thermal conductivity'),
                                max_length=100, null=True, blank=True,)
    tc_pTcond = ChoicesForeignKey(_("pT conditions"),
                                  help_text=_('Pressure and temperature conditions under which the mean thermal conductivity for the given interval was determined. "Recorded" - determined under true conditions at target depths (e.g. sensing in boreholes), "Replicated" - determined in a laboratory under replicated in-situ conditions, "Actual" - under conditions at the respective depth of the heat-flow interval'),
                                  null=True, blank=True,
                                  on_delete=models.SET_NULL)
    tc_pTfunc = models.CharField(_("assumed pT function"),
                                 help_text=_(
                                     'Technique or approach used to correct the measured thermal conductivity towards in-situ pT conditions'),
                                 blank=True, null=True,
                                 max_length=255)
    tc_strategy = models.CharField(_("averaging methodoloy"),
                                   help_text=_(
                                       'Strategy employed to estimate thermal conductivity over the given interval'),
                                   max_length=255,
                                   null=True, blank=True,)
    tc_numb = models.PositiveSmallIntegerField(_("number of temperature recordings"),
                                               help_text=_(
                                                   'Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth.'),
                                               blank=True, null=True)

    corrections = ChoicesManyToMany(_('Applied Corrections'),
                                    through='database.IntervalCorrectionThrough',
                                    blank=True,
                                    )

    # META
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)
    if not settings.DEBUG:
        history = HistoricalRecords()

    class Meta:
        verbose_name = _('Interval')
        verbose_name_plural = _('Heat Flow (Child)')
        ordering = ['site', 'childcomp', 'q_top']
        default_related_name = 'intervals'
        db_table = 'heat_flow_interval'

    def __str__(self):
        return f"{self.pk}"

    def clean(self, *args, **kwargs):
        # run the base validation
        super().clean(*args, **kwargs)

        # Don't allow year older than 1900.
        if self.q_acq is not None:
            if self.q_acq.year < 1900:
                raise ValidationError(
                    'Acquisition year cannot be less than 1900.')

    def full_clean(self, exclude, validate_unique):
        return super().full_clean(exclude, validate_unique)

    def interval(self, obj):
        return '{}-{}'.format(obj.q_top, obj.q_bot)


class Choice(models.Model):
    """This is a generic model for storing modifiable choices in a single table.
    Each `type` relates to a collection of choices that can be utilised by
    `django.db.models.ChoiceField` fields in other models.
    """
    class TypeChoices(models.TextChoices):
        CON_PT = 'tc_pTcond', _('TC PT Conditions')
        CON_SAT = 'tc_satur', _('TC Saturation State')
        CON_SRC = 'tc_source', _('TC Source')
        CORR = 'corrections', _('Correction')
        ENV = 'env', _('Environment')
        EX_METH = 'method', _('Exploration Method')
        EX_PUR = 'expl', _('Exploration Purpose')
        HF_METH = 'q_method', _('Heat Flow Method')
        PROBE = 'hf_probe', _('Probe Type')
        TMP_COR = 'T_corr_method', _('Temp. Corr. Method')
        TMP_METH = 'T_method', _('Temp. Method')
        TRA_MEC = 'q_tf_mech', _('Transfer Mechanism')

    type = models.CharField(_('type'),
                            choices=TypeChoices.choices,
                            max_length=16)
    code = models.CharField(_('code'), max_length=64)
    name = models.CharField(_('name'), max_length=128)
    description = CKEditor5Field(_('description'),
                                 blank=True, null=True)

    class Meta:
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')
        unique_together = ('type', 'code')
        ordering = ['type', 'code']

    def __str__(self):
        return f'{self.type}("{self.code}")'

    @staticmethod
    def autocomplete_search_fields():
        # For Django Grappelli related lookups
        return ("name__icontains", "code__icontains",)


class IntervalCorrectionThrough(models.Model):
    """An intermediate table for the Interval-Correction m2m relationship that
    additionally stores a correction value."""
    APPLIED_CHOCES = choices.CorrectionApplied

    interval = models.ForeignKey("database.Interval", on_delete=models.CASCADE)
    correction = ChoicesForeignKey(
        choice_type='corrections',
        on_delete=models.CASCADE)
    applied = models.CharField(
        max_length=9,
        verbose_name=_('Applied?'),
        help_text=_('Has the correction been applied to this interval?'),
        choices=APPLIED_CHOCES.choices)
    value = models.FloatField(
        verbose_name=_('value'),
        help_text=_(
            'Value of the applied correction in (mW m^-2). Can be positive or negative.'),
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _('correction')
        verbose_name_plural = _('corrections')

    def __str__(self):
        if self.applied == 0:
            return
        return str(self.number)
