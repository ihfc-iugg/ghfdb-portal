"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from django.utils.translation import gettext as _
from fairdm_geo.models.features import Borehole
from fairdm_geo.models.samples.intervals import GeoDepthInterval
from research_vocabs.fields import ConceptField

from heat_flow import vocabularies


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
        verbose_name = _("Heat Flow Site")
        verbose_name_plural = _("Heat Flow Sites")
        db_table_comment = "A geographic location where heat flow data has been collected. Multiple heat flow measurements may be associated with a single site."

    def save(self, *args, **kwargs):
        if not self.top:
            self.top = 0
        super().save(*args, **kwargs)


class HeatFlowInterval(GeoDepthInterval):
    class Meta:
        verbose_name = _("Depth interval")
        verbose_name_plural = _("Depth intervals")

    def save(self):
        super().save()

    # def __str__(self):
    #     top = self.top.magnitude if self.top is not None else "?"
    #     bottom = self.bottom if self.bottom is not None else "?"
    #     return f"{self.__class__.__name__}({top}-{bottom})"
