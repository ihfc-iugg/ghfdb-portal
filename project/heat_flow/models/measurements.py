"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from functools import cached_property

from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.db import models as django_models
from django.utils.translation import gettext as _
from fairdm.core.models import Measurement
from fairdm.db import models
from research_vocabs.fields import ConceptField, ConceptManyToManyField

from heat_flow import vocabularies

from ..utils import MScoreOptions, UScoreOptions, calculate_U_score


class HeatFlowQuerySet(django_models.QuerySet):
    """Custom QuerySet for HeatFlow model with optimized queries."""

    def with_related_data(self):
        """Prefetch all related data for efficient queries."""
        return self.select_related(
            "parent", "parent__sample", "thermal_gradient", "thermal_conductivity"
        ).prefetch_related(
            "method",
            "probe_type",
            "corr_IS_flag",
            "corr_T_flag",
            "thermal_gradient__method_top",
            "thermal_gradient__method_bottom",
            "thermal_conductivity__source",
            "thermal_conductivity__location",
            "thermal_conductivity__method",
        )

    def probe_measurements(self):
        """Filter to probe measurements only."""
        return self.filter(
            django_models.Q(probe_penetration__isnull=False)
            | django_models.Q(probe_type__isnull=False)
            | django_models.Q(probe_length__isnull=False)
            | django_models.Q(probe_tilt__isnull=False)
        )

    def borehole_measurements(self):
        """Filter to borehole measurements only."""
        return self.exclude(
            django_models.Q(probe_penetration__isnull=False)
            | django_models.Q(probe_type__isnull=False)
            | django_models.Q(probe_length__isnull=False)
            | django_models.Q(probe_tilt__isnull=False)
        )

    def high_quality(self):
        """Filter to high quality measurements (U1, U2, M1, M2)."""
        return self.filter(
            U_score__in=[UScoreOptions.U1, UScoreOptions.U2], M_score__in=[MScoreOptions.M1, MScoreOptions.M2]
        )


class HeatFlowManager(django_models.Manager):
    """Custom manager for HeatFlow model."""

    def get_queryset(self):
        return HeatFlowQuerySet(self.model, using=self._db)

    def with_related_data(self):
        return self.get_queryset().with_related_data()

    def probe_measurements(self):
        return self.get_queryset().probe_measurements()

    def borehole_measurements(self):
        return self.get_queryset().borehole_measurements()

    def high_quality(self):
        return self.get_queryset().high_quality()


