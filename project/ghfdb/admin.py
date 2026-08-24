"""
GHFDB admin registration.

Registers the ``GHFDBChild`` and ``GHFDBParent`` proxy models as read-only
changelists reading the published Global Heat Flow Database structure
(US-3), each with an XLSX import action gated on the model's add permission.
Both changelists' published columns are built from
``project/ghfdb/columns.py``'s published-column mapping rather than
restated here — see that module's docstring and
``specs/002-ghfdb-proxy/decisions.md`` D1 and D2.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_permission_codename
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin
from import_export.formats.base_formats import XLSX

from .columns import ColumnDisplay
from .constants import CHILD_COLUMNS, PARENT_COLUMNS
from .models import GHFDBChild, GHFDBParent, GHFDBRelease
from .resources import (
    GHFDBChildImportResource,
    GHFDBExportResource,
    GHFDBImportFormat,
    GHFDBParentImportResource,
    GHFDBSimpleImportFormat,
)


class VocabularyListFilter(SimpleListFilter):
    """A ``SimpleListFilter`` scoped to one controlled vocabulary (FR-018).

    Parametrised by subclass on the vocabulary, the lookup path from the
    changelist's model to the filtered field, and the lookup mode. Two modes
    are needed: ``FIELD``, for a single-valued ``ConceptField`` whose choices
    come from the vocabulary and match on the stored value, and ``CONCEPT``,
    for a many-valued field whose choices come from the concept rows and
    match on their primary key. Both the determination and the site
    changelist filter on environment, exploration method and exploration
    purpose, so one class carries the shape six near-identical ones would
    otherwise repeat.
    """

    FIELD = "field"
    CONCEPT = "concept"

    lookup_path: str = ""
    mode: str = FIELD

    def get_vocabulary(self):
        """Return the vocabulary class this filter scopes to.

        Overridden per subclass with a lazy import, so importing this module
        does not import every controlled vocabulary.
        """
        raise NotImplementedError

    def lookups(self, request, model_admin):
        vocabulary = self.get_vocabulary()
        if self.mode == self.CONCEPT:
            from research_vocabs.models import Concept

            concepts = Concept.get_for_vocabulary(vocabulary).order_by("label")
            return [(concept.pk, concept.label) for concept in concepts]
        return vocabulary().choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.lookup_path: self.value()})
        return queryset


class ExplorePurposeListFilter(VocabularyListFilter):
    """Exploration-purpose filter for the determination changelist, scoped to
    the ``ExplorationPurpose`` vocabulary (FR-018). Many-valued, so it
    matches on the concept row's primary key rather than a stored value."""

    title = _("exploration purpose")
    parameter_name = "explo_purpose"
    mode = VocabularyListFilter.CONCEPT
    lookup_path = "sample__heatflowinterval__site__explo_purpose__pk"

    def get_vocabulary(self):
        from heat_flow.vocabularies import ExplorationPurpose

        return ExplorationPurpose


class EnvironmentListFilter(VocabularyListFilter):
    """Environment filter for the determination changelist, scoped to the
    ``GeographicEnvironment`` vocabulary (FR-018)."""

    title = _("environment")
    parameter_name = "environment"
    lookup_path = "sample__heatflowinterval__site__environment"

    def get_vocabulary(self):
        from heat_flow.vocabularies import GeographicEnvironment

        return GeographicEnvironment


class ChildExplorationMethodListFilter(VocabularyListFilter):
    """Exploration-method filter for the determination changelist, scoped to
    the ``ExplorationMethod`` vocabulary (FR-018)."""

    title = _("exploration method")
    parameter_name = "explo_method"
    lookup_path = "sample__heatflowinterval__site__explo_method"

    def get_vocabulary(self):
        from heat_flow.vocabularies import ExplorationMethod

        return ExplorationMethod


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

    def has_import_permission(self, request):
        """Gate the import route on the model's add permission at the user
        level (T123): the framework's own hook is a no-op whenever
        ``IMPORT_EXPORT_IMPORT_PERMISSION_CODE`` is unset, which it is in
        this project, so a user holding only view permission could
        otherwise reach a route that writes through a changelist declared
        read-only.
        """
        opts = self.opts
        codename = get_permission_codename("add", opts)
        return request.user.has_perm(f"{opts.app_label}.{codename}")

    def get_queryset(self, request):
        """Return the published determinations as complete rows: scoped to
        published records by the manager, and ready for every many-valued
        column without a query per row (FR-002, FR-019)."""
        return GHFDBChild.objects.for_export()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def geography_display(field_name):
    """Build a ``GHFDBParentAdmin`` display method for one geography field,
    read directly off ``obj.sample.heatflowsite`` (D15).

    The site changelist's own queryset ``select_related``s both ``sample``
    and ``sample__heatflowsite`` (``GHFDBParentQuerySet.as_ghfdb_flat()``),
    so no accessor built here can fail to resolve, and a defensive
    ``getattr`` guard would be exactly the kind of accessor a reader could
    mistake for a working one when it never triggers — R4's concern,
    applied to a relationship walk rather than a missing field.
    """

    @admin.display(
        description=_(field_name), ordering=f"sample__heatflowsite__{field_name}"
    )
    def display(self, obj):
        return getattr(obj.sample.heatflowsite, field_name)

    return display


