"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from django.conf import settings
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.db import models as dj_models
from django.utils.translation import gettext as _
from earth_science.models.features import Borehole
from earth_science.models.samples.intervals import GeoDepthInterval
from geoluminate.contrib.core.models import Dataset, Measurement
from geoluminate.db import models
from geoluminate.metadata import Authority, Citation, Metadata
from partial_date.fields import PartialDateField
from research_vocabs.fields import ConceptField

from heat_flow import vocabularies

from .utils import GHFDB

default_metadata = {
    "authority": Authority(
        name=_("International Heat Flow Commission"),
        short_name="IHFC",
        website="https://ihfc-iugg.org",
    ),
    "citation": Citation(
        text="Fuchs, S., et al. (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of Terrestrial Heat Flow and Applications, 4(1), pp.1-14.",
        doi="https://doi.org/10.31214/ijthfa.v4i1.62",
    ),
    "keywords": [],
    "repo_url": "https://github.com/ihfc-iugg/ghfdb-portal",
}


class HeatFlowSite(Borehole):
    environment = ConceptField(
        vocabulary=vocabularies.GeographicEnvironment,
        verbose_name=_("basic geographical environment"),
        help_text=_("Describes the general geographical setting of the heat-flow site (not the applied methodology)."),
        default="unspecified",
    )
    explo_method = ConceptField(
        vocabulary=vocabularies.ExplorationMethod,
        verbose_name=_("exploration method"),
        help_text=_(
            "Specification of the general means by which the rock was accessed by temperature sensors for the"
            " respective data entry."
        ),
        null=True,
        blank=True,
    )
    explo_purpose = ConceptField(
        vocabulary=vocabularies.ExplorationPurpose,
        verbose_name=_("exploration purpose"),
        help_text=_("Main purpose of the reconnaissance target providing access for the temperature sensors."),
        null=True,
        blank=True,
    )

    total_depth_MD = lambda self: self.length
    """Total measured depth (MD) of the borehole."""

    total_depth_TVD = lambda self: self.vertical_depth
    """Specification of the total true vertical depth below mean sea level."""

    class Meta:
        verbose_name = _("Heat flow site")
        verbose_name_plural = _("Heat flow sites")
        db_table_comment = "Represents a heat flow site in the Global Heat Flow Database (GHFDB) to which multiple parent heat flow measurements can be associated."

    class Config:
        metadata = Metadata(
            **default_metadata,
            primary_data_fields=["q"],
            description=_(
                "A heat flow site is a specific geological location where measurements of subsurface temperature gradients and thermal conductivity are conducted to determine the heat flow, or the rate of heat transfer from the Earth's interior to its surface. This site is characterized by its geographical environment, total measured depth (MD) of the borehole, total true vertical depth (TVD) below mean sea level, the exploration method used to access the rock for temperature sensing, and the primary purpose of the exploration. The data collected from a heat flow site is crucial for understanding geothermal energy potential, tectonic processes, and the thermal structure of the Earth's crust."
            ),
        )
        filterset_class = "heat_flow.filters.HeatFlowSiteFilter"
        form_class = "heat_flow.forms.HeatFlowSiteForm"
        table_class = "heat_flow.tables.HeatFlowSiteTable"
        importer_class = "heat_flow.importers.HeatFlowSiteImporter"

    def save(self, *args, **kwargs):
        if not self.top:
            self.top = 0
        # if self.tracker.has_changed("length"):
        # self.bottom = self.length

        super().save(*args, **kwargs)


class HeatFlowInterval(GeoDepthInterval):
    ALLOWED_PARENTS = [HeatFlowSite]

    class Meta:
        verbose_name = _("Depth interval")
        verbose_name_plural = _("Depth intervals")

    class Config:
        metadata = Metadata(
            **default_metadata,
            primary_data_fields=["q"],
            description=_(
                "A heat flow depth interval is a vertical depth interval within the Earth's subsurface, defined by top and bottom depth measurements, over which temperature measurements are taken to determine the terrestrial heat flow at a given location. This interval is used to assess the rate at which heat is conducted from the Earth's interior to the surface. The depth interval is characterized by its vertical extent, which allows for the analysis of temperature gradients and the calculation of heat flux. This data is crucial for understanding geothermal gradients, heat transfer processes, and the thermal structure of the Earth's crust at that location."
            ),
        )
        filterset_fields = ["lithology", "stratigraphy"]
        table_class = "heat_flow.tables.HeatFlowIntervalTable"

    def save(self, *args, **kwargs):
        # self.name = f"{self.get_parent().name} ({self.top} - {self.bottom})"
        super().save(*args, **kwargs)