class HeatFlow(Measurement):
    """Child heat flow as part of the Global Heat Flow Database. This is
    the "child" schema outlined in the formal structure of the database put
    forth by Fuchs et al (2021).
    """

    U_SCORE_CHOICES = UScoreOptions

    # HEAT FLOW DENSITY FIELDS
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
        help_text=_("Principal method of heat-flow calculation from temperature and thermal conductivity data."),
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

    # PROBE SENSING (MARINE) FIELDS
    probe_penetration = models.DecimalQuantityField(
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
    probe_length = models.DecimalQuantityField(
        base_units="m",
        max_digits=5,
        decimal_places=2,
        verbose_name=_("probe length"),
        help_text=_("Length of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    probe_tilt = models.DecimalQuantityField(
        base_units="°",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("probe tilt"),
        help_text=_("Tilt angle of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(90)],
        blank=True,
        null=True,
    )

    water_temperature = models.QuantityField(
        base_units="°C",
        unit_choices=["°C", "K"],
        verbose_name=_("bottom water temperature"),
        help_text=_(
            "Seafloor temperature where surface heat-flow value (q) is taken. e.g. PT 100 or Mudline temperature for"
            " ocean drilling data."
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
    thermal_gradient = models.OneToOneField(
        "heat_flow.ThermalGradient",
        verbose_name=_("temperature gradient"),
        help_text=_("Temperature gradient value used for heat-flow calculation."),
        on_delete=models.CASCADE,
        related_name="heat_flow_child",
        null=True,
        blank=True,
    )
    thermal_conductivity = models.OneToOneField(
        "heat_flow.IntervalConductivity",
        verbose_name=_("thermal conductivity"),
        help_text=_("Thermal conductivity value used for heat-flow calculation."),
        on_delete=models.CASCADE,
        related_name="heat_flow_child",
        null=True,
        blank=True,
    )

    # This field makes absolutely no sense as IGSN refers to a sample, not a measurement. But then would it belong to
    #  a HeatFlowSite or a HeatFlowInterval? It is not clear. For now, we will keep it here on the HeatFlow child to
    # appease the import process and the GHFDB schema.
    IGSN = models.TextField(
        verbose_name="IGSN",
        help_text=_(
            "International Generic Sample Numbers (IGSN, semicolon separated) for rock samples used for laboratory"
            " measurements of thermal conductivity in the heat flow calculation."
        ),
        blank=True,
        null=True,
    )

    # Flag Fields
    corr_IS_flag = ConceptManyToManyField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (IS)"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
        blank=True,
    )
    corr_T_flag = ConceptManyToManyField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (T)"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
        blank=True,
    )
    corr_S_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (S)"),
        help_text=_(
            "Specifies if sedimentation/subsidence effects with respect to the reported heat-flow value were present"
            " and if corrections were performed."
        ),
        blank=True,
        null=True,
    )
    corr_E_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (E)"),
        help_text=_(
            "Specifies if erosion effects with respect to the reported heat-flow value were present and if corrections"
            " were performed."
        ),
        blank=True,
        null=True,
    )
    corr_TOPO_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (TOPO)"),
        help_text=_(
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
        blank=True,
        null=True,
    )
    corr_PAL_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (PAL)"),
        help_text=_(
            "Specifies if paleoclimatic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
        blank=True,
        null=True,
    )
    corr_SUR_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (SUR)"),
        help_text=_(
            "Specifies if climatic conditions (glaciation, post-industrial warming, etc.) with respect to the reported"
            " heat-flow value were present and if corrections were performed."
        ),
        blank=True,
        null=True,
    )
    corr_CONV_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (CONV)"),
        help_text=_(
            "Specifies if convection effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
        blank=True,
        null=True,
    )
    corr_HR_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("Correction (HR)"),
        help_text=_(
            "Specifies if refraction effects, e.g., due to significant local conductivity contrasts, with respect to"
            " the reported heat-flow value were present and if corrections were performed. "
        ),
        blank=True,
        null=True,
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
            "Numerical uncertainty of the heat-flow value, as defined in Fuchs et al. (2023)."
            " U1 = Excellent, U2 = Good, U3 = Ok, U4 = Poor, Ux = not determined / missing data."
        ),
        default=UScoreOptions.Ux,
    )
    M_score = models.CharField(
        max_length=2,
        choices=MScoreOptions.choices,
        verbose_name=_("M-score"),
        help_text=_(
            "Methodological quality of the heat-flow value, as defined in Fuchs et al. (2023)."
            " M1 = Excellent, M2 = Good, M3 = Ok, M4 = Poor, Mx = not determined / missing data."
        ),
        default=MScoreOptions.Mx,
    )

    # Managers
    # objects = HeatFlowManager()

    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow")
        ordering = ["pk"]
        db_table_comment = "Global Heat Flow Database (GHFDB) child table."
        indexes = [
            models.Index(fields=["U_score"]),
            models.Index(fields=["M_score"]),
        ]
        constraints = [
            # Note: Constraints with Quantity fields are commented out due to SQLite compatibility issues
            # The validators on the fields themselves provide the same validation
            # models.CheckConstraint(
            #     condition=models.Q(uncertainty__gte=0) | models.Q(uncertainty__isnull=True),
            #     name="non_negative_uncertainty",
            # ),
            # models.CheckConstraint(
            #     condition=models.Q(probe_penetration__gte=0) | models.Q(probe_penetration__isnull=True),
            #     name="non_negative_probe_penetration",
            # ),
            # models.CheckConstraint(
            #     condition=models.Q(probe_length__gte=0) | models.Q(probe_length__isnull=True),
            #     name="non_negative_probe_length",
            # ),
        ]

    @cached_property
    def is_probe(self):
        """Check if the heat flow measurement is from a probe."""
        has_penetration = bool(self.probe_penetration)
        has_probe_type = self.probe_type.exists() if self.probe_type else False
        has_length = bool(self.probe_length)
        has_tilt = bool(self.probe_tilt)
        return any([has_penetration, has_probe_type, has_length, has_tilt])

    @property
    def interval(self):
        return self.parent

    def get_U_score(self):
        """From Fuchs et al 2023 - Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database, Section 3.1. Uncertainty quantification (U-score).

        COV	U-score (Numerical uncertainty)	Ranking description
        < 5%	U1	Excellent
        5-15%	U2	Good
        15-25%	U3	Ok
        > 25%	U4	Poor
        not applicable	Ux	not determined / missing data
        """
        return calculate_U_score(self)

    def get_M_score(self):
        """From Fuchs et al 2023 - Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database, 3.2. Methodological quality evaluation of thermal conductivity and temperature gradient (M-score)."""
        return None

    def get_TC_score(self):
        """From Fuchs et al 2023 - Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database, Section 3.2.1.2 & 3.2.2.2 Thermal conductivity.

        Evaluation criteria for the thermal conductivity quality score include 1) the location, 2) the source type and saturation condition, 3) the number of conductivity measurements and 4) the pressure and temperature conditions. Table 2 shows in detail the score reductions or enhancements based on the defined threshold values. The score starts at 1.0 and varies from 0.2 to 1.2.
        """
        score = 1
        if self.tc_source == "core":
            score -= 0.2
        elif self.tc_source == "outcrop":
            score -= 0.4
        elif self.tc_source == "lab":
            score -= 0.6

    def get_perturbation_effects(self):
        """Return the perturbation effects of the interval based on correction flags."""
        effects = []

        correction_flags = [
            (self.corr_S_flag, "Sedimentation/Subsidence"),
            (self.corr_E_flag, "Erosion"),
            (self.corr_TOPO_flag, "Topographic"),
            (self.corr_PAL_flag, "Paleoclimatic"),
            (self.corr_SUR_flag, "Surface/Climatic"),
            (self.corr_CONV_flag, "Convection"),
            (self.corr_HR_flag, "Heat Refraction"),
        ]

        for flag, effect_name in correction_flags:
            if flag and hasattr(flag, "id"):
                if flag.id == "present_corrected":
                    effects.append(f"{effect_name} (corrected)")
                elif flag.id == "present_uncorrected":
                    effects.append(f"{effect_name} (uncorrected)")

        return effects if effects else None

    def get_quality(self):
        """Calculate overall quality score for the heat flow measurement."""
        return None


