from django.utils.translation import gettext as _
from fairdm.db import models
from heat_flow.models.measurements import HeatFlow
from polymorphic.managers import PolymorphicManager


class GHFDBManager(PolymorphicManager):
    def get_queryset(self):
        """
        Returns a queryset of HeatFlow objects that are part of the Global Heat Flow Database (GHFDB).
        This queryset can be used to filter and retrieve heat flow data from the GHFDB.
        """
        return (
            super()
            .get_queryset()
            .filter(parent__is_ghfdb=True)
            .select_related(
                "sample",  # The depth interval data associated with the heat flow child measurement
                "parent",  # The heat flow parent object (e.g. heat_flow.SurfaceHeatFlow)
                "parent__sample",  # The heat_flow.HeatFlowSite object associated with the parent heat flow
                # "parent__location",
                "thermal_gradient",  # The thermal gradient associated with the heat flow child measurement
                "thermal_conductivity",  # The thermal conductivity associated with the heat flow child measurement
            )
        )


class GHFDB(HeatFlow):
    """
    This is a proxy model for the heat_flow.HeatFlow model (e.g. child heat flow measurements) and is used to
    construct the Global Heat Flow Database (GHFDB).
    """

    objects = GHFDBManager()

    class Meta:
        proxy = True
        verbose_name = _("Global Heat Flow Database")
        verbose_name_plural = _("Global Heat Flow Database")


class GHFDBRelease(models.Model):
    """
    Model to represent a release of the Global Heat Flow Database (GHFDB).
    This model is used to track different versions of the GHFDB.
    """

    version = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Version"),
    )
    release_date = models.DateField(
        verbose_name=_("Release Date"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    file = models.FileField(
        upload_to="ghfdb/releases/",
        verbose_name=_("Release File"),
    )

    class Meta:
        verbose_name = _("GHFDB Release")
        verbose_name_plural = _("GHFDB Releases")
        ordering = ["-release_date"]
