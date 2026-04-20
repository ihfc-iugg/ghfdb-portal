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

from .models import GHFDB, GHFDBParent, GHFDBRelease
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
            return queryset.filter(sample__heatflowinterval__sample__heatflowsite__environment=self.value())
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
            return queryset.filter(sample__heatflowinterval__sample__heatflowsite__explo_method=self.value())
        return queryset


def _scalar(attr, description=None, orderable=True):
    """Create a display callable for a queryset scalar annotation.

    Each annotation name in ``list_display`` must correspond to either a model
    field or a callable on the admin class.  This factory returns a function
    that reads *attr* from the annotated queryset row, sets ``short_description``
    to *description* (defaults to *attr*), and registers *attr* as the sort key
    unless *orderable* is False (e.g. for subquery-backed annotations).
    """

    def method(self, obj):
        return getattr(obj, attr, None)

    method.short_description = description or attr
    if orderable:
        method.admin_order_field = attr
    return method


@admin.register(GHFDBRelease)
class GHFDBReleaseAdmin(admin.ModelAdmin):
    list_display = ("version", "release_date", "description")
    ordering = ("-release_date",)


@admin.register(GHFDB)
class GHFDBChildAdmin(ImportExportMixin, admin.ModelAdmin):
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
        "local_id",
        "get_id_parent",
        "site_name",
        "lat_NS",
        "long_EW",
        "qc",
        "qc_uncertainty",
        "get_q_method",
        "q_top",
        "q_bottom",
        "probe_penetration",
        "get_publication_reference",
        "get_data_reference",
        "relevant_child",
        "c_comment",
        "corr_IS_flag",
        "corr_T_flag",
        "corr_S_flag",
        "corr_E_flag",
        "corr_TOPO_flag",
        "corr_PAL_flag",
        "corr_SUR_flag",
        "corr_CONV_flag",
        "corr_HR_flag",
        "expedition",
        "get_probe_type",
        "probe_length",
        "probe_tilt",
        "water_temperature",
        "get_geo_lithology",
        "get_geo_stratigraphy",
        "T_grad_mean",
        "T_grad_uncertainty",
        "T_grad_mean_cor",
        "T_grad_uncertainty_cor",
        "get_t_method_top",
        "get_t_method_bottom",
        "T_shutin_top",
        "T_shutin_bottom",
        "get_t_corr_top",
        "get_t_corr_bottom",
        "T_number",
        "q_date",
        "tc_mean",
        "tc_uncertainty",
        "get_tc_source",
        "get_tc_location",
        "get_tc_method",
        "get_tc_saturation",
        "get_tc_p_t_conditions",
        "get_tc_p_t_fuction",
        "tc_number",
        "get_tc_strategy",
        "get_ref_isgn",
    )
    search_fields = (
        "sample__heatflowinterval__sample__name",
        "parent__local_id",
        "local_id",
    )
    list_filter = (
        EnvironmentListFilter,
        "parent__corr_HP_flag",
        ChildExplorationMethodListFilter,
        ExplorePurposeListFilter,
        "sample__heatflowinterval__sample__heatflowsite__country",
        "sample__heatflowinterval__sample__heatflowsite__region",
        "sample__heatflowinterval__sample__heatflowsite__continent",
        "sample__heatflowinterval__sample__heatflowsite__domain",
    )
    list_display_links = None  # enforce read-only (no edit links)
    ordering = ("parent__local_id", "local_id")

    @staticmethod
    def _interval(obj):
        sample = getattr(obj, "sample", None)
        if sample is None:
            return None
        return getattr(sample, "heatflowinterval", None)

    # --- Import configuration -------------------------------------------------------

    def get_import_resource_classes(self, request):
        return [GHFDBChildImportResource]

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

    # --- Scalar annotation display methods ---
    # Generated via _scalar(); no explicit def needed — the factory sets
    # short_description and admin_order_field on the returned callable.

    site_name = _scalar("site_name", description="name")
    lat_NS = _scalar("lat_NS")
    long_EW = _scalar("long_EW")
    qc = _scalar("qc")
    qc_uncertainty = _scalar("qc_uncertainty")
    q_top = _scalar("q_top")
    q_bottom = _scalar("q_bottom")
    probe_penetration = _scalar("probe_penetration")
    relevant_child = _scalar("relevant_child")
    corr_IS_flag = _scalar("corr_IS_flag", orderable=False)
    corr_T_flag = _scalar("corr_T_flag", orderable=False)
    corr_S_flag = _scalar("corr_S_flag", orderable=False)
    corr_E_flag = _scalar("corr_E_flag", orderable=False)
    corr_TOPO_flag = _scalar("corr_TOPO_flag", orderable=False)
    corr_PAL_flag = _scalar("corr_PAL_flag", orderable=False)
    corr_SUR_flag = _scalar("corr_SUR_flag", orderable=False)
    corr_CONV_flag = _scalar("corr_CONV_flag", orderable=False)
    corr_HR_flag = _scalar("corr_HR_flag", orderable=False)
    probe_length = _scalar("probe_length")
    probe_tilt = _scalar("probe_tilt")
    T_grad_mean = _scalar("T_grad_mean")
    T_grad_uncertainty = _scalar("T_grad_uncertainty")
    T_grad_mean_cor = _scalar("T_grad_mean_cor")
    T_grad_uncertainty_cor = _scalar("T_grad_uncertainty_cor")
    T_shutin_top = _scalar("T_shutin_top")
    T_shutin_bottom = _scalar("T_shutin_bottom")
    T_number = _scalar("T_number")
    q_date = _scalar("q_date")
    tc_mean = _scalar("tc_mean")
    tc_uncertainty = _scalar("tc_uncertainty")
    tc_number = _scalar("tc_number")

    @admin.display(description=_("q_method"))
    def get_q_method(self, obj):
        return "; ".join(str(c) for c in obj.method.all())

    @admin.display(description=_("publication_reference"))
    def get_publication_reference(self, obj):
        references = getattr(obj, "publication_references", None)
        if references is None:
            return ""
        return "; ".join(str(r) for r in references.all())

    @admin.display(description=_("data_reference"))
    def get_data_reference(self, obj):
        references = getattr(obj, "data_references", None)
        if references is None:
            return ""
        return "; ".join(str(r) for r in references.all())

    @admin.display(description=_("probe_type"))
    def get_probe_type(self, obj):
        interval = self._interval(obj)
        if interval is None or not hasattr(interval, "probe_metadata"):
            return ""
        return "; ".join(str(c) for c in interval.probe_metadata.probe_type.all())

    @admin.display(description=_("geo_lithology"))
    def get_geo_lithology(self, obj):
        interval = self._interval(obj)
        if interval is None:
            return ""
        return "; ".join(str(c) for c in interval.lithology.all())

    @admin.display(description=_("geo_stratigraphy"))
    def get_geo_stratigraphy(self, obj):
        interval = self._interval(obj)
        if interval is None:
            return ""
        return "; ".join(str(c) for c in interval.stratigraphy.all())

    @admin.display(description=_("T_method_top"))
    def get_t_method_top(self, obj):
        gradient = getattr(obj, "thermal_gradient", None)
        if gradient is None:
            return ""
        return "; ".join(str(c) for c in gradient.method_top.all())

    @admin.display(description=_("T_method_bottom"))
    def get_t_method_bottom(self, obj):
        gradient = getattr(obj, "thermal_gradient", None)
        if gradient is None:
            return ""
        return "; ".join(str(c) for c in gradient.method_bottom.all())

    @admin.display(description=_("T_corr_top"))
    def get_t_corr_top(self, obj):
        gradient = getattr(obj, "thermal_gradient", None)
        if gradient is None:
            return ""
        return "; ".join(str(c) for c in gradient.correction_top.all())

    @admin.display(description=_("T_corr_bottom"))
    def get_t_corr_bottom(self, obj):
        gradient = getattr(obj, "thermal_gradient", None)
        if gradient is None:
            return ""
        return "; ".join(str(c) for c in gradient.correction_bottom.all())

    @admin.display(description=_("tc_source"))
    def get_tc_source(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.source.all())

    @admin.display(description=_("tc_location"))
    def get_tc_location(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.location.all())

    @admin.display(description=_("tc_method"))
    def get_tc_method(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.method.all())

    @admin.display(description=_("tc_saturation"))
    def get_tc_saturation(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.saturation.all())

    @admin.display(description=_("tc_pT_conditions"))
    def get_tc_p_t_conditions(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.pT_conditions.all())

    @admin.display(description=_("tc_pT_fuction"))
    def get_tc_p_t_fuction(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.pT_function.all())

    @admin.display(description=_("tc_strategy"))
    def get_tc_strategy(self, obj):
        conductivity = getattr(obj, "thermal_conductivity", None)
        if conductivity is None:
            return ""
        return "; ".join(str(c) for c in conductivity.strategy.all())

    @admin.display(description=_("Ref_ISGN"))
    def get_ref_isgn(self, obj):
        return ""

    def get_queryset(self, request):
        """Return the flat annotated queryset for the changelist."""
        return GHFDB.objects.as_ghfdb_flat().prefetch_related(
            "method",
            "sample__heatflowinterval__sample__heatflowsite__explo_purpose",
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
        "get_corr_hp_flag",
        "get_total_depth_md",
        "get_total_depth_tvd",
        "get_explo_method",
        "get_explo_purpose",
        "get_country",
        "get_region",
        "get_continent",
        "get_domain",
        "total_children",
        "relevant_children",
    )
    search_fields = (
        "sample__name",
        "local_id",
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
    ordering = ("local_id",)

    def get_import_resource_classes(self, request):
        return [GHFDBParentImportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat]

    @admin.display(description=_("ID_parent"), ordering="local_id")
    def get_id_parent(self, obj):
        return obj.local_id

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

    @admin.display(description=_("environment"), ordering="sample__heatflowsite__environment")
    def get_environment(self, obj):
        site = getattr(obj, "sample", None)
        hfs = getattr(site, "heatflowsite", None) if site else None
        return getattr(hfs, "environment", None) if hfs else None

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

    @admin.display(description=_("explo_method"), ordering="sample__heatflowsite__explo_method")
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

    @admin.display(description=_("continent"), ordering="sample__heatflowsite__continent")
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
