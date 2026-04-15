"""GHFDB release tracking model and proxy model for flat export/admin views."""

from django.utils.translation import gettext_lazy as _
from fairdm.db import models
from heat_flow.models import HeatFlow

from .managers import GHFDBManager


class GHFDBRelease(models.Model):
    """Tracks different release versions of the Global Heat Flow Database."""

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
        db_table = "ghfdb_ghfdbrelease"
        ordering = ["-release_date"]


class GHFDB(HeatFlow):
    """Proxy model over ``HeatFlow`` providing a flat read-oriented view of the
    Global Heat Flow Database.

    Provides a custom manager (``GHFDBManager``) with two key methods:
    - ``as_ghfdb_flat()`` — annotates all scalar GHFDB columns (≤2 queries).
    - ``for_export()`` — additionally pre-fetches all M2M relations (~16 queries).

    This proxy is intentionally read-only and registered as a Django admin view
    only. It does not participate in the FairDM sample/measurement registry.

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
          Flow Database. Earth System Science Data.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    objects = GHFDBManager()

    class Meta:
        proxy = True
        verbose_name = _("GHFDB Entry")
        verbose_name_plural = _("GHFDB Entries")

    def __str__(self) -> str:
        return f"GHFDB Entry #{self.pk}"
