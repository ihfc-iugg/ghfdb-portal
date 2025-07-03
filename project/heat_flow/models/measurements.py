"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.utils.translation import gettext as _
from fairdm.core.models import Measurement
from fairdm.db import models
from research_vocabs.fields import ConceptField, ConceptManyToManyField

from heat_flow import vocabularies


class SurfaceHeatFlow(Measurement):
    """Database table that stores terrestrial heat flow data. This is the "parent" schema outlined in the formal structure of the database put forth by Fuchs et al (2021)."""

    value = models.QuantityField(
        verbose_name=_("heat flow"),
        base_units="mW / m^2",
        help_text=_(
            "Heat-flow density at a given location after all corrections for instrumental and environmental effects have been applied."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of the heat-flow value estimated by error propagation from"
            " uncertainty in thermal conductivity and temperature gradient, standard deviation from the average of the"
            " heat flow intervals or deviation from the linear regression of the Bullard plot."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )

    p_comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comments on the parent level."),
        blank=True,
        null=True,
    )
    corr_HP_flag = models.BooleanField(
        verbose_name=_("HP correction flag"),
        help_text=_(
            "Specifies if corrections to the calculated heat flow considers the contribution of the heat production of"
            " the overburden to the terrestrial surface heat flow q."
        ),
        null=True,
        blank=True,
        default=None,
    )
    is_ghfdb = models.BooleanField(
        verbose_name=_("GHFDB flag"),
        help_text=_("Indicates whether the data entry is part of the Global Heat Flow Database (GHFDB) or not."),
        default=True,
    )

    class Meta:
        verbose_name = _("Surface Heat Flow")
        verbose_name_plural = _("Surface Heat Flow")
        db_table_comment = "Heat flux at Earth's surface for a given HeatFlowSite. This table roughly correlates to the parent level of the GHFDB schema."

    def save(self, *args, **kwargs):
        # ensures that only one parent heat flow measurement marked as `is_ghfdb` is present on a given HeatFlowSite.
        # if self.tracker.has_changed("is_ghfdb") and self.is_ghfdb:
        #     hfsite = self.sample

        #     # update all other parent heat flow measurements on the same site to `is_ghfdb=False`
        #     hfsite.measurements.instance_of(SurfaceHeatFlow).filter(is_ghfdb=True).exclude(pk=self.pk).update(
        #         is_ghfdb=False
        #     )

        # self.name = f"{self.get_parent().name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.value}"

    @property
    def site(self):
        return self.parent

    def get_quality(self):
        """From Fuchs et al 2023 - Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database (Section 3.4 - Evaluation of the site-specific HFD quality on the parent level).

        >So far, the evaluation scheme was applied on the child level only. To provide a quality score on the parent level, several cases need to be distinguished. First, if only one child element is present, the score of this entry is simply passed to the parent level. Secondly, if more than one child element is present and all child elements were considered in the calculation of the site-specific HFD value, the poorest ranking is inherited to the parent level (Fig. 5). Thirdly, if more than one child element is present but not all of them were used to calculate a site-specific HFD, only the ones used are considered and the poorest ranking of the relevant child elements is inherited to the parent level again (cf. underlines in Fig. 5).
        """
        count = self.children.count()

        if count == 1:
            return self.children.first().get_quality()
        elif count > 1:
            # get the quality of the children that were used to calculate the parent
            children = self.children.filter(relevant_child=True)
            if children.count() == 0:
                return None
            elif children.count() == 1:
                return children.first().get_quality()
            else:
                return children.order_by("quality").first().get_quality()
        else:
            return None


class HeatFlow(Measurement):
    """Child heat flow as part of the Global Heat Flow Database. This is
    the "child" schema outlined in the formal structure of the database put
    forth by Fuchs et al (2021).
    """

    parent = models.ForeignKey(
        SurfaceHeatFlow,
        null=True,
        blank=True,
        verbose_name=_("parent"),
        help_text=_("parent heat flow site"),
        related_name="children",
        on_delete=models.CASCADE,
    )

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
    relevant_child = models.BooleanField(
        verbose_name=_("Relevant child"),
        help_text=_(
            "Specify whether the child entry is used for computation of representative location heat flow values at the"
            " parent level or not."
        ),
        default=False,
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
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
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

    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow")
        ordering = ["parent", "relevant_child"]
        db_table_comment = "Global Heat Flow Database (GHFDB) child table."

    # def __str__(self):
    # return f"HeatFlow({self.value})"

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
        cov = self.qc_uncertainty / self.qc
        if cov < 0.05:
            return 1
        elif cov < 0.15:
            return 2
        elif cov < 0.25:
            return 3
        elif cov > 0.25:
            return 4
        else:
            return None

        return None

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
        """Return the perturbation effects of the interval."""
        return None

    def get_quality(self):
        """"""


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

    class Meta:
        verbose_name = _("Thermal Gradient")
        verbose_name_plural = _("Thermal Gradients")
        db_table_comment = "temperature gradient data related to child heat flow measurements"

    # def __str__(self):
    # return self.value

    def save(self, *args, **kwargs):
        # if self.value:
        # self.sample = self.heat_flow_child.sample
        super().save(*args, **kwargs)

    def is_corrected(self):
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
