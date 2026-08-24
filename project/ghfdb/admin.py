"""
GHFDB admin registration.

Registers the ``GHFDBChild`` proxy model with read-only changelist and XLSX import
action (US2).  Import is driven by ``GHFDBChildImportResource`` and
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

from .columns import ColumnDisplay
from .constants import CHILD_COLUMNS
from .models import GHFDBChild, GHFDBParent, GHFDBRelease
from .resources import (
    GHFDBChildImportResource,
    GHFDBExportResource,
    GHFDBImportFormat,
    GHFDBParentImportResource,
    GHFDBSimpleImportFormat,
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
            return queryset.filter(
                sample__heatflowinterval__site__explo_purpose__pk=self.value()
            )
        return queryset


class EnvironmentListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.environment on GHFDBChild (BUG-004).

    Restricts filter choices to values defined in the ``GeographicEnvironment``
    vocabulary so the sidebar shows human-readable labels instead of raw stored
    concept keys (FR-014, FR-015).
    """

    title = _("environment")
    parameter_name = "environment"

    def lookups(self, request, model_admin):
        from heat_flow.vocabularies import GeographicEnvironment

        return GeographicEnvironment().choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                sample__heatflowinterval__site__environment=self.value()
            )
        return queryset


class ChildExplorationMethodListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.explo_method on GHFDBChild (BUG-004).

    Restricts filter choices to values defined in the ``ExplorationMethod``
    vocabulary so the sidebar shows human-readable labels instead of raw stored
    concept keys (FR-014, FR-015).
    """

    title = _("exploration method")
    parameter_name = "explo_method"

    def lookups(self, request, model_admin):
        from heat_flow.vocabularies import ExplorationMethod

        return ExplorationMethod().choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                sample__heatflowinterval__site__explo_method=self.value()
            )
        return queryset


@admin.register(GHFDBRelease)
class GHFDBReleaseAdmin(admin.ModelAdmin):
    list_display = ("version", "release_date", "description")
    ordering = ("-release_date",)


@admin.register(GHFDBChild)
class GHFDBChildAdmin(ImportExportMixin, admin.ModelAdmin):
    """Read-only changelist for the published determination view (US-3).

    Columns come entirely from ``project/ghfdb/columns.py``'s published-column
    mapping (see ``list_display`` below), so a column added to
    ``constants.CHILD_COLUMNS`` and not to that mapping is a startup failure
    rather than a silently missing column. Mutation of existing records is
    disabled; data enters only via the import action.

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global
          Heat Flow Database.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    # The four orientation columns the assessment team reads a row by — the
    # determination's own published identifier, the site's published
    # identifier, the site name and the site's two coordinate columns (D1) —
    # followed by the canonical child block. Built from `ColumnDisplay`, the
    # same mapping the tail is built from: `ID_parent`, `name`, `lat_NS` and
    # `long_EW` are all published parent columns already restated as
    # annotations on this proxy's own queryset (T081). No column list is
    # written out here beyond these four names and `ghfdb_id` itself, which
    # is not a published column.
    list_display = (
        "ghfdb_id",
        ColumnDisplay.build("ID_parent"),
        ColumnDisplay.build("name"),
        ColumnDisplay.build("lat_NS"),
        ColumnDisplay.build("long_EW"),
        *ColumnDisplay.list_display_for(CHILD_COLUMNS),
    )
    search_fields = (
        "sample__heatflowinterval__site__name",
        "parent__ghfdb_id",
        "ghfdb_id",
    )
    list_filter = (
        EnvironmentListFilter,
        "parent__corr_HP_flag",
        ChildExplorationMethodListFilter,
        ExplorePurposeListFilter,
        "sample__heatflowinterval__site__country",
        "sample__heatflowinterval__site__region",
        "sample__heatflowinterval__site__continent",
        "sample__heatflowinterval__site__domain",
    )
    list_display_links = None  # enforce read-only (no edit links)
    ordering = ("parent__ghfdb_id", "ghfdb_id")

    # --- Import configuration -------------------------------------------------------

    def get_import_resource_classes(self, request):
        return [GHFDBChildImportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat, GHFDBSimpleImportFormat]

    # --- Export configuration ---------------------------------------------------

    def get_export_resource_classes(self, request):
        return [GHFDBExportResource]

    def get_export_formats(self):
        return [XLSX]

    def get_import_resource_kwargs(self, request, **kwargs):
        """Pass through resource kwargs; dataset defaults to None for format detection."""
        return super().get_import_resource_kwargs(request, **kwargs)

    def get_queryset(self, request):
        """Return the flat annotated queryset for the changelist."""
        return GHFDBChild.objects.as_ghfdb_flat().prefetch_related(
            "method",
            "sample__heatflowinterval__site__explo_purpose",
            "sample__heatflowinterval__lithology",
            "sample__heatflowinterval__stratigraphy",
            "sample__heatflowinterval__probe_metadata__probe_type",
            "thermal_gradient__method_top",
            "thermal_gradient__method_bottom",
            "thermal_gradient__correction_top",
            "thermal_gradient__correction_bottom",
            "thermal_conductivity__source",
            "thermal_conductivity__location",
            "thermal_conductivity__method",
            "thermal_conductivity__saturation",
            "thermal_conductivity__pT_conditions",
            "thermal_conductivity__pT_function",
            "thermal_conductivity__strategy",
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ParentExplorePurposeListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.explo_purpose on GHFDBParent.

    Same vocabulary scoping as ``ExplorePurposeListFilter`` but filters via the
    parent-model FK path: ``sample__heatflowsite__explo_purpose``.
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
            return queryset.filter(sample__heatflowsite__explo_purpose__pk=self.value())
        return queryset


class ParentEnvironmentListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.environment on GHFDBParent (BUG-004).

    Same vocabulary scoping as ``EnvironmentListFilter`` but filters via the
    shorter parent-model path: ``sample__heatflowsite__environment`` (FR-014,
    FR-015).
    """

    title = _("environment")
    parameter_name = "environment"

    def lookups(self, request, model_admin):
        from heat_flow.vocabularies import GeographicEnvironment

        return GeographicEnvironment().choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sample__heatflowsite__environment=self.value())
        return queryset


class ParentExplorationMethodListFilter(SimpleListFilter):
    """Vocabulary-scoped list filter for HeatFlowSite.explo_method on GHFDBParent (BUG-004).

    Same vocabulary scoping as ``ChildExplorationMethodListFilter`` but filters
    via the shorter parent-model path: ``sample__heatflowsite__explo_method``
    (FR-014, FR-015).
    """

    title = _("exploration method")
    parameter_name = "explo_method"

    def lookups(self, request, model_admin):
        from heat_flow.vocabularies import ExplorationMethod

        return ExplorationMethod().choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sample__heatflowsite__explo_method=self.value())
        return queryset


@admin.register(GHFDBParent)
class GHFDBParentAdmin(ImportExportMixin, admin.ModelAdmin):
    """Read-only Django admin view for GHFDB Parents with parent-level import.

    Displays parent-level GHFDB spreadsheet columns plus computed child count
    columns (``total_children``, ``relevant_children``). Only the
    ``GHFDBParentImportResource`` is attached; no export resource or child import
    resource is present (FR-011b).
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
        "get_p_comment",
        "get_corr_hp_flag",
        "get_total_depth_md",
        "get_total_depth_tvd",
        "get_explo_method",
        "get_explo_purpose",
        "get_quality",
        "get_country",
        "get_region",
        "get_continent",
        "get_domain",
        "total_children",
        "relevant_children",
    )
    search_fields = (
        "sample__name",
        "ghfdb_id",
    )
    list_filter = (
        ParentEnvironmentListFilter,
        "corr_HP_flag",
        ParentExplorationMethodListFilter,
        ParentExplorePurposeListFilter,
        "sample__heatflowsite__country",
        "sample__heatflowsite__region",
        "sample__heatflowsite__continent",
        "sample__heatflowsite__domain",
    )
    list_display_links = None
    ordering = ("ghfdb_id",)

    def get_import_resource_classes(self, request):
        return [GHFDBParentImportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat, GHFDBSimpleImportFormat]

    @admin.display(description=_("ID_parent"), ordering="ghfdb_id")
    def get_id_parent(self, obj):
        return obj.ghfdb_id

    @admin.display(description=_("q"), ordering="value")
    def get_q(self, obj):
        return getattr(obj, "value", None)

    @admin.display(description=_("q_uncertainty"), ordering="uncertainty")
    def get_q_uncertainty(self, obj):
        return getattr(obj, "uncertainty", None)

    @admin.display(description=_("name"), ordering="sample__name")
    def get_name(self, obj):
        site = getattr(obj, "sample", None)
        return getattr(site, "name", None) if site else None

    @admin.display(description=_("lat_NS"))
    def get_lat_ns(self, obj):
        site = getattr(obj, "sample", None)
        loc = getattr(site, "location", None) if site else None
        return getattr(loc, "y", None) if loc else None

    @admin.display(description=_("long_EW"))
    def get_long_ew(self, obj):
        site = getattr(obj, "sample", None)
        loc = getattr(site, "location", None) if site else None
        return getattr(loc, "x", None) if loc else None

    @admin.display(description=_("elevation"))
    def get_elevation(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "elevation", None) if hfs else None

    @admin.display(
        description=_("environment"), ordering="sample__heatflowsite__environment"
    )
    def get_environment(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "environment", None) if hfs else None

    @admin.display(description=_("p_comment"), ordering="comment")
    def get_p_comment(self, obj):
        return getattr(obj, "comment", None)

    @admin.display(description=_("corr_HP_flag"), ordering="corr_HP_flag")
    def get_corr_hp_flag(self, obj):
        return getattr(obj, "corr_HP_flag", None)

    @admin.display(description=_("total_depth_MD"))
    def get_total_depth_md(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "length", None) if hfs else None

    @admin.display(description=_("total_depth_TVD"))
    def get_total_depth_tvd(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "vertical_depth", None) if hfs else None

    @admin.display(
        description=_("explo_method"), ordering="sample__heatflowsite__explo_method"
    )
    def get_explo_method(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "explo_method", None) if hfs else None

    @admin.display(description=_("explo_purpose"))
    def get_explo_purpose(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        if not hfs:
            return ""
        concepts = hfs.explo_purpose.all()
        return "; ".join(str(c) for c in concepts)

    @admin.display(description=_("quality"), ordering="quality")
    def get_quality(self, obj):
        return getattr(obj, "quality", None)

    @admin.display(description=_("country"), ordering="sample__heatflowsite__country")
    def get_country(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "country", None) if hfs else None

    @admin.display(description=_("region"), ordering="sample__heatflowsite__region")
    def get_region(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "region", None) if hfs else None

    @admin.display(
        description=_("continent"), ordering="sample__heatflowsite__continent"
    )
    def get_continent(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "continent", None) if hfs else None

    @admin.display(description=_("domain"), ordering="sample__heatflowsite__domain")
    def get_domain(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "domain", None) if hfs else None

    @admin.display(description=_("total_children"), ordering="total_children")
    def total_children(self, obj):
        return getattr(obj, "total_children", None)

    @admin.display(description=_("relevant_children"), ordering="relevant_children")
    def relevant_children(self, obj):
        return getattr(obj, "relevant_children", None)

    def get_queryset(self, request):
        return (
            GHFDBParent.objects.with_child_counts()
            .select_related(
                "sample",
                "sample__location",
                "sample__heatflowsite",
            )
            .prefetch_related("sample__heatflowsite__explo_purpose")
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
