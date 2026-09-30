"""Child-level heat flow models for the Global Heat Flow Database (GHFDB).

This module contains HeatFlowInterval (the depth interval within a borehole),
the child HeatFlow record, and all directly associated sub-measurement models
(ThermalGradient, IntervalConductivity, ProbeMetadata, HeatFlowCorrection).
Each HeatFlow child links to a ParentHeatFlow via ForeignKey.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat Flow Database.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from functools import cached_property
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.db import models as django_models
from django.utils.translation import gettext_lazy as _
from fairdm.core.models import Measurement
from fairdm.db import models
from fairdm_geo.core.models import GeoDepthInterval as AbstractGeoDepthInterval
from fairdm_geo.core.models import Interval
from research_vocabs.fields import ConceptManyToManyField

from heat_flow import vocabularies

from ..quality import SCHEME_REVISION, QualityScheme, Reading, SubScore, route
from ..utils import MScoreOptions, UScoreOptions


class HeatFlowInterval(Interval, AbstractGeoDepthInterval):
    """Depth interval within a HeatFlowSite borehole over which a child heat flow measurement is calculated."""

    site = models.ForeignKey(
        "heat_flow.HeatFlowSite",
        verbose_name=_("site"),
        help_text=_("The heat flow site this depth interval belongs to."),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="intervals",
    )

    class Meta:
        verbose_name = _("Depth interval")
        verbose_name_plural = _("Depth intervals")

    def __str__(self):
        """String representation of the depth interval."""
        top = getattr(self.top, "magnitude", self.top) if self.top is not None else "?"
        bottom = (
            getattr(self.bottom, "magnitude", self.bottom)
            if self.bottom is not None
            else "?"
        )
        return f"{self.__class__.__name__}({top}-{bottom})"

    def clean(self):
        """Reject an interval whose bottom depth is not below its top depth."""
        super().clean()
        if self.top is not None and self.bottom is not None:
            top = getattr(self.top, "magnitude", self.top)
            bottom = getattr(self.bottom, "magnitude", self.bottom)
            if top >= bottom:
                raise ValidationError(
                    _("Interval bottom depth must be greater than top depth.")
                )


class HeatFlow(Measurement):
    """Child heat flow as part of the Global Heat Flow Database.

    This is the "child" schema outlined in the formal structure of the
    database put forth by Fuchs et al (2021).
    """

    U_SCORE_CHOICES = UScoreOptions

    value = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow"),
        help_text=_(
            "Heat-flow density at a given location after all corrections for instrumental and environmental effects have been applied."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_(
            "The uncertainty (1 sigma) of the heat-flow value. Uncertainty is estimated by propagating errors from uncertainties in thermal conductivity and temperature gradient. Alternatively, it can be determined by the deviation from the linear regression of the Bullard plot, with preference given to corrected values over directly measured gradients."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    method = ConceptManyToManyField(
        vocabulary=vocabularies.HeatFlowMethod,
        verbose_name=_("method"),
        help_text=_(
            "Principal method of heat-flow calculation from temperature and thermal conductivity data."
        ),
        blank=True,
    )
    expedition = models.CharField(
        verbose_name=_("expedition/platform/ship"),
        help_text=_(
            "Specification of the expedition, cruise, platform or research vessel where the marine heat flow survey was"
            " conducted."
        ),
        max_length=255,
        null=True,
        blank=True,
    )

    surface_temperature = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("surface temperature"),
        help_text=_(
            "Temperature at the upper boundary of the heat-flow determination interval: seafloor or"
            " bottom-water temperature for a marine measurement, ground-surface or mudline temperature for a"
            " continental one. e.g. PT 100 or Mudline temperature for ocean drilling data."
        ),
        null=True,
        blank=True,
        validators=[MinVal(-10), MaxVal(1000)],
    )
    date_acquired = models.PartialDateField(
        _("date of acquisition "),
        help_text=_(
            "Year of acquisition of the heat-flow data which may differ from publication year. Must be in YYYY-MM-DD format. Note: DD is optional."
        ),
        null=True,
        blank=True,
    )
    thermal_gradient = models.ForeignKey(
        "heat_flow.ThermalGradient",
        verbose_name=_("temperature gradient"),
        help_text=_("Temperature gradient value used for heat-flow calculation."),
        on_delete=models.PROTECT,
        related_name="heat_flow_children",
        null=True,
        blank=True,
    )
    thermal_conductivity = models.ForeignKey(
        "heat_flow.IntervalConductivity",
        verbose_name=_("thermal conductivity"),
        help_text=_("Thermal conductivity value used for heat-flow calculation."),
        on_delete=models.PROTECT,
        related_name="heat_flow_children",
        null=True,
        blank=True,
    )

    c_comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comments on the child level."),
        blank=True,
        null=True,
    )

    U_score = models.CharField(
        max_length=2,
        choices=UScoreOptions.choices,
        verbose_name=_("U-score"),
        help_text=_(
            "Numerical uncertainty of the heat-flow value, graded from the uncertainty as a"
            " percentage of the value (Fuchs et al. 2023; Dergunova et al. 2026)."
            " U1 = Excellent, U2 = Good, U3 = Ok, U4 = Poor, Ux = not determined / missing data."
            " Calculated by the portal."
        ),
        default=UScoreOptions.Ux,
        editable=False,
    )
    T_score = models.FloatField(
        verbose_name=_("T-score (corrected)"),
        help_text=_(
            "The child's temperature-gradient score after its own corrections are applied, from"
            " 0.1 to 1.2. It equals the T-score the Heat Flow Quality Analysis Toolbox gives the"
            " same row. Empty means not determined. Calculated by the portal."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    T_score_missing = models.BooleanField(
        verbose_name=_("T-score reached with missing information"),
        help_text=_(
            "True when an input the corrected T-score needed was empty. Calculated by the portal."
        ),
        default=False,
        editable=False,
    )
    TC_score = models.FloatField(
        verbose_name=_("TC-score (corrected)"),
        help_text=_(
            "The child's thermal-conductivity score after its own corrections are applied, from"
            " 0.1 to 1.2. It equals the TC-score the Heat Flow Quality Analysis Toolbox gives"
            " the same row. Empty means not determined. Calculated by the portal."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    TC_score_missing = models.BooleanField(
        verbose_name=_("TC-score reached with missing information"),
        help_text=_(
            "True when an input the corrected TC-score needed was empty. Calculated by the"
            " portal."
        ),
        default=False,
        editable=False,
    )
    M_score = models.CharField(
        max_length=3,
        choices=MScoreOptions.choices,
        verbose_name=_("M-score"),
        help_text=_(
            "Methodological quality of the heat-flow value, graded from the product of the"
            " corrected T-score and TC-score (Fuchs et al. 2023; Dergunova et al. 2026)."
            " M1 = Excellent, M2 = Good, M3 = Ok, M4 = Poor, Mx = not determined / missing data."
            " A trailing x marks a grade reached with missing information. Calculated by the"
            " portal."
        ),
        default=MScoreOptions.Mx,
        editable=False,
    )
    quality = models.CharField(
        max_length=14,
        verbose_name=_("quality score"),
        help_text=_(
            "The quality code: the U-score, the M-score and the seven perturbation flags"
            " (S E T P V C R), joined by dots, for example U2.M3x.-e-PX--. Calculated by the"
            " portal."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    quality_scheme = models.CharField(
        max_length=32,
        verbose_name=_("scheme revision"),
        help_text=_(
            "The revision of the quality scheme that calculated the stored scores, for example"
            " hfqa_tool 0.2. Empty until the scores have been calculated."
        ),
        blank=True,
        default="",
        editable=False,
    )

    parent = models.ForeignKey(
        "heat_flow.ParentHeatFlow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("parent heat flow"),
        help_text=_(
            "The parent-level heat flow record this measurement contributes to."
        ),
    )
    is_relevant = models.BooleanField(
        verbose_name=_("is relevant"),
        help_text=_(
            "Indicates whether this child measurement was used in calculating the parent heat flow value."
        ),
        default=False,
    )

    ghfdb_id = models.PositiveIntegerField(
        verbose_name=_("ID Child"),
        help_text=_(
            "The original unique identifier for this record in the GHFDB schema, used for traceability."
        ),
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow")
        ordering = ["pk"]
        db_table_comment = "Global Heat Flow Database (GHFDB) child table."
        indexes = [
            models.Index(fields=["U_score"]),
            models.Index(fields=["M_score"]),
            models.Index(fields=["T_score"]),
            models.Index(fields=["TC_score"]),
        ]
        # A CheckConstraint on uncertainty is not usable with Quantity fields on SQLite;
        # the field's own validators enforce the same non-negative rule instead.
        constraints: list[models.BaseConstraint] = []

    @cached_property
    def is_probe(self):
        """Check if the heat flow measurement was acquired using a marine probe."""
        return self.sample is not None and hasattr(self.sample, "probe_metadata")

    def save(self, *args, **kwargs):
        """Reject a sample that is not a HeatFlowInterval before saving."""
        if self.sample_id and not isinstance(self.sample, HeatFlowInterval):
            raise ValidationError(
                _("HeatFlow sample must be a HeatFlowInterval instance.")
            )
        super().save(*args, **kwargs)

    def refresh_quality(self) -> None:
        """Recalculate and store the child's scores, the quality code and the revision.

        Each measurement is scored by the route of its own site, then corrected by this
        child's corrections: a tilt-corrected temperature and a corrected surface and
        bottom-water correction waive the probe criteria they cover, and the in-situ
        correction must agree with a borehole conductivity's pT conditions. The write is a
        queryset ``update``, so it sends no save signal and the receivers that call this
        method do not re-enter.
        """
        statuses = dict(self.corrections.values_list("correction_type", "status"))
        t = SubScore(None)
        rules = (
            route(Reading.site(self.thermal_gradient))
            if self.thermal_gradient
            else None
        )
        if rules is not None:
            t = rules.gradient(
                self.thermal_gradient,
                tilt_corrected=statuses.get("T") == "tilt_corrected",
                bottom_water_corrected=statuses.get("SUR") == "present_corrected",
            )
        tc = SubScore(None)
        rules = (
            route(Reading.site(self.thermal_conductivity))
            if self.thermal_conductivity
            else None
        )
        if rules is not None:
            tc = rules.conductivity(
                self.thermal_conductivity, in_situ=statuses.get("IS")
            )

        u = QualityScheme.u_score(
            Reading.magnitude(self.value, "mW / m^2"),
            Reading.magnitude(self.uncertainty, "mW / m^2"),
        )
        m = QualityScheme.m_score(t, tc)
        self.U_score = u
        self.T_score, self.T_score_missing = t.value, t.missing
        self.TC_score, self.TC_score_missing = tc.value, tc.missing
        self.M_score = m
        self.quality = QualityScheme.code(
            u, m, QualityScheme.perturbation_flags(statuses)
        )
        self.quality_scheme = SCHEME_REVISION
        type(self).objects.filter(pk=self.pk).update(
            U_score=self.U_score,
            T_score=self.T_score,
            T_score_missing=self.T_score_missing,
            TC_score=self.TC_score,
            TC_score_missing=self.TC_score_missing,
            M_score=self.M_score,
            quality=self.quality,
            quality_scheme=self.quality_scheme,
        )


class ProbeMetadata(django_models.Model):
    """Supplementary metadata for calcuations made with marine heat flow probes."""

    interval = models.OneToOneField(
        "heat_flow.HeatFlowInterval",
        on_delete=models.CASCADE,
        related_name="probe_metadata",
        verbose_name=_("heat flow measurement"),
    )
    penetration = models.DecimalQuantityField(
        base_units="m",
        max_digits=5,
        decimal_places=2,
        verbose_name=_("probe penetration"),
        help_text=_("Penetration depth of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    probe_type = ConceptManyToManyField(
        vocabulary=vocabularies.ProbeType,
        verbose_name=_("probe type"),
        help_text=_("Type of heat-flow probe used for measurement."),
        blank=True,
    )
    length = models.DecimalQuantityField(
        base_units="m",
        max_digits=5,
        decimal_places=2,
        verbose_name=_("probe length"),
        help_text=_("Length of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    tilt = models.DecimalQuantityField(
        base_units="°",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("probe tilt"),
        help_text=_("Tilt angle of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(90)],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Probe Metadata")
        verbose_name_plural = _("Probe Metadata")
        db_table_comment = "Metadata for marine heat flow probe measurements"

    def __str__(self):
        """Return the interval this probe metadata belongs to."""
        return f"Probe metadata for {self.interval}"


class HeatFlowCorrection(django_models.Model):
    """Environmental and methodological corrections applied to heat flow measurements."""

    class CorrectionTypeChoices(models.TextChoices):
        IS = "IS", _("In-situ conditions")
        T = "T", _("Temperature")
        S = "S", _("Sedimentation/Subsidence")
        E = "E", _("Erosion")
        TOPO = "TOPO", _("Topographic")
        PAL = "PAL", _("Paleoclimatic")
        SUR = "SUR", _("Surface/Climatic")
        CONV = "CONV", _("Convection")
        HR = "HR", _("Heat Refraction")

    class StatusChoices(models.TextChoices):
        PRESENT_CORRECTED = "present_corrected", _("Present and corrected")
        PRESENT_NOT_CORRECTED = "present_not_corrected", _("Present and not corrected")
        PRESENT_NOT_SIGNIFICANT = (
            "present_not_significant",
            _("Present not significant"),
        )
        NOT_RECOGNIZED = "not_recognized", _("not recognized")
        CONSIDERED_P = "considered_p", _("Considered - p")
        CONSIDERED_T = "considered_t", _("Considered - t")
        CONSIDERED_PT = "considered_pt", _("Considered - pT")
        NOT_CONSIDERED = "not_considered", _("not considered")
        TILT_CORRECTED = "tilt_corrected", _("Tilt corrected")
        DRIFT_CORRECTED = "drift_corrected", _("Drift corrected")
        NOT_CORRECTED = "not_corrected", _("not corrected")
        CORRECTED = "corrected", _("Corrected")
        UNSPECIFIED = "-", _("unspecified")

    heat_flow = models.ForeignKey(
        "heat_flow.HeatFlow",
        on_delete=models.CASCADE,
        related_name="corrections",
        verbose_name=_("heat flow measurement"),
    )
    correction_type = models.CharField(
        max_length=10,
        choices=CorrectionTypeChoices.choices,
        verbose_name=_("correction type"),
        help_text=_("Type of correction applied to the heat flow measurement."),
    )
    status = models.CharField(
        max_length=25,
        choices=StatusChoices.choices,
        verbose_name=_("correction status"),
        help_text=_("Whether the correction was present and applied."),
        default=StatusChoices.UNSPECIFIED,
    )
    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("Comment regarding the applied correction."),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Heat Flow Correction")
        verbose_name_plural = _("Heat Flow Corrections")
        db_table_comment = "Corrections applied to heat flow measurements"
        unique_together = [("heat_flow", "correction_type")]
        indexes = [
            models.Index(fields=["correction_type"]),
            models.Index(fields=["status"]),
        ]

    # Valid status values per correction type.
    VALID_STATUS_FOR_TYPE: dict[str, set[str]] = {
        "IS": {
            "present_corrected",
            "present_not_corrected",
            "not_recognized",
            "not_considered",
            "tilt_corrected",
            "drift_corrected",
            "-",
        },
        "T": {
            "present_corrected",
            "present_not_corrected",
            "not_corrected",
            "corrected",
            "not_recognized",
            "not_considered",
            "-",
        },
    }
    ENVIRONMENTAL_VALID: set[str] = {
        "present_corrected",
        "present_not_corrected",
        "present_not_significant",
        "not_recognized",
        "considered_p",
        "considered_t",
        "considered_pt",
        "not_considered",
        "-",
    }
    # S, E, TOPO, PAL, SUR, CONV, HR → ENVIRONMENTAL_VALID
    _ENVIRONMENTAL_TYPES: frozenset[str] = frozenset(
        {"S", "E", "TOPO", "PAL", "SUR", "CONV", "HR"}
    )

    def __str__(self):
        """Return the correction type's label and its status."""
        return f"{self.get_correction_type_display()} - {self.status}"

    def save(self, *args, **kwargs):
        """Reject a status that is not valid for this correction's type."""
        valid: set[str] | None = None
        if self.correction_type in self.VALID_STATUS_FOR_TYPE:
            valid = self.VALID_STATUS_FOR_TYPE[self.correction_type]
        elif self.correction_type in self._ENVIRONMENTAL_TYPES:
            valid = self.ENVIRONMENTAL_VALID
        if valid is not None and self.status not in valid:
            raise ValidationError(
                _(
                    f"Status '{self.status}' is not valid for correction type '{self.correction_type}'."
                )
            )
        super().save(*args, **kwargs)


