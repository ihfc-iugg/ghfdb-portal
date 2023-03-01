# -*- coding: UTF-8 -*-
from controlled_vocabulary.models import ControlledTerm, ControlledTermField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from geoluminate.models import Geoluminate
from geoscience.fields import EarthMaterialOneToOne, GeologicTimeOneToOne
from ghfdb import choices
from quantityfield.fields import PositiveIntegerQuantityField, QuantityField
from shortuuid.django_fields import ShortUUIDField


class HeatFlow(Geoluminate):
    """Terrestrial heat flow as part of the Global Heat Flow Database. This is
    the "parent" table outlined in the formal structure of the database put
    forth by Fuchs et. al. (2021).
    """

    q = QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow"),
        help_text=_("site heat flow value"),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    q_unc = QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow uncertainty"),
        help_text=_(
            "uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient)."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    q_date_acq = models.DateField(
        _("date acquired"),
        help_text=_(
            'Year of acquisition of the heat-flow data in the form "YYYY-MM" (may differ from publication year)'
        ),
        null=True,
    )
    borehole_depth = QuantityField(
        verbose_name=_("total borehole depth"),
        base_units="m",
        help_text=_(
            "Specification of the total drilling depth below ground surface level."
        ),
        validators=[MinVal(0), MaxVal(15000)],
        null=True,
        blank=True,
    )
    expedition = models.CharField(
        verbose_name=_("expedition/platform/ship"),
        null=True,
        help_text=_(
            "Specify the expedition, cruise, platform or research vessel where the marine heat flow survey was conducted. Only applies to marine probe sensing and drillings. Examples: Expedition cruise number OR R/V Ship OR D/V Platform"
        ),
        max_length=255,
    )

    environment = ControlledTermField(
        "environment",
        verbose_name=_("basic geographical environment"),
        help_text=_(
            "Describes the general geographical setting of the heat-flow site (not the applied methodology)."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    water_temp = QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("bottom water temperature"),
        help_text=_("Seafloor temperature where heat-flow measurements were taken."),
        null=True,
        blank=True,
    )

    explo_method = ControlledTermField(
        "explo_method",
        verbose_name=_("exploration method"),
        help_text=_(
            "Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    explo_purpose = ControlledTermField(
        "explo_purpose",
        verbose_name=_("exploration purpose"),
        help_text=_(
            "Main purpose of the original excavation providing access for the temperature sensors."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow (Parent)")
        default_related_name = "sites"
        # ordering = ["-date_added"]
        db_table = "global_heat_flow"

    def save(self, *args, **kwargs):
        # if uncertainty > 50%? of mean, ask user for validation
        return super().save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        """
        <Unnamed Site: 45.2 +/- 3.2 mW/m^2>

        """
        name = self.name if self.name else _("Unnamed Site")

        q = self.q.plus_minus(self.q_unc)

        return f"{name} <{q.magnitude:~P}>"

    def get_absolute_url(self):
        return reverse("site", kwargs={"pk": self.pk})


class Interval(models.Model):
    """Interval heat flow as part of the Global Heat Flow Database. This is
    the "child" schema outlined in the formal structure of the database put
    forth by Fuchs et al (2021).
    """

    id = ShortUUIDField(
        verbose_name="ID",
        length=8,
        blank=True,
        max_length=15,
        prefix="GHFI-",
        alphabet="23456789ABCDEFGHJKLMNPQRSTUVWXYZ",
        primary_key=True,
    )
    historic_id = models.PositiveIntegerField(
        _("Historic ID"),
        help_text=_(
            "This is the numeric identifier used in old forms of the GHFDB to identify measurements"
        ),
        blank=True,
        null=True,
    )
    site = models.ForeignKey(
        "ghfdb.HeatFlow",
        verbose_name=_("site"),
        null=True,
        on_delete=models.SET_NULL,
    )

    # HEAT FLOW DENSITY FIELDS
    qc = QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow"),
        help_text=_("child heat flow value"),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    qc_unc = QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow uncertainty"),
        help_text=_(
            "uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient)."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )

    q_method = ControlledTermField(
        "q_method",
        verbose_name=_("method"),
        help_text=_(
            "Principal method of heat-flow density calculation from temperature and thermal conductivity data"
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    q_top = QuantityField(
        base_units="m",
        verbose_name=_("interval top"),
        help_text=_(
            "Specifies the true vertical depth at the top of the heat-flow interval relative to land surface/ocean bottom."
        ),
        validators=[MinVal(0), MaxVal(10000)],
        blank=True,
        null=True,
    )
    q_bot = QuantityField(
        base_units="m",
        verbose_name=_("interval bottom"),
        help_text=_(
            "Describes the true vertical depth of the bottom end of the heat-flow determination interval relative to the land surface/ocean bottom."
        ),
        validators=[MinVal(0), MaxVal(10000)],
        blank=True,
        null=True,
    )

    # PROBE SENSING
    hf_pen = QuantityField(
        base_units="m",
        verbose_name=_("penetration depth"),
        help_text=_("Depth of penetration of marine probe into the sediment."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    hf_probe = ControlledTermField(
        "hf_probe",
        verbose_name=_("probe type"),
        help_text=_("Type of marine probe used for measurement."),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    hf_probeL = QuantityField(
        base_units="m",
        verbose_name=_("probe length"),
        help_text=_("length of the marine probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    probe_tilt = QuantityField(
        base_units="degree",
        verbose_name=_("tilt"),
        help_text=_("Tilt of the marine probe."),
        validators=[MinVal(0), MaxVal(90)],
        blank=True,
        null=True,
    )

    # METADATA AND FLAGS
    q_tf_mech = ControlledTermField(
        "q_tf_mech",
        verbose_name=_("transfer mechanism"),
        help_text=_(
            "Specification of the predominant heat transfer mechanism relevant to the reported heat flow value."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reference = models.ForeignKey(
        "literature.Literature",
        help_text=_(
            "The publication or other reference from which the measurement was reported."
        ),
        verbose_name=_("reference"),
        on_delete=models.CASCADE,
    )
    q_date_acq = models.DateField(
        _("date of acquisition (YYYY-MM)"),
        help_text=_(
            "Year of acquisition of the heat-flow data (may differ from publication year)"
        ),
        null=True,
        blank=True,
    )
    relevant_child = models.BooleanField(
        verbose_name=_("Is relevant child?"),
        help_text=_(
            "Specify whether the child entry is used for computation of representative location heat flow values at the parent level or not."
        ),
        default=None,
        null=True,
        blank=True,
    )
    lithology = EarthMaterialOneToOne(
        verbose_name=_("lithology"),
        help_text=_(
            "Dominant rock type/lithology within the interval of heat-flow determination using the British Geological Society Earth Material Class (rock classification) scheme."
        ),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    stratigraphy = GeologicTimeOneToOne(
        verbose_name=_("ICS stratigraphy"),
        help_text=_(
            "Stratigraphic age of the depth range involved in the reported heat-flow determination based on the official geologic timescale of the International Commission on Stratigraphy."
        ),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # Temperature Fields
    T_grad_mean = QuantityField(
        base_units="K/km",
        verbose_name=_("measured gradient"),
        help_text=_(
            "measured temperature gradient for the heat-flow determination interval."
        ),
        null=True,
        blank=True,
    )
    T_grad_uncertainty = QuantityField(
        base_units="K/km",
        verbose_name=_("uncertainty"),
        help_text=_(
            "uncertainty (standard deviation) of the measured temperature gradient estimated by error propagation from uncertainty in the top and bottom interval temperatures."
        ),
        blank=True,
        null=True,
    )
    T_grad_mean_cor = QuantityField(
        base_units="K/km",
        verbose_name=_("corrected gradient"),
        help_text=_(
            "temperature gradient corrected for borehole and environmental effects. Correction method should be recorded in the relevant field."
        ),
        blank=True,
        null=True,
    )
    T_grad_uncertainty_cor = QuantityField(
        base_units="K/km",
        verbose_name=_("uncertainty"),
        help_text=_(
            "uncertainty (standard deviation) of the corrected temperature gradient estimated by error propagation from uncertainty of the measured gradient and the applied correction approaches."
        ),
        blank=True,
        null=True,
    )
    T_method_top = ControlledTermField(
        "T_method",
        verbose_name=_("temperature method (top)"),
        help_text=_(
            "Method used to determine temperature at the top of the heat flow interval."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    T_method_bottom = ControlledTermField(
        "T_method",
        verbose_name=_("temperature method (bottom)"),
        help_text=_(
            "Method used to determine temperature at the bottom of the heat flow interval."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    T_shutin_top = PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("Shut-in time (top)"),
        help_text=_(
            "Time of measurement at the interval top in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling."
        ),
        blank=True,
        null=True,
    )
    T_shutin_bottom = PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("Shut-in time (bottom; hrs)"),
        help_text=_(
            "Time of measurement at the interval bottom in relation to the end of drilling/end of mud circulation. Positive values are measured after the drilling, 0 represents temperatures measured during the drilling."
        ),
        blank=True,
        null=True,
    )
    T_correction_top = ControlledTermField(
        "T_correction_method",
        verbose_name=_("correction method (top)"),
        help_text=_(
            "Approach used at the top of the heat flow interval to correct the measured temperature for drilling perturbations."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    T_correction_bottom = ControlledTermField(
        "T_correction_method",
        verbose_name=_("correction method (bottom)"),
        help_text=_(
            "Approach used at the bottom of the heat flow interval to correct the measured temperature for drilling perturbations."
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    T_count = models.PositiveSmallIntegerField(
        _("number of temperature recordings"),
        help_text=_(
            "Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth."
        ),
        blank=True,
        null=True,
    )

    # Conductivity fields
    tc_mean = QuantityField(
        base_units="W/mK",
        verbose_name=_("Mean conductivity"),
        help_text=_(
            "Mean conductivity in the vertical direction representative for the heat-flow determination interval. Value should reflect true in-situ conditions for the interval."
        ),
        null=True,
        blank=True,
        validators=[MinVal(0), MaxVal(100)],
    )
    tc_uncertainty = QuantityField(
        base_units="W/mK",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty of the mean thermal conductivity given as one-sigma standard deviation."
        ),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    tc_source = ControlledTermField(
        "tc_source",
        verbose_name=_("source"),
        help_text=_(
            "Nature of the samples from which the mean thermal conductivity was determined"
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tc_method = models.CharField(
        _("method"),
        help_text=_(
            "Method used to determine the mean thermal conductivity over the given interval"
        ),
        max_length=100,
        blank=True,
        null=True,
    )
    tc_saturation = models.CharField(
        _("saturation state"),
        help_text=_(
            "Saturation state of the rock sample studied for thermal conductivity"
        ),
        max_length=100,
        null=True,
        blank=True,
    )
    tc_pT_conditions = ControlledTermField(
        "tc_pT_conditions",
        verbose_name=_("pT conditions"),
        help_text=_(
            'Pressure and temperature conditions under which the mean thermal conductivity for the given interval was determined. "Recorded" - determined under true conditions at target depths (e.g. sensing in boreholes), "Replicated" - determined in a laboratory under replicated in-situ conditions, "Actual" - under conditions at the respective depth of the heat-flow interval'
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tc_pT_function = models.CharField(
        _("assumed pT function"),
        help_text=_(
            "Technique or approach used to correct the measured thermal conductivity towards in-situ pT conditions"
        ),
        blank=True,
        null=True,
        max_length=255,
    )
    tc_strategy = models.CharField(
        verbose_name=_("averaging methodoloy"),
        help_text=_(
            "Strategy employed to estimate thermal conductivity over the given interval"
        ),
        max_length=255,
        null=True,
        blank=True,
    )
    tc_count = models.PositiveSmallIntegerField(
        _("number of temperature recordings"),
        help_text=_(
            "Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth."
        ),
        blank=True,
        null=True,
    )

    corrections = models.ManyToManyField(
        ControlledTerm,
        verbose_name=_("Applied Corrections"),
        through="ghfdb.IntervalCorrectionThrough",
        blank=True,
    )

    if not settings.DEBUG:
        history = HistoricalRecords()

    class Meta:
        verbose_name = _("Interval")
        verbose_name_plural = _("Heat Flow (Child)")
        ordering = ["site", "relevant_child", "q_top"]
        default_related_name = "intervals"
        db_table = "heat_flow_interval"

    def __str__(self):
        return f"{self.pk}"

    def clean(self, *args, **kwargs):
        # run the base validation
        super().clean(*args, **kwargs)

        # Don't allow year older than 1900.
        if self.q_date_acq is not None:
            if self.q_date_acq.year < 1900:
                raise ValidationError("Acquisition year cannot be less than 1900.")

    def full_clean(self, exclude, validate_unique):
        return super().full_clean(exclude, validate_unique)

    def interval(self, obj):
        return "{}-{}".format(obj.q_top, obj.q_bot)


class IntervalCorrectionThrough(models.Model):
    """An intermediate table for the Interval-Correction m2m relationship that
    additionally stores a correction value."""

    APPLIED_CHOICES = choices.CorrectionApplied

    interval = models.ForeignKey("ghfdb.Interval", on_delete=models.CASCADE)
    correction = ControlledTermField("correction", on_delete=models.CASCADE)
    applied = models.CharField(
        max_length=9,
        verbose_name=_("Applied?"),
        help_text=_("Has the correction been applied to this interval?"),
        choices=APPLIED_CHOICES.choices,
    )
    value = models.FloatField(
        verbose_name=_("value"),
        help_text=_(
            "Value of the applied correction in (mW m^-2). Can be positive or negative."
        ),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("correction")
        verbose_name_plural = _("corrections")

    def __str__(self):
        if self.applied == 0:
            return
        return str(self.value)
