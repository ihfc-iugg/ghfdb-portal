"""
GHFDB admin registration.

Registers the GHFDB proxy model with read-only changelist and XLSX import
action (US2).  Import is driven by ``GHFDBImportResource`` and
``GHFDBImportFormat``.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from import_export.formats.base_formats import XLSX

from .models import GHFDB, GHFDBRelease
from .resources import (
    GHFDBChildImportResource,
    GHFDBExportResource,
    GHFDBImportFormat,
    GHFDBParentImportResource,
)


@admin.register(GHFDBRelease)
class GHFDBReleaseAdmin(admin.ModelAdmin):
    list_display = ("version", "release_date", "description")
    ordering = ("-release_date",)


@admin.register(GHFDB)
class GHFDBAdmin(ImportExportMixin, admin.ModelAdmin):
    """Read-only Django admin view for GHFDB flat entries with XLSX import action.

    The changelist uses ``GHFDBQuerySet.as_ghfdb_flat()`` so all annotated
    scalar columns are available as ``list_display`` attributes.  Mutation of
    existing records is disabled; data enters only via the import action.

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global
          Heat Flow Database.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    list_display = ("pk", "get_site_name", "get_lat_ns", "get_long_ew", "get_p_q", "value")
    list_display_links = None  # enforce read-only (no edit links)
    ordering = ("pk",)

    # --- Import configuration -------------------------------------------------------

    def get_import_resource_classes(self):
        return [GHFDBParentImportResource, GHFDBChildImportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat]

    # --- Export configuration ---------------------------------------------------

    def get_export_resource_classes(self):
        return [GHFDBExportResource]

    def get_export_formats(self):
        return [XLSX]

    def get_import_resource_kwargs(self, request, **kwargs):
        """Inject the current dataset into the resource for FK resolution."""
        kw = super().get_import_resource_kwargs(request, **kwargs)
        # Dataset is resolved from the request or set externally; default to None
        # so the resource can be instantiated without a dataset during format detection.
        kw.setdefault("dataset", None)
        return kw

    @admin.display(description=_("site name"))
    def get_site_name(self, obj):
        return getattr(obj, "site_name", None)

    @admin.display(description=_("lat (N/S)"))
    def get_lat_ns(self, obj):
        return getattr(obj, "lat_ns", None)

    @admin.display(description=_("long (E/W)"))
    def get_long_ew(self, obj):
        return getattr(obj, "long_ew", None)

    @admin.display(description=_("heat flow (mW/m²)"))
    def get_p_q(self, obj):
        return getattr(obj, "p_q", None)

    def get_queryset(self, request):
        """Return the flat annotated queryset for the changelist."""
        return GHFDB.objects.as_ghfdb_flat()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