class ParentHeatFlow(Measurement):
    """Database table that stores terrestrial heat flow data. This is the "parent" schema outlined in the formal structure of the database put forth by Fuchs et al (2021)."""

    ALLOWED_SAMPLE_TYPES = [HeatFlowSite]

    sample2 = models.ForeignKey(
        "HeatFlowSite",
        verbose_name=_("sample"),
        help_text=_("The sample on which the measurement was made."),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    value = models.QuantityField(
        verbose_name=_("heat flow"),
        base_units="mW / m^2",
        help_text=_(
            "Heat-flow density for the location after all corrections for instrumental and environmental effects."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of the heat-flow value [q] estimated by an error propagation from"
            " uncertainty in thermal conductivity and temperature gradient, standard deviation from the average of the"
            " heat flow intervals or deviation from the linear regression of the Bullard plot."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
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
        verbose_name = _("Heat Flow (Parent)")
        verbose_name_plural = _("Heat Flow (Parents)")
        db_table_comment = "Global Heat Flow Database (GHFDB) parent table."

    class Config:
        metadata = Metadata(
            **default_metadata,
            primary_data_fields=["q"],
            description=_(
                "Heat flow refers to the rate at which heat is transferred from the Earth's interior to its surface. This data is crucial for understanding the geothermal gradient, which indicates how temperature increases with depth beneath the Earth's surface. By analyzing heat flow, scientists can assess the thermal properties of subsurface rocks and fluids, determine the heat generation from radioactive decay within the Earth's crust, and evaluate the potential for geothermal energy resources. This data helps identify areas with higher geothermal potential, guiding the development of geothermal power plants."
            ),
        )
        filterset_fields = ["name", "value", "uncertainty", "corr_HP_flag"]
        table_class = "heat_flow.tables.ParentHeatFlowTable"

    def save(self, *args, **kwargs):
        # ensures that only one parent heat flow measurement marked as `is_ghfdb` is present on a given HeatFlowSite.
        # if self.tracker.has_changed("is_ghfdb") and self.is_ghfdb:
        #     hfsite = self.sample

        #     # update all other parent heat flow measurements on the same site to `is_ghfdb=False`
        #     hfsite.measurements.instance_of(ParentHeatFlow).filter(is_ghfdb=True).exclude(pk=self.pk).update(
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


class ChildHeatFlow(Measurement):
    """Child heat flow as part of the Global Heat Flow Database. This is
    the "child" schema outlined in the formal structure of the database put
    forth by Fuchs et al (2021).
    """

    ALLOWED_SAMPLE_TYPES = [HeatFlowInterval]

    ghfdb = GHFDB()

    parent = models.ForeignKey(
        ParentHeatFlow,
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
        help_text=_("Any kind of heat-flow value."),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_(
            "The uncertainty (expressed as one standard deviation) of the heat-flow value [qc], which is estimated by propagating errors from uncertainties in thermal conductivity and temperature gradient. Alternatively, it can be determined by the deviation from the linear regression of the Bullard plot, with preference given to corrected values over directly measured gradients."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    method = ConceptField(
        vocabulary=vocabularies.HeatFlowMethod,
        verbose_name=_("method"),
        help_text=_("Principal method of heat-flow calculation from temperature and thermal conductivity data."),
        null=True,
        blank=True,
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
        default=False,
    )

    # PROBE SENSING (MARINE) FIELDS
    probe_penetration = models.DecimalQuantityField(
        base_units="m",
        max_digits=5,
        decimal_places=2,
        verbose_name=_("probe length"),
        help_text=_("Penetration depth of marine heat-flow probe."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    probe_type = ConceptField(
        vocabulary=vocabularies.ProbeType,
        verbose_name=_("probe type"),
        help_text=_("Type of heat-flow probe used for measurement."),
        null=True,
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

    # q_date_acq = models.DateField(
    #     _("date of acquisition (YYYY-MM)"),
    #     help_text=_("Year of acquisition of the heat-flow data (may differ from publication year)"),
    #     null=True,
    #     blank=True,
    # )

    # Temperature Fields
    T_grad_mean = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=7,
        decimal_places=2,
        db_comment="Calculated or inferred temperature gradient.",
        verbose_name=_("temperature gradient"),
        help_text=_("Mean temperature gradient measured for the heat-flow determination interval."),
        null=True,
        blank=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_grad_uncertainty = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=7,
        decimal_places=2,
        db_comment="Uncertainty of the temperature gradient.",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of mean measured temperature gradient [T_grad_mean] as estimated by"
            " an error propagation from the uncertainty in the top and bottom temperature determinations or deviation"
            " from the linear regression of the temperature-depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(0), MaxVal(10**5)],
    )
    T_grad_mean_cor = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=5,
        decimal_places=2,
        db_comment="Mean corrected temperature gradient.",
        verbose_name=_("corrected gradient"),
        help_text=_(
            "Mean temperature gradient corrected for borehole (drilling/mud circulation) and environmental effects"
            " (terrain effects/topography, sedimentation, erosion, magmatic intrusions, paleoclimate, etc.). Name the"
            " correction method in the corresponding item."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_grad_uncertainty_cor = models.DecimalQuantityField(
        base_units="K/km",
        max_digits=5,
        decimal_places=2,
        db_comment="Uncertainty of the corrected temperature gradient.",
        verbose_name=_("corrected uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of  mean corrected temperature gradient [T_grad_mean_cor] as"
            " estimated by an error propagation from the uncertainty in the top and bottom temperature determinations"
            " or deviation from the linear regression of the temperature depth data."
        ),
        blank=True,
        null=True,
        validators=[MinVal(-(10**5)), MaxVal(10**5)],
    )
    T_method_top = ConceptField(
        vocabulary=vocabularies.TemperatureMethod,
        db_comment="Method used for temperature determination at the top of the heat-flow determination interval.",
        verbose_name=_("temperature method (top)"),
        help_text=_("Method used for temperature determination at the top of the heat-flow determination interval."),
        null=True,
        blank=True,
    )
    T_method_bottom = ConceptField(
        vocabulary=vocabularies.TemperatureMethod,
        db_comment="Method used for temperature determination at the bottom of the heat-flow determination interval.",
        verbose_name=_("temperature method (bottom)"),
        help_text=_("Method used for temperature determination at the bottom of the heat-flow determination interval."),
        null=True,
        blank=True,
    )
    T_shutin_top = models.PositiveIntegerQuantityField(
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
    T_shutin_bottom = models.PositiveIntegerQuantityField(
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
    T_corr_top = ConceptField(
        vocabulary=vocabularies.TemperatureCorrection,
        verbose_name=_("Temperature correction method (top)"),
        help_text=_(
            "Approach applied to correct the temperature measurement for drilling perturbations at the top of the"
            " interval used for heat-flow determination."
        ),
        null=True,
        blank=True,
    )
    T_corr_bottom = ConceptField(
        vocabulary=vocabularies.TemperatureCorrection,
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
    tc_mean = models.DecimalQuantityField(
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
    tc_uncertainty = models.DecimalQuantityField(
        base_units="W/mK",
        max_digits=4,
        decimal_places=2,
        verbose_name=_("Thermal conductivity uncertainty"),
        help_text=_("Uncertainty (one standard deviation) of mean thermal conductivity."),
        validators=[MinVal(0), MaxVal(100)],
        blank=True,
        null=True,
    )
    tc_source = ConceptField(
        vocabulary=vocabularies.ConductivitySource,
        verbose_name=_("Thermal conductivity source"),
        help_text=_("Nature of the samples from which the mean thermal conductivity was determined."),
        null=True,
        blank=True,
    )
    tc_location = ConceptField(
        vocabulary=vocabularies.ConductivityLocation,
        verbose_name=_("Thermal conductivity location"),
        help_text=_("Location of conductivity data used for heat-flow calculation."),
        null=True,
        blank=True,
    )
    tc_method = ConceptField(
        vocabulary=vocabularies.ConductivityMethod,
        verbose_name=_("Thermal conductivity method"),
        help_text=_("Method used to determine mean thermal conductivity."),
        blank=True,
        null=True,
    )
    tc_saturation = ConceptField(
        vocabulary=vocabularies.ConductivitySaturation,
        verbose_name=_("Thermal conductivity saturation"),
        help_text=_("Saturation state of the studied rock interval studied for thermal conductivity."),
        null=True,
        blank=True,
    )
    tc_pT_conditions = ConceptField(
        vocabulary=vocabularies.ConductivityPTConditions,
        verbose_name=_("Thermal conductivity pT conditions"),
        help_text=_(
            "Qualified conditions of pressure and temperature under which the mean thermal conductivity used for the"
            " heat-flow computation was determined."
        ),
        null=True,
        blank=True,
    )
    tc_pT_function = ConceptField(
        vocabulary=vocabularies.ConductivityPTFunction,
        verbose_name=_("Thermal conductivity pT assumed function"),
        help_text=_(
            "Technique or approach used to correct the measured thermal conductivity towards in-situ pressure (p)"
            " and/or temperature (T)  conditions."
        ),
        blank=True,
        null=True,
    )
    tc_strategy = ConceptField(
        vocabulary=vocabularies.ConductivityStrategy,
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

    # temperature_gradient = models.OneToOneField(
    #     "heat_flow.TemperatureGradient",
    #     verbose_name=_("temperature gradient"),
    #     help_text=_("Temperature gradient value used for heat-flow calculation."),
    #     on_delete=models.CASCADE,
    #     related_name="heat_flow_child",
    #     null=True,
    #     blank=True,
    # )

    # # Conductivity fields
    # thermal_conductivity = models.OneToOneField(
    #     "heat_flow.ChildConductivity",
    #     verbose_name=_("thermal conductivity"),
    #     help_text=_("Thermal conductivity value used for heat-flow calculation."),
    #     on_delete=models.CASCADE,
    #     related_name="heat_flow_child",
    #     null=True,
    #     blank=True,
    # )

    # IGSN = models.TextField(
    #     verbose_name="IGSN",
    #     help_text=_(
    #         "International Generic Sample Numbers (IGSN, semicolon separated) for rock samples used for laboratory"
    #         " measurements of thermal conductivity in the heat flow calculation."
    #     ),
    #     blank=True,
    #     null=True,
    # )

    # Flag Fields
    corr_IS_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("in-situ thermal properties"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
    )
    corr_T_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("in-situ thermal properties"),
        help_text=_(
            "Specifies whether the in-situ pressure and temperature conditions were considered to the reported thermal"
            " conductivity value or not."
        ),
    )
    corr_S_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("sedimentation effect"),
        help_text=_(
            "Specifies if sedimentation/subsidence effects with respect to the reported heat-flow value were present"
            " and if corrections were performed."
        ),
    )
    corr_E_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("erosion effect"),
        help_text=_(
            "Specifies if erosion effects with respect to the reported heat-flow value were present and if corrections"
            " were performed."
        ),
    )
    corr_TOPO_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("topographic effect"),
        help_text=_(
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_PAL_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("paleoclimatic effect"),
        help_text=_(
            "Specifies if topographic effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_SUR_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("in-situ thermal properties"),
        help_text=_(
            "Specifies if climatic conditions (glaciation, post-industrial warming, etc.) with respect to the reported"
            " heat-flow value were present and if corrections were performed."
        ),
    )
    corr_CONV_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("convection processes"),
        help_text=_(
            "Specifies if convection effects with respect to the reported heat-flow value were present and if"
            " corrections were performed."
        ),
    )
    corr_HR_flag = ConceptField(
        vocabulary=vocabularies.GenericFlagChoices,
        default="unspecified",
        verbose_name=_("heat refraction effect"),
        help_text=_(
            "Specifies if refraction effects, e.g., due to significant local conductivity contrasts, with respect to"
            " the reported heat-flow value were present and if corrections were performed. "
        ),
    )

    c_comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comments on the child level."),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Heat Flow (Child)")
        verbose_name_plural = _("Heat Flow (Children)")
        ordering = ["parent", "relevant_child"]
        db_table_comment = "Global Heat Flow Database (GHFDB) child table."

    class Config:
        metadata = Metadata(
            **default_metadata,
            primary_data_fields=["q"],
            description=_(
                "A child heat flow measurement refers to the heat flow data obtained from a specific, typically vertical, depth interval within a larger dataset, such as that from a borehole. These measurements represent localized heat flow at particular depths, capturing the rate at which heat is conducted through the Earth at that specific interval. By averaging these child measurements across several depth intervals, scientists can determine the overall surface heat flow for the area. Child heat flow measurements are essential for capturing variations in thermal conductivity and temperature gradients within the subsurface, allowing for a more accurate assessment of the Earth's heat flow at the surface."
            ),
        )
        table_class = "heat_flow.tables.ChildHeatFlowTable"
        filterset_class = "heat_flow.filters.ChildHeatFlowFilter"

    def __str__(self):
        return f"ChildHeatFlow({self.value})"

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


# =========== REQUIREMENT =================
# Convert some vocabulary fields to Vocabulary tables for user with M2M fields.


# class TemperatureGradient(Measurement):
#     # Temperature Fields
#     mean = models.DecimalQuantityField(
#         base_units="K/km",
#         max_digits=7,
#         decimal_places=2,
#         db_comment="Calculated or inferred temperature gradient.",
#         verbose_name=_("temperature gradient"),
#         help_text=_("Mean temperature gradient measured for the heat-flow determination interval."),
#         null=True,
#         blank=True,
#         validators=[MinVal(-(10**5)), MaxVal(10**5)],
#     )
#     uncertainty = models.DecimalQuantityField(
#         base_units="K/km",
#         max_digits=7,
#         decimal_places=2,
#         db_comment="Uncertainty of the temperature gradient.",
#         verbose_name=_("uncertainty"),
#         help_text=_(
#             "Uncertainty (one standard deviation) of mean measured temperature gradient [T_grad_mean] as estimated by"
#             " an error propagation from the uncertainty in the top and bottom temperature determinations or deviation"
#             " from the linear regression of the temperature-depth data."
#         ),
#         blank=True,
#         null=True,
#         validators=[MinVal(0), MaxVal(10**5)],
#     )
#     corrected_mean = models.DecimalQuantityField(
#         base_units="K/km",
#         max_digits=5,
#         decimal_places=2,
#         db_comment="Mean corrected temperature gradient.",
#         verbose_name=_("corrected gradient"),
#         help_text=_(
#             "Mean temperature gradient corrected for borehole (drilling/mud circulation) and environmental effects"
#             " (terrain effects/topography, sedimentation, erosion, magmatic intrusions, paleoclimate, etc.). Name the"
#             " correction method in the corresponding item."
#         ),
#         blank=True,
#         null=True,
#         validators=[MinVal(-(10**5)), MaxVal(10**5)],
#     )
#     corrected_uncertainty = models.DecimalQuantityField(
#         base_units="K/km",
#         max_digits=5,
#         decimal_places=2,
#         db_comment="Uncertainty of the corrected temperature gradient.",
#         verbose_name=_("corrected uncertainty"),
#         help_text=_(
#             "Uncertainty (one standard deviation) of  mean corrected temperature gradient [T_grad_mean_cor] as"
#             " estimated by an error propagation from the uncertainty in the top and bottom temperature determinations"
#             " or deviation from the linear regression of the temperature depth data."
#         ),
#         blank=True,
#         null=True,
#         validators=[MinVal(-(10**5)), MaxVal(10**5)],
#     )
#     method_top = ConceptField(
#         vocabulary=vocabularies.TemperatureMethod,
#         db_comment="Method used for temperature determination at the top of the heat-flow determination interval.",
#         verbose_name=_("temperature method (top)"),
#         help_text=_("Method used for temperature determination at the top of the heat-flow determination interval."),
#         null=True,
#         blank=True,
#     )
#     method_bottom = ConceptField(
#         vocabulary=vocabularies.TemperatureMethod,
#         db_comment="Method used for temperature determination at the bottom of the heat-flow determination interval.",
#         verbose_name=_("temperature method (bottom)"),
#         help_text=_("Method used for temperature determination at the bottom of the heat-flow determination interval."),
#         null=True,
#         blank=True,
#     )
#     shutin_top = models.PositiveIntegerQuantityField(
#         base_units="hour",
#         verbose_name=_("shut-in time (top)"),
#         help_text=_(
#             "Time of measurement at the interval top in relation to the end values measured during the drilling are"
#             " equal to zero."
#         ),
#         blank=True,
#         null=True,
#         validators=[MaxVal(10000)],
#     )
#     shutin_bottom = models.PositiveIntegerQuantityField(
#         base_units="hour",
#         verbose_name=_("shut-in time (bottom)"),
#         help_text=_(
#             "Time of measurement at the interval bottom in relation to the end values measured during the drilling are"
#             " equal to zero."
#         ),
#         blank=True,
#         null=True,
#         validators=[MaxVal(10000)],
#     )
#     correction_top = ConceptField(
#         vocabulary=vocabularies.TemperatureCorrection,
#         verbose_name=_("Temperature correction method (top)"),
#         help_text=_(
#             "Approach applied to correct the temperature measurement for drilling perturbations at the top of the"
#             " interval used for heat-flow determination."
#         ),
#         null=True,
#         blank=True,
#     )
#     correction_bottom = ConceptField(
#         vocabulary=vocabularies.TemperatureCorrection,
#         verbose_name=_("Temperature correction method (bottom)"),
#         help_text=_(
#             "Approach applied to correct the temperature measurement for drilling perturbations at the bottom of the"
#             " interval used for heat-flow determination."
#         ),
#         null=True,
#         blank=True,
#     )
#     number = models.PositiveSmallIntegerField(
#         _("Number of temperature recordings"),
#         help_text=_(
#             "Number of discrete temperature points (e.g. number of used BHT values, log values or thermistors used in"
#             " probe sensing) confirming the mean temperature gradient [T_grad_mean_meas]. NOT the repetition of one"
#             " measurement at a certain depth."
#         ),
#         blank=True,
#         null=True,
#     )

#     class Meta:
#         verbose_name = _("Temperature Gradient")
#         verbose_name_plural = _("Temperature Gradients")
#         db_table_comment = "temperature gradient data related to child heat flow measurements"

#     class Config:
#         metadata = Metadata(
#             **default_metadata,
#             primary_data_fields=["mean"],
#             description=_(
#                 "A thermal gradient refers to the rate of temperature change with depth in the Earth's crust and mantle. It reflects how heat flows from the Earth's hot interior toward its cooler surface, driven by conduction, convection, and sometimes advection. Thermal gradient is typically measured in degrees Celsius per kilometer (°C/km) and varies depending on local geological conditions, such as rock composition and tectonic activity. In regions with high geothermal activity, the thermal gradient is steeper, indicating rapid heat flow, whereas stable cratons tend to have lower gradients. Understanding thermal gradients helps geoscientists study Earth's geothermal energy potential and processes like plate tectonics and mantle convection."
#             ),
#         )
#         filterset_class = "heat_flow.filters.HeatFlowSiteFilter"
#         table_class = "heat_flow.tables.HeatFlowSiteTable"

#     def save(self, *args, **kwargs):
#         if self.heat_flow:
#             self.sample = self.heat_flow.sample
#         super().save(*args, **kwargs)


# class ChildConductivity(models.Model):
#     mean = models.DecimalQuantityField(
#         base_units="W/mK",
#         max_digits=4,
#         decimal_places=2,
#         verbose_name=_("Mean thermal conductivity"),
#         help_text=_(
#             "Mean conductivity in vertical direction representative for the interval of heat-flow determination. In"
#             " best case, the value reflects the true in-situ conditions for the corresponding heat-flow interval."
#         ),
#         null=True,
#         blank=True,
#         validators=[MinVal(0), MaxVal(100)],
#     )
#     uncertainty = models.DecimalQuantityField(
#         base_units="W/mK",
#         max_digits=4,
#         decimal_places=2,
#         verbose_name=_("Thermal conductivity uncertainty"),
#         help_text=_("Uncertainty (one standard deviation) of mean thermal conductivity."),
#         validators=[MinVal(0), MaxVal(100)],
#         blank=True,
#         null=True,
#     )
#     source = ConceptField(
#         vocabulary=vocabularies.ConductivitySource,
#         verbose_name=_("Thermal conductivity source"),
#         help_text=_("Nature of the samples from which the mean thermal conductivity was determined."),
#         null=True,
#         blank=True,
#     )
#     location = ConceptField(
#         vocabulary=vocabularies.ConductivityLocation,
#         verbose_name=_("Thermal conductivity location"),
#         help_text=_("Location of conductivity data used for heat-flow calculation."),
#         null=True,
#         blank=True,
#     )
#     method = ConceptField(
#         vocabulary=vocabularies.ConductivityMethod,
#         verbose_name=_("Thermal conductivity method"),
#         help_text=_("Method used to determine mean thermal conductivity."),
#         blank=True,
#         null=True,
#     )
#     saturation = ConceptField(
#         vocabulary=vocabularies.ConductivitySaturation,
#         verbose_name=_("Thermal conductivity saturation"),
#         help_text=_("Saturation state of the studied rock interval studied for thermal conductivity."),
#         null=True,
#         blank=True,
#     )
#     pT_conditions = ConceptField(
#         vocabulary=vocabularies.ConductivityPTConditions,
#         verbose_name=_("Thermal conductivity pT conditions"),
#         help_text=_(
#             "Qualified conditions of pressure and temperature under which the mean thermal conductivity used for the"
#             " heat-flow computation was determined."
#         ),
#         null=True,
#         blank=True,
#     )
#     pT_function = ConceptField(
#         vocabulary=vocabularies.ConductivityPTFunction,
#         verbose_name=_("Thermal conductivity pT assumed function"),
#         help_text=_(
#             "Technique or approach used to correct the measured thermal conductivity towards in-situ pressure (p)"
#             " and/or temperature (T)  conditions."
#         ),
#         blank=True,
#         null=True,
#     )
#     strategy = ConceptField(
#         vocabulary=vocabularies.ConductivityStrategy,
#         verbose_name=_("Thermal conductivity averaging methodology"),
#         help_text=_(
#             "Strategy that was employed to estimate the thermal conductivity over the vertical interval of heat-flow"
#             " determination."
#         ),
#         null=True,
#         blank=True,
#     )
#     number = models.PositiveSmallIntegerField(
#         _("Thermal conductivity number"),
#         help_text=_(
#             "Number of discrete conductivity determinations used to determine the mean thermal conductivity, e.g."
#             " number of rock samples with a conductivity value used, or number of thermistors used by probe sensing"
#             " techniques. Not the repetition of one measurement on one rock sample or one thermistor."
#         ),
#         blank=True,
#         null=True,
#         validators=[MaxVal(10000)],
#     )

#     class Meta:
#         verbose_name = _("Child Thermal Conductivity")
#         verbose_name_plural = _("Child Thermal Conductivities")
#         db_table_comment = "thermal conductivity data related to child heat flow measurements"


class Review(dj_models.Model):
    reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("reviewers"),
        help_text=_("Users who have reviewed the data."),
        related_name="heat_flow_reviews",
    )

    dataset = models.OneToOneField(
        "fairdm.Dataset",
        verbose_name=_("dataset"),
        help_text=_("The dataset that was reviewed."),
        on_delete=models.CASCADE,
        related_name="review",
    )

    literature = models.OneToOneField(
        "literature.LiteratureItem",
        verbose_name=_("literature"),
        help_text=_("The literature item that was reviewed."),
        on_delete=models.CASCADE,
        related_name="review",
    )

    start_date = PartialDateField(
        verbose_name=_("start date"),
        help_text=_("Date the review started."),
    )

    completion_date = PartialDateField(
        verbose_name=_("completion date"),
        help_text=_("Date the review was completed."),
        null=True,
        blank=True,
    )

    status = models.IntegerField(
        choices=[
            (1, _("Review pending")),
            (2, _("Review accepted")),
            (0, _("Review rejected")),
        ],
        default=1,
        verbose_name=_("status"),
        help_text=_("The status of the review."),
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comment on the review."),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        if not kwargs.get("pk") and not self.dataset_id:
            self.dataset = Dataset.objects.create(name=self.literature.title)
        super().save(*args, **kwargs)
