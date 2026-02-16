"""
Heat Flow Database Models

This module implements the IHFC Global Heat Flow Database structure
as described in the 2021 database specification.

The structure follows a parent-child hierarchy:
- HeatFlowSite: Represents a geographical location (parent)
- HeatFlowMeasurement: Represents depth-specific determinations (child)

Related data is normalized into separate models:
- TemperatureData: Temperature gradient measurements
- ThermalConductivityData: Thermal conductivity measurements
- Publication: Reference publications
"""

from decimal import Decimal

from django.contrib.gis.db import models as gis_models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# ============================================================================
# CHOICE DEFINITIONS
# ============================================================================


class GeographicalEnvironment(models.TextChoices):
    """Basic geographical environment types"""

    ONSHORE_CONTINENTAL = "onshore_continental", "Onshore (continental)"
    ONSHORE_LAKE = "onshore_lake", "Onshore (lake)"
    OFFSHORE_CONTINENTAL = "offshore_continental", "Offshore (continental)"
    OFFSHORE_MARINE = "offshore_marine", "Offshore (marine)"
    UNSPECIFIED = "unspecified", "Unspecified"


class ExplorationMethod(models.TextChoices):
    """Methods of subsurface access"""

    DRILLING = "drilling", "Drilling"
    MINING = "mining", "Mining"
    TUNNELING = "tunneling", "Tunneling"
    PROBING_LAKE = "probing_lake", "Probing (lake)"
    PROBING_OCEAN = "probing_ocean", "Probing (ocean)"
    UNSPECIFIED = "unspecified", "Unspecified"


class ExplorationPurpose(models.TextChoices):
    """Original purpose of excavation"""

    HYDROCARBON = "hydrocarbon", "Hydrocarbon"
    UNDERGROUND_STORAGE = "underground_storage", "Underground Storage"
    GEOTHERMAL = "geothermal", "Geothermal"
    MAPPING = "mapping", "Mapping"
    MINING = "mining", "Mining"
    TUNNELING = "tunneling", "Tunneling"
    UNSPECIFIED = "unspecified", "Unspecified"


class HeatFlowMethod(models.TextChoices):
    """Heat flow calculation methods"""

    FOURIER = "fourier", "Fourier's Law / Product / Interval Method"
    BULLARD = "bullard", "Bullard Method"
    BOOTSTRAP = "bootstrap", "Boot-strapping Method"
    OTHER = "other", "Other"


class HeatFlowTransferMechanism(models.TextChoices):
    """Dominant heat transfer mechanism"""

    CONDUCTIVE = "conductive", "Conductive"
    CONVECTIVE_UNSPECIFIED = "convective_unspecified", "Convective Unspecified"
    CONVECTIVE_UPFLOW = "convective_upflow", "Convective Upflow"
    CONVECTIVE_DOWNFLOW = "convective_downflow", "Convective Downflow"
    UNSPECIFIED = "unspecified", "Unspecified"


class ProbeType(models.TextChoices):
    """Types of heat flow probes"""

    CORER_OUTRIGGER = "corer_outrigger", "Corer-outrigger"
    BULLARD = "bullard", "Bullard Probe"
    LISTER = "lister", "Lister Violin-Bow Probe"
    EWING = "ewing", "Ewing Probe"
    OTHER = "other", "Other Probe"
    UNSPECIFIED = "unspecified", "Unspecified"


class TemperatureMethod(models.TextChoices):
    """Temperature measurement methods"""

    BHT = "bht", "Bottom Hole Temperature (uncorrected)"
    CBHT = "cbht", "Corrected Bottom Hole Temperature"
    DST = "dst", "Drill Stem Test"
    PT100 = "pt100", "PT-100 Probe"
    PT1000 = "pt1000", "PT-1000 Probe"
    LOG = "log", "Continuous Temperature Logging"
    CLOG = "clog", "Corrected Temperature Log"
    DTS = "dts", "Distributed Temperature Sensing"
    CPD = "cpd", "Curie Point/Depth Estimates"
    XENOLITH = "xenolith", "Xenolith"
    GEOTHERMOMETRY = "geothermometry", "Geothermometry"
    BSR = "bsr", "Bottom-Simulating Reflector"
    APCT = "apct", "APCT/SET-2 Ocean Drilling Tool"
    SURFACE = "surface", "Surface Temperature"