class ParentExplorePurposeListFilter(VocabularyListFilter):
    """Exploration-purpose filter for the site changelist, scoped to the
    ``ExplorationPurpose`` vocabulary (FR-018). Many-valued, so it matches
    on the concept row's primary key rather than a stored value (T118)."""

    title = _("exploration purpose")
    parameter_name = "explo_purpose"
    mode = VocabularyListFilter.CONCEPT
    lookup_path = "sample__heatflowsite__explo_purpose__pk"

    def get_vocabulary(self):
        from heat_flow.vocabularies import ExplorationPurpose

        return ExplorationPurpose


class ParentEnvironmentListFilter(VocabularyListFilter):
    """Environment filter for the site changelist, scoped to the
    ``GeographicEnvironment`` vocabulary (FR-018, T118)."""

    title = _("environment")
    parameter_name = "environment"
    lookup_path = "sample__heatflowsite__environment"

    def get_vocabulary(self):
        from heat_flow.vocabularies import GeographicEnvironment

        return GeographicEnvironment


class ParentExplorationMethodListFilter(VocabularyListFilter):
    """Exploration-method filter for the site changelist, scoped to the
    ``ExplorationMethod`` vocabulary (FR-018, T118)."""

    title = _("exploration method")
    parameter_name = "explo_method"
    lookup_path = "sample__heatflowsite__explo_method"

    def get_vocabulary(self):
        from heat_flow.vocabularies import ExplorationMethod

        return ExplorationMethod


@admin.register(GHFDBParent)
class GHFDBParentAdmin(ImportExportMixin, admin.ModelAdmin):
    """Read-only changelist for the published site view (US-3).

    The published block of ``list_display`` comes entirely from
    ``project/ghfdb/columns.py``'s published-column mapping (see
    ``list_display`` below), so a column added to ``constants.PARENT_COLUMNS``
    and not to that mapping is a startup failure rather than a silently
    missing column. Four geography columns follow it — portal additions, not
    part of the published structure (D8) — and the two determination-count
    columns come last. Mutation of existing records is disabled; data enters
    only via the import action, gated to staff holding the model's add
    permission (T123). Only ``GHFDBParentImportResource`` is attached; no
    export resource is present (FR-021).

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global
          Heat Flow Database.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    list_display = (
        *ColumnDisplay.list_display_for(PARENT_COLUMNS),
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

    def get_export_resource_classes(self, request):
        """No export resource on this changelist (FR-021): ``ImportExportMixin``
        overrides only the import side, so without this the framework's
        default export path is live with a generated resource that would
        emit the site model's own fields rather than the published
        structure (T119)."""
        return []

    def has_import_permission(self, request):
        """Gate the import route on the model's add permission at the user
        level (T123): the framework's own hook is a no-op whenever
        ``IMPORT_EXPORT_IMPORT_PERMISSION_CODE`` is unset, which it is in
        this project, so a user holding only view permission could
        otherwise reach a route that writes through a changelist declared
        read-only.
        """
        opts = self.opts
        codename = get_permission_codename("add", opts)
        return request.user.has_perm(f"{opts.app_label}.{codename}")

    get_country = geography_display("country")
    get_region = geography_display("region")
    get_continent = geography_display("continent")
    get_domain = geography_display("domain")

    @admin.display(description=_("total_children"), ordering="total_children")
    def total_children(self, obj):
        return getattr(obj, "total_children", None)

    @admin.display(description=_("relevant_children"), ordering="relevant_children")
    def relevant_children(self, obj):
        return getattr(obj, "relevant_children", None)

    def get_queryset(self, request):
        """Return the published sites as complete rows: scoped to published
        records by the manager, flattened onto every published column, and
        carrying the determination counts and the attached children without
        a query per site (FR-002, FR-019)."""
        return GHFDBParent.objects.as_ghfdb_flat().with_child_counts().with_children()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