class ThermalGradient(Measurement):
    # Temperature Fields
    value = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=7,
        decimal_places=2,
        db_comment="Calculated or inferred temperature gradient.",
        verbose_name=_("thermal gradient"),
        help_text=_("Mean thermal gradient measured over a given length interval."),
        null=True,
        blank=True,
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
        help_text=_("Mean temperature gradient corrected for borehole and environmental effects."),
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
        help_text=_("Method used for temperature determination at the top of the heat-flow determination interval."),
        blank=True,
    )
    method_bottom = ConceptManyToManyField(
        vocabulary=vocabularies.TemperatureMethod,
        verbose_name=_("method (bottom)"),
        help_text=_("Method used for temperature determination at the bottom of the heat-flow determination interval."),
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
    score = models.FloatField(
        verbose_name=_("T-score"),
        help_text=_(
            "Score of the temperature gradient measurement, ranging from 0.0 to 1.0. A score of 1.0 indicates a"
            " high-quality measurement, while a score of 0.0 indicates a low-quality measurement."
        ),
        default=1.0,
        validators=[MinVal(0.0), MaxVal(1.0)],
    )

    class Meta:
        verbose_name = _("Thermal Gradient")
        verbose_name_plural = _("Thermal Gradients")
        db_table_comment = "temperature gradient data related to child heat flow measurements"
        indexes = [
            models.Index(fields=["score"]),
            models.Index(fields=["number"]),
        ]
        constraints = [
            # Note: Constraints with Quantity fields are commented out due to SQLite compatibility issues
            # The validators on the fields themselves provide the same validation
            # models.CheckConstraint(
            #     condition=models.Q(corrected_uncertainty__gte=0) | models.Q(corrected_uncertainty__isnull=True),
            #     name="non_negative_corrected_gradient_uncertainty",
            # ),
            models.CheckConstraint(
                condition=models.Q(number__gt=0) | models.Q(number__isnull=True), name="positive_temperature_recordings"
            ),
        ]

    def __str__(self):
        """String representation of the thermal gradient."""
        if self.value:
            return f"{self.value}"
        return "ThermalGradient(undefined)"

    def is_corrected(self):
        """Check if the thermal gradient has been corrected."""
        return self.corrected_value is not None


class IntervalConductivity(Measurement):
    value = models.DecimalQuantityField(
        base_units="W/mK",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Mean thermal conductivity"),
        help_text=_(
            "Mean conductivity in vertical direction representative for the interval of heat-flow determination. In"
            " best case, the value reflects the true in-situ conditions for the corresponding heat-flow interval."
        ),
        null=True,
        blank=True,
        validators=[MinVal(0), MaxVal(100)],
    )
    uncertainty = models.DecimalQuantityField(
        base_units="W/mK",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("uncertainty"),
        help_text=_("Uncertainty (one standard deviation) of mean thermal conductivity."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    source = ConceptManyToManyField(
        vocabulary=vocabularies.ConductivitySource,
        verbose_name=_("source"),
        help_text=_("Nature of the samples from which the mean thermal conductivity was determined."),
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
        help_text=_("Saturation state of the studied rock interval studied for thermal conductivity."),
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

    class Meta:
        verbose_name = _("Thermal Conductivity")
        verbose_name_plural = _("Thermal Conductivities")
        db_table_comment = (
            "Thermal conductivity determined over a given length interval (as opposed to discrete thermal conductivity)"
        )
        indexes = [
            models.Index(fields=["number"]),
        ]
        constraints = [
            # Note: Constraints with Quantity fields are commented out due to SQLite compatibility issues
            # The validators on the fields themselves provide the same validation
            # models.CheckConstraint(
            #     condition=models.Q(value__gt=0) | models.Q(value__isnull=True), name="positive_thermal_conductivity"
            # ),
            # models.CheckConstraint(
            #     condition=models.Q(uncertainty__gte=0) | models.Q(uncertainty__isnull=True),
            #     name="non_negative_conductivity_uncertainty",
            # ),
        ]

    def __str__(self):
        """String representation of the thermal conductivity."""
        if self.value:
            return f"{self.value}"
        return "IntervalConductivity(undefined)"

    def get_quality_score(self):
        """Calculate quality score for thermal conductivity measurement.

        Based on Fuchs et al 2023 criteria for thermal conductivity quality assessment.
        """
        score = 1.0

        # Source quality assessment
        if self.source.exists():
            source_ids = list(self.source.values_list("id", flat=True))
            if "lab" in source_ids:
                score += 0.1  # Lab measurements are preferred
            elif "core" in source_ids:
                score -= 0.1
            elif "outcrop" in source_ids:
                score -= 0.2

        # Number of measurements
        if self.number:
            if self.number >= 10:
                score += 0.1
            elif self.number >= 5:
                score += 0.05
            elif self.number < 3:
                score -= 0.1

        # Location quality
        if self.location.exists():
            location_ids = list(self.location.values_list("id", flat=True))
            if "actual" in location_ids:
                score += 0.1
            elif "literature" in location_ids:
                score -= 0.2

        # pT conditions consideration
        if self.pT_conditions.exists():
            pt_ids = list(self.pT_conditions.values_list("id", flat=True))
            if "in_situ" in pt_ids:
                score += 0.1
            elif "ambient" in pt_ids:
                score -= 0.1

        return max(0.2, min(1.2, score))

    def clean(self):
        """Validate thermal conductivity data."""
        from django.core.exceptions import ValidationError

        super().clean()

        # Validate uncertainty relative to value
        if self.value and self.uncertainty and self.uncertainty > self.value:
            raise ValidationError(_("Uncertainty cannot be greater than the conductivity value."))

        # Validate reasonable conductivity range
        if self.value and (self.value < 0.1 or self.value > 50):
            raise ValidationError(
                _("Thermal conductivity value seems unrealistic (should be between 0.1 and 50 W/mK).")
            )

    def save(self, *args, **kwargs):
        """Save with data validation."""
        super().save(*args, **kwargs)