class TemperatureCorrectionMethod(models.TextChoices):
    """Methods for correcting temperature measurements"""

    HORNER = "horner", "Horner Plot"
    CYLINDER_SOURCE = "cylinder_source", "Cylinder Source Method"
    LINE_SOURCE = "line_source", "Line Source Method"
    INVERSE_MODELING = "inverse_modeling", "Inverse Numerical Modeling"
    OTHER = "other", "Other"
    UNSPECIFIED = "unspecified", "Unspecified"
    NOT_CORRECTED = "not_corrected", "Not Corrected"


class ThermalConductivitySource(models.TextChoices):
    """Source of thermal conductivity samples"""

    OUTCROP = "outcrop", "Outcrop Samples"
    CORE = "core", "Core Samples"
    CUTTINGS = "cuttings", "Cutting Samples"
    MINERAL_COMPUTATION = "mineral_computation", "Mineral Computation"
    WELL_LOG = "well_log", "Well Log Interpretation"
    CORE_LOG = "core_log", "Core-Log Integration"
    IN_SITU_PROBE = "in_situ_probe", "In-Situ Probe"
    OTHER = "other", "Other"
    UNSPECIFIED = "unspecified", "Unspecified"


class ThermalConductivitySaturation(models.TextChoices):
    """Saturation state during thermal conductivity measurement"""

    DRY_MEASURED = "drymeas", "Dry Measured"
    SATURATED_MEASURED = "satmeas", "Saturated Measured"
    IN_SITU_SATURATED = "insitusatmeas", "In-Situ Saturated Measured"
    CORE_SATURATED = "coresatmeas", "Core Saturated Measured"
    SATURATED_CALCULATED = "satcalc", "Saturated Calculated"
    AS_RECOVERED = "recov", "As Recovered"
    OTHER = "other", "Other"
    UNSPECIFIED = "unspec", "Unspecified"
    NOT_APPLICABLE = "na", "N/A"


class ThermalConductivityPTConditions(models.TextChoices):
    """Pressure-Temperature conditions during measurement"""

    UNRECORDED_AMBIENT = "unrecorded_ambient", "Unrecorded Ambient pT Conditions"
    RECORDED_AMBIENT = "recorded_ambient", "Recorded Ambient pT Conditions"
    ACTUAL_IN_SITU = "actual_in_situ", "Actual In-Situ (pT) Conditions"
    REPLICATED_P = "replicated_p", "Replicated In-Situ (p)"
    REPLICATED_T = "replicated_t", "Replicated In-Situ (T)"
    REPLICATED_PT = "replicated_pt", "Replicated In-Situ (pT)"
    UNSPECIFIED = "unspecified", "Unspecified"


# ============================================================================
# ABSTRACT BASE MODELS
# ============================================================================


