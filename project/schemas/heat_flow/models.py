"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

# PRIMARY_DATA_FIELDS = ["q"]
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.utils.translation import gettext as _
from geoluminate.contrib.samples.models import Measurement
from geoluminate.db import models
from geoluminate.utils.generic import max_length_from_choices
from research_vocabs.fields import ConceptField

from project.schemas.heat_flow import vocabularies


class HeatFlow(Measurement):
    """Database table that stores terrestrial heat flow data. This is the "parent" schema outlined in the formal structure of the database put forth by Fuchs et al (2021)."""

    q = models.QuantityField(
        verbose_name=_("heat flow"),
        base_units="mW / m^2",
        help_text=_(
            "Heat-flow density for the location after all corrections for instrumental and environmental effects."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    q_uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of the heat-flow value [q] estimated by an error propagation from"
            " uncertainty in thermal conductivity and temperature gradient, standard deviation from the average of the"
            " heat flow intervals or deviation from the linear regression of the Bullard plot."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
    )
    environment = models.CharField(
        max_length=255,
        verbose_name=_("basic geographical environment"),
        help_text=_("Describes the general geographical setting of the heat-flow site (not the applied methodology)."),
        choices=vocabularies.GeographicEnvironment.choices,
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
    total_depth_MD = models.QuantityField(
        base_units="m",
        verbose_name=_("total measured depth"),
        help_text=_("Total measured depth (MD) of the borehole."),
        validators=[MinVal(-12000), MaxVal(9000)],
        null=True,
        blank=True,
    )
    total_depth_TVD = models.QuantityField(
        base_units="m",
        verbose_name=_("total true vertical depth"),
        help_text=_("Specification of the total true vertical depth below mean sea level."),
        validators=[MinVal(-12000), MaxVal(9000)],
        null=True,
        blank=True,
    )
    explo_method = models.CharField(
        max_length=255,
        verbose_name=_("exploration method"),
        help_text=_(
            "Specification of the general means by which the rock was accessed by temperature sensors for the"
            " respective data entry."
        ),
        choices=vocabularies.ExplorationMethod.choices,
        null=True,
        blank=True,
    )
    explo_purpose = models.CharField(
        max_length=255,
        verbose_name=_("exploration purpose"),
        help_text=_("Main purpose of the reconnaissance target providing access for the temperature sensors."),
        choices=vocabularies.ExplorationPurpose.choices,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow (Parent)")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<HF Parent: {self.q} lat={self.lat_NS:.5f} lon={self.long_EW:.5f}>"

    @property
    def name(self):
        return self.get_sample.title

    @property
    def lat_NS(self):
        return self.get_location.point.y

    @property
    def long_EW(self):
        return self.get_location.point.x

    @property
    def elevation(self):
        return self.get_location.elevation

    @property
    def q_comment(self):
        return self.get_sample.comment

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


class HeatFlowChild(Measurement):
    """Child heat flow as part of the Global Heat Flow Database. This is
    the "child" schema outlined in the formal structure of the database put
    forth by Fuchs et al (2021).
    """

    PRIMARY_DATA_FIELDS = ["qc"]

    sample = None

    parent = models.ForeignKey(
        HeatFlow,
        null=True,
        blank=True,
        verbose_name=_("parent"),
        help_text=_("parent heat flow site"),
        related_name="children",
        on_delete=models.CASCADE,
    )

    # HEAT FLOW DENSITY FIELDS
    qc = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow (child)"),
        help_text=_("Any kind of heat-flow value."),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    qc_uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow uncertainty"),
        # help_text=_(
        #     "Uncertainty (one standard deviation) of the heat-flow value [qc] estimated by an error propagation from"
        #     " uncertainty in thermal conductivity and temperature gradient or deviation from the linear regression of"
        #     " the Bullard plot (corrected preferred over measured gradient)."
        # ),
        help_text=_(
            "The uncertainty (expressed as one standard deviation) of the heat-flow value [qc], which is estimated by propagating errors from uncertainties in thermal conductivity and temperature gradient. Alternatively, it can be determined by the deviation from the linear regression of the Bullard plot, with preference given to corrected values over directly measured gradients."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )

    q_method = models.CharField(
        max_length=255,
        choices=vocabularies.HeatFlowMethod.choices,
        verbose_name=_("method"),
        help_text=_("Principal method of heat-flow calculation from temperature and thermal conductivity data."),
        null=True,
        blank=True,
    )
    q_top = models.QuantityField(
        base_units="m",
        verbose_name=_("interval top"),
        help_text=_(
            "Describes the true vertical depth (TVD) of the top end of the heat-flow determination interval relative to"
            " the land surface/seafloor."
        ),
        validators=[MinVal(0), MaxVal(20000)],
        blank=True,
        null=True,
    )
    q_bottom = models.QuantityField(
        base_units="m",
        verbose_name=_("interval bottom"),
        help_text=_(
            "Describes the true vertical depth (TVD) of the bottom end of the heat-flow determination interval relative"
            " to the land surface."
        ),
        validators=[MinVal(0), MaxVal(20000)],
        blank=True,
        null=True,
    )

    expedition = models.CharField(
        verbose_name=_("expedition/platform/ship"),
        null=True,
        help_text=_(
            "Specification of the expedition, cruise, platform or research vessel where the marine heat flow survey was"
            " conducted."
        ),
        max_length=255,
    )

    relevant_child = models.BooleanField(
        verbose_name=_("Relevant child"),
        help_text=_(
            "Specify whether the child entry is used for computation of representative location heat flow values at the"
            " parent level or not."
        ),
        default=None,
        null=True,
        blank=True,
    )

    # PROBE SENSING
    probe_penetration = models.QuantityField(
        base_units="m",
        verbose_name=_("penetration depth"),
        help_text=_("Penetration depth of marine probe into the sediment."),
        validators=[MinVal(0), MaxVal(1000)],
        blank=True,
        null=True,
    )
    probe_type = models.CharField(
        max_length=255,
        choices=vocabularies.ProbeType.choices,
        verbose_name=_("probe type"),
        help_text=_("Type of heat-flow probe used for measurement."),
        null=True,
        blank=True,
    )
    probe_length = models.QuantityField(
        base_units="m",
        verbose_name=_("probe length"),
        help_text=_("Length of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    probe_tilt = models.QuantityField(
        base_units="degree",
        verbose_name=_("probe tilt"),
        help_text=_("Tilt of the marine heat-flow probe."),
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

    lithology = ConceptField(
        scheme=vocabularies.SimpleLithology,
        help_text=_(
            "Dominant rock type/lithology within the interval of heat-flow determination using the CGI Simple Lithology research vocabulary."
        ),
        null=True,
        blank=True,
    )

    stratigraphy = ConceptField(
        scheme=vocabularies.ISC2020,
        verbose_name=_("ISC Geologic Age"),
        help_text=_(
            "Stratigraphic age of the depth range involved in the reported heat-flow determination based on the"
            " official geologic timescale of the International Commission on Stratigraphy."
        ),
        blank=True,
        null=True,
    )

    # q_date_acq = models.DateField(
    #     _("date of acquisition (YYYY-MM)"),
    #     help_text=_("Year of acquisition of the heat-flow data (may differ from publication year)"),
    #     null=True,
    #     blank=True,
    # )

    # Temperature Fields
    T_grad_mean = models.QuantityField(
        base_units="K/km",
        verbose_name=_("Calculated or inferred temperature gradient"),
        help_text=_("Mean temperature gradient measured for the heat-flow determination interval."),
        null=True,
        blank=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_grad_uncertainty = models.QuantityField(
        base_units="K/km",
        verbose_name=_("Temperature gradient uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of mean measured temperature gradient [T_grad_mean] as estimated by"
            " an error propagation from the uncertainty in the top and bottom temperature determinations or deviation"
            " from the linear regression of the temperature-depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(0), MaxVal(10**5)],
    )
    T_grad_mean_cor = models.QuantityField(
        base_units="K/km",
        verbose_name=_("Mean temperature gradient corrected"),
        help_text=_(
            "Mean temperature gradient corrected for borehole (drilling/mud circulation) and environmental effects"
            " (terrain effects/topography, sedimentation, erosion, magmatic intrusions, paleoclimate, etc.). Name the"
            " correction method in the corresponding item."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_grad_uncertainty_cor = models.QuantityField(
        base_units="K/km",
        verbose_name=_("Corrected temperature gradient uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of  mean corrected temperature gradient [T_grad_mean_cor] as"
            " estimated by an error propagation from the uncertainty in the top and bottom temperature determinations"
            " or deviation from the linear regression of the temperature depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_method_top = models.CharField(
        max_length=255,
        choices=vocabularies.TemperatureMethod.choices,
        verbose_name=_("Temperature method (top)"),
        help_text=_("Method used for temperature determination at the top of the heat-flow determination interval."),
        null=True,
        blank=True,
    )
    T_method_bottom = models.CharField(
        max_length=255,
        choices=vocabularies.TemperatureMethod.choices,
        verbose_name=_("Temperature method (bottom)"),
        help_text=_("Method used for temperature determination at the bottom of the heat-flow determination interval."),
        null=True,
        blank=True,
    )
    T_shutin_top = models.PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("Shut-in time (top)"),
        help_text=_(
            "Time of measurement at the interval top in relation to the end values measured during the drilling are"
            " equal to zero."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )
    T_shutin_bottom = models.PositiveIntegerQuantityField(
        base_units="hour",
        verbose_name=_("Shut-in time (bottom)"),
        help_text=_(
            "Time of measurement at the interval bottom in relation to the end values measured during the drilling are"
            " equal to zero."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )
    T_correction_top = models.CharField(
        max_length=255,
        choices=vocabularies.TemperatureCorrection.choices,
        verbose_name=_("Temperature correction method (top)"),
        help_text=_(
            "Approach applied to correct the temperature measurement for drilling perturbations at the top of the"
            " interval used for heat-flow determination."
        ),
        null=True,
        blank=True,
    )
    T_correction_bottom = models.CharField(
        max_length=255,
        choices=vocabularies.TemperatureCorrection.choices,
        verbose_name=_("Temperature correction method (bottom)"),
        help_text=_(
            "Approach applied to correct the temperature measurement for drilling perturbations at the bottom of the"
            " interval used for heat-flow determination."
        ),
        null=True,
        blank=True,
    )
    T_number = models.PositiveSmallIntegerField(
        _("Number of temperature recordings"),
        help_text=_(
            "Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in"
            " probe sensing) confirming the mean temperature gradient [T_grad_mean_meas]. NOT the repetition of one"
            " measurement at a certain depth."
        ),
        blank=True,
        null=True,
    )

    # Conductivity fields
    tc_mean = models.QuantityField(
        base_units="W/mK",
        verbose_name=_("Mean thermal conductivity"),
        help_text=_(
            "Mean conductivity in vertical direction representative for the interval of heat-flow determination. In"
            " best case, the value reflects the true in-situ conditions for the corresponding heat-flow interval."
        ),
        null=True,
        blank=True,
        validators=[MinVal(0), MaxVal(100)],
    )
    tc_uncertainty = models.QuantityField(
        base_units="W/mK",
        verbose_name=_("Thermal conductivity uncertainty"),
        help_text=_("Uncertainty (one standard deviation) of mean thermal conductivity."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    tc_source = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivitySource.choices,
        verbose_name=_("Thermal conductivity source"),
        help_text=_("Nature of the samples from which the mean thermal conductivity was determined."),
        null=True,
        blank=True,
    )
    tc_location = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivityLocation.choices,
        verbose_name=_("Thermal conductivity location"),
        help_text=_("Location of conductivity data used for heat-flow calculation."),
        null=True,
        blank=True,
    )
    tc_method = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivityMethod.choices,
        verbose_name=_("Thermal conductivity method"),
        help_text=_("Method used to determine mean thermal conductivity."),
        blank=True,
        null=True,
    )
    tc_saturation = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivitySaturation.choices,
        verbose_name=_("Thermal conductivity saturation"),
        help_text=_("Saturation state of the studied rock interval studied for thermal conductivity."),
        null=True,
        blank=True,
    )
    tc_pT_conditions = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivityPTConditions.choices,
        verbose_name=_("Thermal conductivity pT conditions"),
        help_text=_(
            "Qualified conditions of pressure and temperature under which the mean thermal conductivity used for the"
            " heat-flow computation was determined."
        ),
        null=True,
        blank=True,
    )
    tc_pT_function = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivityPTFunction,
        verbose_name=_("Thermal conductivity pT assumed function"),
        help_text=_(
            "Technique or approach used to correct the measured thermal conductivity towards in-situ pressure (p)"
            " and/or temperature (T)  conditions."
        ),
        blank=True,
        null=True,
    )
    tc_strategy = models.CharField(
        max_length=255,
        choices=vocabularies.ConductivityStrategy.choices,
        verbose_name=_("Thermal conductivity averaging methodology"),
        help_text=_(
            "Strategy that was employed to estimate the thermal conductivity over the vertical interval of heat-flow"
            " determination."
        ),
        null=True,
        blank=True,
    )
    tc_number = models.PositiveSmallIntegerField(
        _("Thermal conductivity number"),
        help_text=_(
            "Number of discrete conductivity determinations used to determine the mean thermal conductivity, e.g."
            " number of rock samples with a conductivity value used, or number of thermistors used by probe sensing"
            " techniques. Not the repetition of one measurement on one rock sample or one thermistor."
        ),
        blank=True,
        null=True,
        validators=[MaxVal(10000)],
    )

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

    corr_IS_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.InSituFlagChoices.choices),
        choices=vocabularies.InSituFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag in-situ thermal properties"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
    )
    corr_T_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.TemperatureFlagChoices.choices),
        choices=vocabularies.TemperatureFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag in-situ thermal properties"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
    )

    corr_S_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag sedimentation effect (temperature/heat flow correction)"),
        help_text=_(
            "Specifies if sedimentation/subsidence effects with respect to the reported heat-flow value were present"
            " and if corrections were performed."
        ),
    )
    corr_E_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag erosion effect (heat-flow correction)"),
        help_text=_(
            "Specifies if erosion effects with respect to the reported heat-flow value were present and if corrections"
            " were performed."
        ),
    )
    corr_TOPO_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag topographic effect (heat-flow correction)"),
        help_text=_(
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_PAL_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag paleoclimatic effect (heat-flow correction)"),
        help_text=_(
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_SUR_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag in-situ thermal properties"),
        help_text=_(
            "Specifies if climatic conditions (glaciation, post-industrial warming, etc.) with respect to the reported"
            " heat-flow value were present and if corrections were performed."
        ),
    )
    corr_CONV_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag convection processes (heat-flow correction)"),
        help_text=_(
            "Specifies if convection effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_HR_flag = models.CharField(
        max_length=max_length_from_choices(vocabularies.GenericFlagChoices.choices),
        choices=vocabularies.GenericFlagChoices.choices,
        default="unspecified",
        verbose_name=_("Flag heat refraction effect (heat-flow correction)"),
        help_text=_(
            "Specifies if refraction effects, e.g., due to significant local conductivity contrasts, with respect to"
            " the reported heat-flow value were present and if corrections were performed. "
        ),
    )

    class Meta:
        verbose_name = _("Heat Flow (Child)")
        verbose_name_plural = _("Heat Flow (Children)")
        ordering = ["parent", "relevant_child", "q_top"]
        constraints = [
            models.CheckConstraint(check=models.Q(q_bottom__gt=models.F("q_top")), name="q_top_above_q_bottom")
        ]

    def __str__(self):
        return f"<HF Child ({self.q_top} - {self.q_bottom}): {self.qc}>"

    def clean(self, *args, **kwargs):
        # run the base validation
        super().clean(*args, **kwargs)

        # # Don't allow year older than 1900.
        # if self.q_date_acq is not None:
        #     if self.q_date_acq.year < 1900:
        #         raise ValidationError("Acquisition year cannot be less than 1900.")

    def interval(self, obj):
        return f"{obj.q_top}-{obj.q_bottom}"

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