class ScoredMeasurement:
    """Stores a measurement's own score, which reads nothing from any child.

    The score is the uncorrected T-score or TC-score of the toolbox V0.2 scheme. Every child
    that uses the measurement sees the same value, and the child applies its own corrections
    when it calculates its corrected scores.
    """

    # Supplied by the model this mixin is combined with.
    pk: Any
    objects: Any

    def score_with(self, rules) -> SubScore:
        """Return this measurement's score under the rules of its route."""
        raise NotImplementedError

    def refresh_score(self) -> None:
        """Recalculate and store the score, the missing-information mark and the revision.

        The write is a queryset ``update``, so it sends no save signal and the receivers that
        call this method do not re-enter.
        """
        rules = route(Reading.site(self))
        sub_score = SubScore(None) if rules is None else self.score_with(rules)
        self.score = sub_score.value
        self.score_missing = sub_score.missing
        self.quality_scheme = SCHEME_REVISION
        type(self).objects.filter(pk=self.pk).update(
            score=self.score,
            score_missing=self.score_missing,
            quality_scheme=self.quality_scheme,
        )


class ThermalGradient(ScoredMeasurement, Measurement):
    """Temperature gradient measured over a depth interval."""

    value = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=7,
        decimal_places=2,
        db_comment="Calculated or inferred temperature gradient.",
        verbose_name=_("thermal gradient"),
        help_text=_("Mean thermal gradient measured over a given length interval."),
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    uncertainty = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=7,
        decimal_places=2,
        db_comment="Uncertainty of the thermal gradient.",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (1 sigma) of mean measured temperature gradient as estimated through"
            " error propagation from uncertainty in the top and bottom temperature determinations or deviation"
            " from the linear regression of the temperature-depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(0), MaxVal(10**5)],
    )
    corrected_value = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=5,
        decimal_places=2,
        db_comment="Mean corrected temperature gradient.",
        verbose_name=_("corrected gradient"),
        help_text=_(
            "Mean temperature gradient corrected for borehole and environmental effects."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    corrected_uncertainty = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=5,
        decimal_places=2,
        db_comment="Uncertainty of the corrected temperature gradient.",
        verbose_name=_("corrected uncertainty"),
        help_text=_(
            "Uncertainty (1 sigma) of  mean corrected temperature gradient as"
            " estimated through error propagation from uncertainty in the top and bottom temperature determinations"
            " or deviation from the linear regression of the temperature depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    method_top = ConceptManyToManyField(
        vocabulary=vocabularies.TemperatureMethod,
        verbose_name=_("method (top)"),
        help_text=_(
            "Method used for temperature determination at the top of the heat-flow determination interval."
        ),
        blank=True,
    )
    method_bottom = ConceptManyToManyField(
        vocabulary=vocabularies.TemperatureMethod,
        verbose_name=_("method (bottom)"),
        help_text=_(
            "Method used for temperature determination at the bottom of the heat-flow determination interval."
        ),
        blank=True,
    )
    shutin_top = models.PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("shut-in time (top)"),
        help_text=_(
            "Time of measurement at the interval top in relation to the end values measured during the drilling are"
            " equal to zero."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )
    shutin_bottom = models.PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("shut-in time (bottom)"),
        help_text=_(
            "Time of measurement at the interval bottom in relation to the end values measured during the drilling are"
            " equal to zero."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )
    correction_top = ConceptManyToManyField(
        vocabulary=vocabularies.TemperatureCorrection,
        verbose_name=_("correction method (top)"),
        help_text=_(
            "Approach applied to correct the temperature measurement for drilling perturbations at the top of the"
            " interval used for heat-flow determination."
        ),
        blank=True,
    )
    correction_bottom = ConceptManyToManyField(
        vocabulary=vocabularies.TemperatureCorrection,
        verbose_name=_("correction method (bottom)"),
        help_text=_(
            "Approach applied to correct the temperature measurement for drilling perturbations at the bottom of the"
            " interval used for heat-flow determination."
        ),
        blank=True,
    )
    number = models.PositiveSmallIntegerField(
        _("Number of temperature recordings"),
        help_text=_(
            "Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in"
            " probe sensing) confirming the mean temperature gradient [T_grad_mean_meas]. NOT the repetition of one"
            " measurement at a certain depth."
        ),
        blank=True,
        null=True,
    )
    temperature_top = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("temperature (top)"),
        help_text=_(
            "Mean absolute temperature at the top of the heat-flow determination interval, used to calculate the"
            " temperature gradient."
        ),
        null=True,
        blank=True,
        validators=[MinVal(-99999.99), MaxVal(99999.99)],
    )
    temperature_top_uncertainty = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("temperature uncertainty (top)"),
        help_text=_(
            "Uncertainty (1 sigma) of the mean absolute temperature at the top of the heat-flow determination"
            " interval."
        ),
        null=True,
        blank=True,
        validators=[MinVal(-99999.99), MaxVal(99999.99)],
    )
    temperature_bottom = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("temperature (bottom)"),
        help_text=_(
            "Mean absolute temperature at the bottom of the heat-flow determination interval, used to calculate the"
            " temperature gradient."
        ),
        null=True,
        blank=True,
        validators=[MinVal(-99999.99), MaxVal(99999.99)],
    )
    temperature_bottom_uncertainty = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("temperature uncertainty (bottom)"),
        help_text=_(
            "Uncertainty (1 sigma) of the mean absolute temperature at the bottom of the heat-flow determination"
            " interval."
        ),
        null=True,
        blank=True,
        validators=[MinVal(-99999.99), MaxVal(99999.99)],
    )
    score = models.FloatField(
        verbose_name=_("T-score"),
        help_text=_(
            "The gradient's own score under the toolbox V0.2 scheme (Dergunova et al. 2026), from 0.1"
            " to 1.2. It is calculated from the gradient, its interval and its site, and reads no"
            " child's corrections. Empty means not determined, because the site's exploration method"
            " selects neither rule set."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    score_missing = models.BooleanField(
        verbose_name=_("T-score reached with missing information"),
        help_text=_(
            "True when an input the T-score needed was empty, so the score takes the criterion's"
            " largest penalty without the information being known."
        ),
        default=False,
        editable=False,
    )
    quality_scheme = models.CharField(
        max_length=32,
        verbose_name=_("scheme revision"),
        help_text=_(
            "The revision of the quality scheme that calculated the stored score, for example"
            " hfqa_tool 0.2. Empty until the score has been calculated."
        ),
        blank=True,
        default="",
        editable=False,
    )

    SCORED_CONCEPT_FIELDS = ("method_top", "method_bottom")

    class Meta:
        verbose_name = _("Thermal Gradient")
        verbose_name_plural = _("Thermal Gradients")
        db_table_comment = (
            "temperature gradient data related to child heat flow measurements"
        )
        indexes = [
            models.Index(fields=["score"]),
            models.Index(fields=["number"]),
        ]
        # A CheckConstraint on corrected_uncertainty is not usable with Quantity fields on
        # SQLite; the field's own validators enforce the same non-negative rule instead.
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(number__gt=0) | models.Q(number__isnull=True),
                name="positive_temperature_recordings",
            ),
        ]

    def __str__(self):
        """String representation of the thermal gradient."""
        if self.value:
            return f"{self.value}"
        return "ThermalGradient(undefined)"

    def score_with(self, rules) -> SubScore:
        """Return the gradient's T-score under *rules*, reading no correction."""
        return rules.gradient(self)

    def is_corrected(self):
        """Check if the thermal gradient has been corrected."""
        return self.corrected_value is not None

    def save(self, *args, **kwargs):
        """Reject a sample that is not a HeatFlowInterval before saving."""
        if self.sample_id and not isinstance(self.sample, HeatFlowInterval):
            raise ValidationError(
                _("ThermalGradient sample must be a HeatFlowInterval instance.")
            )
        super().save(*args, **kwargs)