class TimeStampedModel(models.Model):
    """Abstract base class for models with creation/modification timestamps"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PerturbationFlags(models.Model):
    """
    Abstract base class for perturbation effect flags.
    These indicate whether corrections were applied for various effects.
    """

    flag_sedimentation = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Sedimentation Effect Corrected",
        help_text="Whether corrections for sedimentation/subsidence effects were applied",
    )
    flag_erosion = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Erosion Effect Corrected",
        help_text="Whether corrections for erosion effects were applied",
    )
    flag_topography = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Topographic Effect Corrected",
        help_text="Whether corrections for topographic effects were applied",
    )
    flag_paleoclimate = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Paleoclimatic Effect Corrected",
        help_text="Whether corrections for transient climatic effects were applied",
    )
    flag_convection = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Convection Effect Corrected",
        help_text="Whether corrections for convection effects were applied",
    )
    flag_bottom_water = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Bottom Water Temperature Corrected",
        help_text="Whether corrections for transient bottom-water temperature were applied",
    )
    flag_heat_refraction = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Heat Refraction Corrected",
        help_text="Whether corrections for heat refraction effects were applied",
    )

    class Meta:
        abstract = True


# ============================================================================
# PUBLICATION MODEL
# ============================================================================


class Publication(TimeStampedModel):
    """
    Publication references for heat flow data.
    Stores bibliographic information in structured format.
    """

    first_author = models.CharField(max_length=255)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)])
    title = models.TextField()
    journal_or_publisher = models.CharField(max_length=500, blank=True)
    doi = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="DOI",
        help_text="Digital Object Identifier",
    )

    class Meta:
        ordering = ["-year", "first_author"]
        unique_together = ["first_author", "year", "title"]

    def __str__(self):
        return f"{self.first_author} ({self.year})"

    @property
    def citation(self):
        """Return formatted citation string"""
        parts = [
            self.first_author,
            str(self.year),
            self.title,
            self.journal_or_publisher,
        ]
        if self.doi:
            parts.append(f"DOI: {self.doi}")
        return " | ".join(filter(None, parts))


# ============================================================================
# PARENT MODEL: HEAT FLOW SITE
# ============================================================================


class HeatFlowSite(TimeStampedModel):
    """
    Parent level: Represents a geographical location with heat flow data.
    Contains site-level metadata and representative surface heat flow value.
    """

    # ========== Identification ==========
    site_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Local name of the heat flow site or survey",
    )

    # ========== Geographical Location ==========
    # Using GeoDjango PointField for spatial queries
    location = gis_models.PointField(
        help_text="Geographical coordinates (longitude, latitude)",
        geography=True,
        srid=4326,  # WGS84
    )

    # Store separately for easier access and validation
    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
        help_text="Latitude in decimal degrees (-90 to +90)",
    )
    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        validators=[
            MinValueValidator(Decimal("-180")),
            MaxValueValidator(Decimal("180")),
        ],
        help_text="Longitude in decimal degrees (-180 to +180)",
    )
    elevation = models.FloatField(
        validators=[MinValueValidator(-12000), MaxValueValidator(9000)],
        help_text="Elevation in meters (positive above sea level, negative below)",
    )

    # ========== Geographical Environment ==========
    environment = models.CharField(
        max_length=50,
        choices=GeographicalEnvironment.choices,
        default=GeographicalEnvironment.UNSPECIFIED,
    )

    # ========== Heat Flow Value ==========
    heat_flow = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Terrestrial surface heat flow in mW/m²",
    )
    heat_flow_uncertainty = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Uncertainty (1-sigma) in mW/m²",
    )

    # ========== Borehole-Specific Fields ==========
    total_measured_depth = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total measured depth along borehole (m)",
    )
    total_true_vertical_depth = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="True vertical depth (m)",
    )
    exploration_method = models.CharField(
        max_length=50,
        choices=ExplorationMethod.choices,
        blank=True,
        help_text="Method of subsurface access",
    )
    exploration_purpose = models.CharField(
        max_length=50,
        choices=ExplorationPurpose.choices,
        blank=True,
        help_text="Original purpose of excavation",
    )

    # ========== Flags ==========
    flag_heat_production = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether heat production of overburden was corrected",
    )

    # ========== Comments ==========
    comments = models.TextField(blank=True, help_text="Additional comments about the site")

    # ========== Administrative Fields ==========
    # Auto-populated from spatial queries
    country = models.CharField(max_length=100, blank=True, editable=False)
    region = models.CharField(max_length=100, blank=True, editable=False)
    continent = models.CharField(max_length=50, blank=True, editable=False)

    # ========== Persistent Identifiers ==========
    doi = models.CharField(max_length=255, blank=True, verbose_name="DOI")
    ror_id = models.CharField(
        max_length=255, blank=True, verbose_name="ROR ID", help_text="Research Organization Registry ID"
    )

    class Meta:
        ordering = ["site_name"]
        indexes = [
            models.Index(fields=["site_name"]),
            models.Index(fields=["country", "region"]),
        ]

    def __str__(self):
        return f"{self.site_name} ({self.latitude:.2f}, {self.longitude:.2f})"

    def save(self, *args, **kwargs):
        """Override save to sync location PointField with lat/lon"""
        from django.contrib.gis.geos import Point

        # Create Point from longitude, latitude (note: lon first in GIS)
        self.location = Point(float(self.longitude), float(self.latitude))
        super().save(*args, **kwargs)

    @property
    def has_child_measurements(self):
        """Check if site has associated measurements"""
        return self.measurements.exists()

    @property
    def measurement_count(self):
        """Count of child measurements"""
        return self.measurements.count()


# ============================================================================
# CHILD MODEL: HEAT FLOW MEASUREMENT
# ============================================================================


class HeatFlowMeasurement(TimeStampedModel, PerturbationFlags):
    """
    Child level: Represents a depth-specific heat flow determination.
    Related to a parent HeatFlowSite via foreign key.
    """

    # ========== Parent Relationship ==========
    site = models.ForeignKey(
        HeatFlowSite,
        on_delete=models.CASCADE,
        related_name="measurements",
        help_text="Parent heat flow site",
    )

    # ========== Heat Flow Data ==========
    heat_flow = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        help_text="Heat flow value for this interval (mW/m²)",
    )
    heat_flow_uncertainty = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Uncertainty (1-sigma) in mW/m²",
    )
    heat_flow_method = models.CharField(
        max_length=50,
        choices=HeatFlowMethod.choices,
        help_text="Calculation method",
    )
    heat_flow_method_details = models.TextField(blank=True, help_text="Additional details if method is 'other'")

    # ========== Depth Interval ==========
    interval_top = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="True vertical depth of interval top (m)",
    )
    interval_bottom = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="True vertical depth of interval bottom (m) - for boreholes",
    )

    # ========== Marine Probe Specific ==========
    penetration_depth = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(Decimal("999.99"))],
        help_text="Probe penetration depth (m) - for marine probes",
    )
    probe_type = models.CharField(
        max_length=50,
        choices=ProbeType.choices,
        blank=True,
        help_text="Type of heat flow probe used",
    )
    probe_length = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(Decimal("999.99"))],
        help_text="Length of probe (m)",
    )
    probe_tilt = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(99)],
        help_text="Probe tilt angle (degrees)",
    )
    bottom_water_temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(Decimal("999.99"))],
        help_text="Seafloor temperature (°C)",
    )

    # ========== Transfer Mechanism ==========
    transfer_mechanism = models.CharField(
        max_length=50,
        choices=HeatFlowTransferMechanism.choices,
        blank=True,
        help_text="Predominant heat transfer mechanism",
    )

    # ========== Data Quality & Relevance ==========
    relevant_for_parent = models.BooleanField(
        default=True,
        help_text="Whether this child is used for parent heat flow computation",
    )
    flag_in_situ_properties = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether in-situ p-T conditions were considered for thermal conductivity",
    )
    flag_temperature_correction = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether temperature corrections were applied",
    )

    # ========== Geological Context ==========
    lithology = models.TextField(blank=True, help_text="Dominant rock type(s) - semicolon separated")
    stratigraphic_age = models.CharField(
        max_length=255, blank=True, help_text="Stratigraphic age - semicolon separated"
    )

    # ========== References ==========
    primary_reference = models.ForeignKey(
        Publication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_measurements",
        help_text="Primary publication reference",
    )
    additional_references = models.ManyToManyField(
        Publication,
        blank=True,
        related_name="additional_measurements",
        help_text="Additional publication references",
    )

    # ========== Expedition/Platform ==========
    expedition_platform = models.CharField(
        max_length=255,
        blank=True,
        help_text="Research vessel, platform, or expedition name",
    )

    # ========== Acquisition Date ==========
    acquisition_date = models.DateField(null=True, blank=True, help_text="Date of data acquisition")

    # ========== Comments ==========
    comments = models.TextField(blank=True, help_text="Additional comments about this measurement")

    # ========== Persistent Identifiers ==========
    igsn = models.TextField(
        blank=True,
        verbose_name="IGSN",
        help_text="International Geo Sample Numbers (semicolon separated)",
    )

    class Meta:
        ordering = ["site", "interval_top"]
        indexes = [
            models.Index(fields=["site", "interval_top"]),
            models.Index(fields=["acquisition_date"]),
        ]

    def __str__(self):
        return f"{self.site.site_name} - {self.interval_top}m ({self.heat_flow} mW/m²)"

    @property
    def interval_thickness(self):
        """Calculate interval thickness"""
        if self.interval_bottom and self.interval_top:
            return abs(self.interval_bottom - self.interval_top)
        return None

    @property
    def is_marine_measurement(self):
        """Check if this is a marine probe measurement"""
        return self.probe_type and self.probe_type != ProbeType.UNSPECIFIED


# ============================================================================
# RELATED MODEL: TEMPERATURE DATA
# ============================================================================


class TemperatureData(models.Model):
    """
    Temperature gradient data associated with a heat flow measurement.
    OneToOne relationship allows optional temperature data.
    """

    measurement = models.OneToOneField(
        HeatFlowMeasurement,
        on_delete=models.CASCADE,
        related_name="temperature_data",
        primary_key=True,
    )

    # ========== Measured Gradient ==========
    gradient_measured = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Mean measured temperature gradient (K/km)",
    )
    gradient_measured_uncertainty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Uncertainty in measured gradient (K/km)",
    )

    # ========== Corrected Gradient ==========
    gradient_corrected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Mean corrected temperature gradient (K/km)",
    )
    gradient_corrected_uncertainty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Uncertainty in corrected gradient (K/km)",
    )

    # ========== Measurement Methods ==========
    method_top = models.CharField(
        max_length=50,
        choices=TemperatureMethod.choices,
        help_text="Temperature measurement method at interval top",
    )
    method_bottom = models.CharField(
        max_digits=50,
        choices=TemperatureMethod.choices,
        blank=True,
        help_text="Temperature measurement method at interval bottom",
    )

    # ========== Shut-in Times ==========
    shutin_time_top = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time since drilling at top measurement (hours)",
    )
    shutin_time_bottom = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time since drilling at bottom measurement (hours)",
    )

    # ========== Correction Methods ==========
    correction_method_top = models.CharField(
        max_length=50,
        choices=TemperatureCorrectionMethod.choices,
        blank=True,
        help_text="Correction method applied at top",
    )
    correction_method_bottom = models.CharField(
        max_length=50,
        choices=TemperatureCorrectionMethod.choices,
        blank=True,
        help_text="Correction method applied at bottom",
    )

    # ========== Number of Recordings ==========
    number_of_recordings = models.PositiveIntegerField(help_text="Number of discrete temperature points used")

    class Meta:
        verbose_name_plural = "Temperature data"

    def __str__(self):
        return f"Temperature data for {self.measurement}"

    @property
    def has_corrections(self):
        """Check if corrections were applied"""
        return bool(self.gradient_corrected)


# ============================================================================
# RELATED MODEL: THERMAL CONDUCTIVITY DATA
# ============================================================================


class ThermalConductivityData(models.Model):
    """
    Thermal conductivity data associated with a heat flow measurement.
    OneToOne relationship allows optional conductivity data.
    """

    measurement = models.OneToOneField(
        HeatFlowMeasurement,
        on_delete=models.CASCADE,
        related_name="conductivity_data",
        primary_key=True,
    )

    # ========== Conductivity Value ==========
    conductivity_mean = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(Decimal("99.99"))],
        help_text="Mean thermal conductivity (W/mK)",
    )
    conductivity_uncertainty = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(Decimal("99.99"))],
        help_text="Uncertainty in thermal conductivity (W/mK)",
    )

    # ========== Sample Source ==========
    source = models.CharField(
        max_length=50,
        choices=ThermalConductivitySource.choices,
        help_text="Nature of samples used for measurement",
    )
    source_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Location where measurements were made relative to site",
    )

    # ========== Measurement Method ==========
    method = models.CharField(max_length=255, help_text="Laboratory or field measurement method")

    # ========== Saturation State ==========
    saturation = models.CharField(
        max_length=50,
        choices=ThermalConductivitySaturation.choices,
        help_text="Saturation state of samples during measurement",
    )

    # ========== Pressure-Temperature Conditions ==========
    pt_conditions = models.CharField(
        max_length=50,
        choices=ThermalConductivityPTConditions.choices,
        help_text="Pressure-temperature conditions during measurement",
    )
    pt_correction_function = models.CharField(
        max_length=255,
        blank=True,
        help_text="Correction function or reference used for p-T conditions",
    )

    # ========== Sample Statistics ==========
    number_of_samples = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(9999)],
        help_text="Number of discrete conductivity determinations",
    )

    # ========== Averaging Strategy ==========
    averaging_strategy = models.CharField(
        max_length=255,
        blank=True,
        help_text="Strategy used to estimate mean conductivity over interval",
    )

    class Meta:
        verbose_name_plural = "Thermal conductivity data"

    def __str__(self):
        return f"Conductivity data for {self.measurement}"

    @property
    def is_in_situ(self):
        """Check if measurements were made in-situ"""
        return self.source == ThermalConductivitySource.IN_SITU_PROBE


# ============================================================================
# QUALITY ASSESSMENT (Computed Properties)
# ============================================================================


class QualityMetrics:
    """
    Helper class for computing quality scores.
    Can be extended into a model if scores need to be stored.
    """

    @staticmethod
    def calculate_u_score(measurement: HeatFlowMeasurement) -> dict:
        """
        Calculate uncertainty score based on field completeness.
        Returns dict with score and contributing factors.
        """
        factors = {
            "heat_flow_uncertainty": measurement.heat_flow_uncertainty is not None,
            "has_temperature_data": hasattr(measurement, "temperature_data"),
            "has_conductivity_data": hasattr(measurement, "conductivity_data"),
        }

        if hasattr(measurement, "temperature_data"):
            factors["gradient_uncertainty"] = measurement.temperature_data.gradient_measured_uncertainty is not None

        if hasattr(measurement, "conductivity_data"):
            factors["conductivity_uncertainty"] = measurement.conductivity_data.conductivity_uncertainty is not None

        score = sum(factors.values()) / len(factors) * 100
        return {"score": score, "factors": factors}

    @staticmethod
    def calculate_m_score(measurement: HeatFlowMeasurement) -> dict:
        """
        Calculate method quality score based on methods used.
        Returns dict with score and contributing factors.
        """
        factors = {
            "has_temperature_data": hasattr(measurement, "temperature_data"),
            "has_conductivity_data": hasattr(measurement, "conductivity_data"),
            "flag_in_situ_properties": measurement.flag_in_situ_properties is True,
            "flag_temperature_correction": measurement.flag_temperature_correction is True,
        }

        if hasattr(measurement, "temperature_data"):
            temp = measurement.temperature_data
            factors["sufficient_recordings"] = temp.number_of_recordings >= 5
            factors["has_corrections"] = temp.gradient_corrected is not None

        if hasattr(measurement, "conductivity_data"):
            cond = measurement.conductivity_data
            factors["sufficient_samples"] = cond.number_of_samples >= 3
            factors["appropriate_saturation"] = cond.saturation != ThermalConductivitySaturation.UNSPECIFIED

        score = sum(factors.values()) / len(factors) * 100
        return {"score": score, "factors": factors}

    @staticmethod
    def calculate_perturbation_score(measurement: HeatFlowMeasurement) -> dict:
        """
        Calculate perturbation correction completeness.
        Returns dict with score and flag status.
        """
        perturbation_flags = [
            "flag_sedimentation",
            "flag_erosion",
            "flag_topography",
            "flag_paleoclimate",
            "flag_convection",
            "flag_bottom_water",
            "flag_heat_refraction",
        ]

        flag_status = {flag: getattr(measurement, flag, None) for flag in perturbation_flags}

        # Count how many flags are explicitly set (not None)
        set_flags = sum(1 for v in flag_status.values() if v is not None)
        total_flags = len(perturbation_flags)

        score = (set_flags / total_flags) * 100
        return {"score": score, "flags": flag_status}
