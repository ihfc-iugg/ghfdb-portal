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
from django.contrib.admin import SimpleListFilter
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


class ExplorePurposeListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.explo_purpose (BUG-001).

    Restricts filter choices to ``Concept`` objects belonging to the
    ``ExplorationPurpose`` vocabulary, preventing unrelated generic concepts
    from appearing in the admin sidebar (FR-013).
    """

    title = _("exploration purpose")
    parameter_name = "explo_purpose"

    def lookups(self, request, model_admin):
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        concepts = Concept.get_for_vocabulary(ExplorationPurpose).order_by("label")
        return [(c.pk, c.label) for c in concepts]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sample__heatflowinterval__sample__heatflowsite__explo_purpose__pk=self.value())
        return queryset


@admin.register(GHFDBRelease)
class GHFDBReleaseAdmin(admin.ModelAdmin):
    list_display = ("version", "release_date", "description")
    ordering = ("-release_date",)


@admin.register(GHFDB)
class GHFDBAdmin(ImportExportMixin, admin.ModelAdmin):
    """Read-only Django admin view for GHFDB flat entries with XLSX import action.

    The changelist uses ``GHFDBQuerySet.as_ghfdb_flat()`` so all annotated
    scalar columns are available as ``list_display`` attributes. Mutation of
    existing records is disabled; data enters only via the import action.

    Admin column ordering is intentionally aligned to parent-level GHFDB
    spreadsheet fields (FR-012) and includes explicit search/filter fields
    (FR-013, FR-014).

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global
          Heat Flow Database.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    list_display = (
        "get_id_parent",
        "get_q",
        "get_q_uncertainty",
        "get_name",
        "get_lat_ns",
        "get_long_ew",
        "get_elevation",
        "get_environment",
        "get_corr_hp_flag",
        "get_total_depth_md",
        "get_total_depth_tvd",
        "get_explo_method",
        "get_explo_purpose",
        "get_country",
        "get_region",
        "get_continent",
        "get_domain",
    )
    search_fields = (
        "sample__heatflowinterval__sample__name",
        "parent__local_id",
    )
    list_filter = (
        "sample__heatflowinterval__sample__heatflowsite__environment",
        "parent__corr_HP_flag",
        "sample__heatflowinterval__sample__heatflowsite__explo_method",
        ExplorePurposeListFilter,
        "sample__heatflowinterval__sample__heatflowsite__country",
        "sample__heatflowinterval__sample__heatflowsite__region",
        "sample__heatflowinterval__sample__heatflowsite__continent",
        "sample__heatflowinterval__sample__heatflowsite__domain",
    )
    list_display_links = None  # enforce read-only (no edit links)
    ordering = ("parent__local_id", "local_id")

    # --- Import configuration -------------------------------------------------------

    def get_import_resource_classes(self, request):
        return [GHFDBParentImportResource, GHFDBChildImportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat]

    # --- Export configuration ---------------------------------------------------

    def get_export_resource_classes(self, request):
        return [GHFDBExportResource]

    def get_export_formats(self):
        return [XLSX]

    def get_import_resource_kwargs(self, request, **kwargs):
        """Pass through resource kwargs; dataset defaults to None for format detection."""
        return super().get_import_resource_kwargs(request, **kwargs)

    @admin.display(description=_("ID_parent"), ordering="parent__local_id")
    def get_id_parent(self, obj):
        return getattr(obj.parent, "local_id", None)

    @admin.display(description=_("q"), ordering="p_q")
    def get_q(self, obj):
        return getattr(obj, "p_q", None)

    @admin.display(description=_("q_uncertainty"), ordering="p_q_uncertainty")
    def get_q_uncertainty(self, obj):
        return getattr(obj, "p_q_uncertainty", None)

    @admin.display(description=_("name"), ordering="site_name")
    def get_name(self, obj):
        return getattr(obj, "site_name", None)

    @admin.display(description=_("lat_NS"), ordering="lat_ns")
    def get_lat_ns(self, obj):
        return getattr(obj, "lat_ns", None)

    @admin.display(description=_("long_EW"), ordering="long_ew")
    def get_long_ew(self, obj):
        return getattr(obj, "long_ew", None)

    @admin.display(description=_("elevation"), ordering="site_elevation")
    def get_elevation(self, obj):
        return getattr(obj, "site_elevation", None)

    @admin.display(description=_("environment"), ordering="site_environment")
    def get_environment(self, obj):
        return getattr(obj, "site_environment", None)

    @admin.display(description=_("corr_HP_flag"), ordering="p_corr_hp_flag")
    def get_corr_hp_flag(self, obj):
        return getattr(obj, "p_corr_hp_flag", None)

    @admin.display(description=_("total_depth_MD"), ordering="total_depth_md")
    def get_total_depth_md(self, obj):
        return getattr(obj, "total_depth_md", None)

    @admin.display(description=_("total_depth_TVD"), ordering="total_depth_tvd")
    def get_total_depth_tvd(self, obj):
        return getattr(obj, "total_depth_tvd", None)

    @admin.display(description=_("explo_method"), ordering="site_explo_method")
    def get_explo_method(self, obj):
        return getattr(obj, "site_explo_method", None)

    @admin.display(description=_("explo_purpose"))
    def get_explo_purpose(self, obj):
        site = getattr(getattr(obj, "sample", None), "heatflowinterval", None)
        if not site or not getattr(site, "sample", None):
            return ""
        heat_flow_site = getattr(site.sample, "heatflowsite", None)
        if not heat_flow_site:
            return ""
        concepts = heat_flow_site.explo_purpose.all()
        return "; ".join(str(concept) for concept in concepts)

    @admin.display(description=_("country"), ordering="site_country")
    def get_country(self, obj):
        return getattr(obj, "site_country", None)

    @admin.display(description=_("region"), ordering="site_region")
    def get_region(self, obj):
        return getattr(obj, "site_region", None)

    @admin.display(description=_("continent"), ordering="site_continent")
    def get_continent(self, obj):
        return getattr(obj, "site_continent", None)

    @admin.display(description=_("domain"), ordering="site_domain")
    def get_domain(self, obj):
        return getattr(obj, "site_domain", None)

    def get_queryset(self, request):
        """Return the flat annotated queryset for the changelist."""
        return GHFDB.objects.as_ghfdb_flat().prefetch_related(
            "sample__heatflowinterval__sample__heatflowsite__explo_purpose"
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
