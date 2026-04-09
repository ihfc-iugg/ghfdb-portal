"""GHFDB release tracking model."""

from django.utils.translation import gettext as _
from fairdm.db import models


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