class IntervalConductivity(ScoredMeasurement, Measurement):
    """Thermal conductivity measured over a depth interval."""

    value = models.DecimalQuantityField(
        base_units="W/mK",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Mean thermal conductivity"),
        help_text=_(
            "Mean conductivity in vertical direction representative for the interval of heat-flow determination. In"
            " best case, the value reflects the true in-situ conditions for the corresponding heat-flow interval."
        ),
        validators=[MinVal(0), MaxVal(100)],
    )
    uncertainty = models.DecimalQuantityField(
        base_units="W/mK",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of mean thermal conductivity."
        ),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    source = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivitySource,
        verbose_name=_("source"),
        help_text=_(
            "Nature of the samples from which the mean thermal conductivity was determined."
        ),
        blank=True,
    )
    location = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivityLocation,
        verbose_name=_("location"),
        help_text=_("Location of conductivity data used for heat-flow calculation."),
        blank=True,
    )
    method = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivityMethod,
        verbose_name=_("method"),
        help_text=_("Method used to determine mean thermal conductivity."),
        blank=True,
    )
    saturation = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivitySaturation,
        verbose_name=_("saturation state"),
        help_text=_(
            "Saturation state of the studied rock interval studied for thermal conductivity."
        ),
        blank=True,
    )
    pT_conditions = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivityPTConditions,
        verbose_name=_("pT conditions"),
        help_text=_(
            "Qualified conditions of pressure and temperature under which the mean thermal conductivity used for the"
            " heat-flow computation was determined."
        ),
        blank=True,
    )
    pT_function = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivityPTFunction,
        verbose_name=_("pT function"),
        help_text=_(
            "Technique or approach used to correct the measured thermal conductivity towards in-situ pressure (p)"
            " and/or temperature (T)  conditions."
        ),
        blank=True,
    )
    strategy = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivityStrategy,
        verbose_name=_("averaging methodology"),
        help_text=_(
            "Strategy that was employed to estimate the thermal conductivity over the vertical interval of heat-flow"
            " determination."
        ),
        blank=True,
    )
    number = models.PositiveSmallIntegerField(
        _("number"),
        help_text=_(
            "Number of discrete conductivity determinations used to determine the mean thermal conductivity, e.g."
            " number of rock samples with a conductivity value used, or number of thermistors used by probe sensing"
            " techniques. Not the repetition of one measurement on one rock sample or one thermistor."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )
    score = models.FloatField(
        verbose_name=_("TC-score"),
        help_text=_(
            "The conductivity's own score under the toolbox V0.2 scheme (Dergunova et al. 2026), from"
            " 0.1 to 1.2. It is calculated from the conductivity, its interval and its site, and"
            " reads no child's corrections. Empty means not determined, because the site's"
            " exploration method selects neither rule set."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    score_missing = models.BooleanField(
        verbose_name=_("TC-score reached with missing information"),
        help_text=_(
            "True when an input the TC-score needed was empty, so the score takes the criterion's"
            " largest penalty without the information being known."
        ),
        default=False,
        editable=False,
    )
    quality_scheme = models.CharField(
        max_length=32,
        verbose_name=_("scheme revision"),
        help_text=_(
            "The revision of the quality scheme that calculated the stored score, for example"
            " hfqa_tool 0.2. Empty until the score has been calculated."
        ),
        blank=True,
        default="",
        editable=False,
    )

    SCORED_CONCEPT_FIELDS = (
        "source",
        "location",
        "method",
        "saturation",
        "pT_conditions",
    )

    class Meta:
        verbose_name = _("Thermal Conductivity")
        verbose_name_plural = _("Thermal Conductivities")
        db_table_comment = "Thermal conductivity determined over a given length interval (as opposed to discrete thermal conductivity)"
        indexes = [
            models.Index(fields=["number"]),
            models.Index(fields=["score"]),
        ]
        # CheckConstraints on value and uncertainty are not usable with Quantity fields on
        # SQLite; the fields' own validators enforce the same rules instead.
        constraints: list[models.BaseConstraint] = []

    def __str__(self):
        """String representation of the thermal conductivity."""
        if self.value:
            return f"{self.value}"
        return "IntervalConductivity(undefined)"

    def score_with(self, rules) -> SubScore:
        """Return the conductivity's TC-score under *rules*, reading no correction."""
        return rules.conductivity(self)

    def clean(self):
        """Validate thermal conductivity data."""
        super().clean()

        if self.value and self.uncertainty and self.uncertainty > self.value:
            raise ValidationError(
                _("Uncertainty cannot be greater than the conductivity value.")
            )

        if self.value and (self.value < 0.1 or self.value > 50):
            raise ValidationError(
                _(
                    "Thermal conductivity value seems unrealistic (should be between 0.1 and 50 W/mK)."
                )
            )

    def save(self, *args, **kwargs):
        """Reject a sample that is not a HeatFlowInterval before saving."""
        if self.sample_id and not isinstance(self.sample, HeatFlowInterval):
            raise ValidationError(
                _("IntervalConductivity sample must be a HeatFlowInterval instance.")
            )
        super().save(*args, **kwargs)
