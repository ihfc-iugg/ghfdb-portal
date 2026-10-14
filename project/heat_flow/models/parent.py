"""Parent-level models for the Global Heat Flow Database (GHFDB).

Contains HeatFlowSite (the geographic measurement location) and ParentHeatFlow
(the aggregated, quality-controlled surface heat flow for that site).
Child HeatFlow records link back to ParentHeatFlow via ForeignKey.

Reference: Fuchs et al. (2021), Fuchs et al. (2023)
"""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.utils.translation import gettext_lazy as _
from fairdm.core.models import Measurement
from fairdm.db import models
from fairdm.db.models import QuantityField
from fairdm_geo.core.models import GenericEarthSample, GenericHole
from fairdm_geo.core.models import GeoDepthInterval as AbstractGeoDepthInterval
from fairdm_geo.vocabularies.odm2 import ElevationDatum, SiteType
from research_vocabs.fields import ConceptField, ConceptManyToManyField

from heat_flow import vocabularies

from ..quality import SCHEME_REVISION, MScoreOptions, QualityScheme, UScoreOptions


class HeatFlowSite(GenericHole, AbstractGeoDepthInterval, GenericEarthSample):
    """A heat flow site: a borehole with geological context and geographic information."""

    # Fields sourced from the old abstract SamplingLocation (now concrete in fairdm_geo)
    type = ConceptField(
        vocabulary=SiteType,
        default="unknown",
        verbose_name=_("type"),
        help_text=_("The type of sampling location."),
    )
    elevation_datum = ConceptField(
        vocabulary=ElevationDatum,
        default="MSL",
        verbose_name=_("elevation datum"),
        help_text=_(
            "The reference point for the elevation measurement, such as Mean Sea Level (MSL)."
        ),
    )
    elevation = QuantityField(
        base_units="m",
        unit_choices=["m", "ft"],
        null=True,
        blank=True,
        verbose_name=_("elevation"),
        help_text=_(
            "The site elevation in meters with reference to the specified elevation datum."
        ),
    )

    environment = ConceptField(
        vocabulary=vocabularies.GeographicEnvironment,
        verbose_name=_("basic geographical environment"),
        help_text=_(
            "Describes the general geographical setting of the heat-flow site (not the applied methodology)."
        ),
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
    explo_purpose = ConceptManyToManyField(
        vocabulary=vocabularies.ExplorationPurpose,
        verbose_name=_("exploration purpose"),
        help_text=_(
            "Main purpose of the reconnaissance target providing access for the temperature sensors."
        ),
        blank=True,
    )

    # adding these here for now but it would be nice to eventually automate this when the database is fully GIS-enabled
    country = models.CharField(
        max_length=100,
        verbose_name=_("country"),
        help_text=_("Country where the heat flow site is located."),
        blank=True,
        null=True,
    )
    region = models.CharField(
        max_length=100,
        verbose_name=_("region"),
        help_text=_("Region where the heat flow site is located."),
        blank=True,
        null=True,
    )
    continent = models.CharField(
        max_length=100,
        verbose_name=_("continent"),
        help_text=_("Continent where the heat flow site is located."),
        blank=True,
        null=True,
    )
    domain = models.CharField(
        max_length=100,
        verbose_name=_("domain"),
        help_text=_("Geological domain where the heat flow site is located."),
        blank=True,
        null=True,
    )

    @property
    def total_depth_MD(self):
        """Total measured depth (MD) of the borehole."""
        return self.length

    @property
    def total_depth_TVD(self):
        """Specification of the total true vertical depth below mean sea level."""
        return self.vertical_depth

    class Meta:
        verbose_name = _("Heat Flow Site")
        verbose_name_plural = _("Heat Flow Sites")
        db_table_comment = "A geographic location where heat flow data has been collected. Multiple heat flow measurements may be associated with a single site."
        indexes = [
            models.Index(fields=["country"]),
            models.Index(fields=["continent"]),
            models.Index(fields=["environment"]),
        ]

    def _check_location_uniqueness(self):
        """Refuse a location already held by another HeatFlowSite (FS-001 FR-004, FR-005).

        Binds only where ``location`` is set, and never rejects a site
        against itself.
        """
        if self.location_id:
            existing = HeatFlowSite.objects.filter(location=self.location).exclude(
                pk=self.pk
            )
            if existing.exists():
                raise ValidationError(
                    _(
                        "A HeatFlowSite already exists at coordinate pair "
                        "(%(x)s, %(y)s)."
                    )
                    % {"x": self.location.x, "y": self.location.y}
                )

    def clean(self):
        """Reject a location already held by another HeatFlowSite."""
        super().clean()
        self._check_location_uniqueness()

    def save(self, *args, **kwargs):
        """Default an unset top depth to 0 and enforce location uniqueness."""
        if not self.top:
            self.top = 0
        self._check_location_uniqueness()
        # TODO: Implement automatic geographic field population from coordinates when GIS is enabled
        # This would populate country, region, continent, domain from location coordinates
        super().save(*args, **kwargs)


class ParentHeatFlow(Measurement):
    """Database table that stores terrestrial heat flow data.

    This is the 'parent' schema outlined in the formal structure of the
    database put forth by Fuchs et al (2021).
    """

    value = models.QuantityField(
        verbose_name=_("heat flow"),
        base_units="mW / m^2",
        help_text=_(
            "Heat-flow density at a given location after all corrections for "
            "instrumental and environmental effects have been applied."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of the heat-flow value estimated "
            "by error propagation from uncertainty in thermal conductivity and "
            "temperature gradient, standard deviation from the average of the heat "
            "flow intervals or deviation from the linear regression of the Bullard plot."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    corr_HP_flag = models.BooleanField(
        verbose_name=_("HP correction flag"),
        help_text=_(
            "Specifies if corrections to the calculated heat flow considers the "
            "contribution of the heat production of the overburden to the terrestrial "
            "surface heat flow q."
        ),
        null=True,
        blank=True,
        default=None,
    )
    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comments on the parent level."),
        blank=True,
        null=True,
    )

    ghfdb_id = models.PositiveIntegerField(
        verbose_name=_("ID Parent"),
        help_text=_(
            "The original unique identifier for this record in the GHFDB schema, used for traceability."
        ),
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )
    U_score = models.CharField(
        max_length=2,
        choices=UScoreOptions.choices,
        verbose_name=_("U-score"),
        help_text=_(
            "The poorest U-score among the children this parent rests on (Fuchs et al. 2023)."
            " U1 = Excellent, U2 = Good, U3 = Ok, U4 = Poor, Ux = not determined / missing data."
            " Calculated by the portal."
        ),
        default=UScoreOptions.Ux,
        editable=False,
    )
    M_score = models.CharField(
        max_length=3,
        choices=MScoreOptions.choices,
        verbose_name=_("M-score"),
        help_text=_(
            "The poorest M-score among the children this parent rests on (Fuchs et al. 2023)."
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
            "The quality code inherited from the children: the poorest U-score, the poorest"
            " M-score and the seven perturbation flags (S E T P V C R) of the poorest child,"
            " joined by dots, for example U2.M3x.-e-PX--. Calculated by the portal."
        ),
        null=True,
        blank=True,
        editable=False,
    )
    quality_scheme = models.CharField(
        max_length=32,
        verbose_name=_("scheme revision"),
        help_text=_(
            "The revision of the quality scheme that calculated the inherited scores, for"
            " example hfqa_tool 0.2. Empty until the scores have been calculated."
        ),
        blank=True,
        default="",
        editable=False,
    )

    class Meta:
        verbose_name = _("Parent Heat Flow")
        verbose_name_plural = _("Parent Heat Flow")
        db_table_comment = (
            "Heat flux at Earth's surface for a given HeatFlowSite. This table "
            "roughly correlates to the parent level of the GHFDB schema."
        )
        indexes = [
            models.Index(fields=["ghfdb_id"]),
            models.Index(fields=["corr_HP_flag"]),
            models.Index(fields=["U_score"]),
            models.Index(fields=["M_score"]),
        ]

    def save(self, *args, **kwargs):
        """Enforce one parent record per site before saving."""
        if self.sample_id:
            if not isinstance(self.sample, HeatFlowSite):
                raise ValidationError(
                    _("ParentHeatFlow sample must be a HeatFlowSite instance.")
                )
            existing = ParentHeatFlow.objects.filter(sample=self.sample).exclude(
                pk=self.pk
            )
            if existing.exists():
                raise ValidationError(
                    _(
                        "A ParentHeatFlow already exists for site %(site)s. "
                        "Only one parent per site is allowed."
                    )
                    % {"site": self.sample}
                )
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the parent heat flow value."""
        return f"{self.value}"

    @property
    def site(self):
        """Return the HeatFlowSite this parent record belongs to."""
        return self.sample

    def refresh_quality(self) -> None:
        """Recalculate and store the quality this parent inherits from its children.

        A parent rests on its only child, marked relevant or not, because a single
        determination cannot be weighed against another. With several children it rests on
        those marked relevant, and with none of those, or no children at all, it is not
        determined. The parent's value is never written (the value is designated, not
        calculated). The write is a queryset ``update``, so it sends no save signal.
        """
        children = list(self.children.all())
        if len(children) > 1:
            children = [child for child in children if child.is_relevant]
        self.U_score, self.M_score, flags = QualityScheme.inherit(children)
        self.quality = QualityScheme.code(self.U_score, self.M_score, flags)
        self.quality_scheme = SCHEME_REVISION
        type(self).objects.filter(pk=self.pk).update(
            U_score=self.U_score,
            M_score=self.M_score,
            quality=self.quality,
            quality_scheme=self.quality_scheme,
        )
