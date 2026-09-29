"""DRF viewsets for the GHFDB published-structure API (FS-006)."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from fairdm.api.filters import FairDMVisibilityFilter
from fairdm.api.permissions import FairDMObjectPermissions
from heat_flow.models import HeatFlowSite
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import GHFDBChild, GHFDBParent
from .serializers import (
    GHFDBChildDetailSerializer,
    GHFDBChildListSerializer,
    GHFDBFlatSerializer,
    GHFDBParentDetailSerializer,
    GHFDBParentSerializer,
)


class GHFDBObjectPermissions(FairDMObjectPermissions):
    """Object-level permission for the GHFDB proxy viewsets.

    A safe-method check asks for ``measurement.view_measurement`` — the
    permission :class:`~fairdm.api.filters.FairDMVisibilityFilter` already
    resolves a list request to — instead of the proxy's own
    ``ghfdb.view_ghfdb*`` codename. Guardian resolves a proxy model's content
    type through its concrete model, ``heat_flow`` for both
    ``GHFDBParent``/``GHFDBChild``, so checking the proxy's own
    ``ghfdb``-labelled permission against the object raised
    ``guardian.exceptions.WrongAppError`` instead of deciding.
    """

    def get_required_object_permissions(self, method, model_cls):
        """Ask for the measurement view permission on a read."""
        if method in SAFE_METHODS:
            return ["measurement.view_measurement"]
        return super().get_required_object_permissions(method, model_cls)


def served_parents_for(request, view):
    """Parents visible to *request*, narrowed to ones whose site is visible too.

    A parent's own visibility (via ``FairDMVisibilityFilter`` on its dataset)
    says nothing about the ``HeatFlowSite`` it describes — the two can sit in
    different datasets — so ADR 0021's second path (a determination attached
    to a site that is not public) is only closed by checking both.
    """
    served = FairDMVisibilityFilter().filter_queryset(
        request, GHFDBParent.objects.all(), view
    )
    visible_sites = FairDMVisibilityFilter().filter_queryset(
        request, HeatFlowSite.objects.all(), view
    )
    return served.filter(sample_id__in=visible_sites.values_list("pk", flat=True))


class GHFDBBaseViewSet(ReadOnlyModelViewSet):
    """Shared read-only base for the GHFDB published-structure viewsets.

    Keeps DRF's own ``get_object()`` unmodified, so the visibility filter and
    the object permission check run on the single-record route too.
    Pagination and throttling are the framework's own settings; the
    permission class is narrowed to :class:`GHFDBObjectPermissions`.
    """

    lookup_field = "ghfdb_id"
    lookup_value_regex = "[0-9]+"
    filter_backends = [FairDMVisibilityFilter]
    permission_classes = [GHFDBObjectPermissions]


@extend_schema_view(
    list=extend_schema(summary=_("List published parents"), tags=["ghfdb"]),
    retrieve=extend_schema(
        summary=_("Retrieve a published parent"),
        tags=["ghfdb"],
        responses=GHFDBParentDetailSerializer,
    ),
)
class GHFDBParentViewSet(GHFDBBaseViewSet):
    """Published parent heat-flow records, one per site (FS-006)."""

    serializer_class = GHFDBParentSerializer

    @property
    def queryset(self):
        """Expose ``get_queryset()`` as the attribute, as the framework's viewsets do."""
        return self.get_queryset()

    def get_serializer_class(self):
        """Use the children-attached shape on the single record (FS-006 FR-006)."""
        if self.action == "retrieve":
            return GHFDBParentDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """Attach the determinations the determination route would serve.

        Reuses ``GHFDBChildViewSet``'s own queryset, narrowed to this parent,
        so the attached list is exactly what ``/children/`` would serve this
        requester for this parent.
        """
        instance = self.get_object()
        child_viewset = GHFDBChildViewSet()
        child_viewset.request = request
        children = child_viewset.filter_queryset(child_viewset.get_queryset())
        instance.children_list = children.filter(parent=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        """Return published parents, their counts and exploration purposes.

        Narrowed to parents this requester is served (ADR 0021).
        Ordered by published identifier then primary key, so a page is
        stable. Constant query count regardless of row count.
        """
        served = served_parents_for(self.request, self)
        return (
            GHFDBParent.objects.as_ghfdb_flat()
            .with_child_counts()
            .prefetch_related("sample__heatflowsite__explo_purpose")
            .filter(pk__in=served.values_list("pk", flat=True))
            .order_by("ghfdb_id", "pk")
        )


@extend_schema_view(
    list=extend_schema(summary=_("List published determinations"), tags=["ghfdb"]),
    retrieve=extend_schema(
        summary=_("Retrieve a published determination"),
        tags=["ghfdb"],
        responses=GHFDBChildDetailSerializer,
    ),
)
class GHFDBChildViewSet(GHFDBBaseViewSet):
    """Published heat-flow determinations, one per measurement (FS-006)."""

    serializer_class = GHFDBChildListSerializer

    @property
    def queryset(self):
        """Expose ``get_queryset()`` as the attribute, as the framework's viewsets do."""
        return self.get_queryset()

    def get_serializer_class(self):
        """Use the parent-nesting shape on the single record (FS-006 FR-008)."""
        if self.action == "retrieve":
            return GHFDBChildDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """Nest the parent's full record, in one further query (FS-006 FR-008).

        ``get_queryset()``'s ``select_related("parent")`` on the underlying
        ``HeatFlow`` row carries no counts or column annotations, so the
        nested parent is loaded through the parent route's own queryset
        instead, the same shape ``GHFDBParentViewSet`` serves.
        """
        instance = self.get_object()
        parent_viewset = GHFDBParentViewSet()
        parent_viewset.request = request
        instance.parent = parent_viewset.get_queryset().get(pk=instance.parent_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        """Return determinations whose parent the parent route also serves.

        Visibility is decided per record, and a determination and its parent
        can sit in different datasets, so a determination is narrowed to
        parents this requester is served, as a subquery — a determination
        with no served parent is not served either (ADR 0021).
        Ordered by published identifier then primary key, so a page is
        stable, and constant query count regardless of row count.
        """
        served_parents = served_parents_for(self.request, self)
        return (
            GHFDBChild.objects.for_export()
            .filter(parent__in=served_parents)
            .order_by("ghfdb_id", "pk")
        )


@extend_schema_view(
    list=extend_schema(summary=_("List published rows"), tags=["ghfdb"]),
    retrieve=extend_schema(summary=_("Retrieve a published row"), tags=["ghfdb"]),
)
class GHFDBFlatViewSet(GHFDBBaseViewSet):
    """The released row, one per determination, in the release's own shape
    (FS-006).
    """

    serializer_class = GHFDBFlatSerializer

    @property
    def queryset(self):
        """Expose ``get_queryset()`` as the attribute, as the framework's viewsets do."""
        return self.get_queryset()

    def get_queryset(self):
        """Return the determination route's own queryset.

        Reuses ``GHFDBChildViewSet.get_queryset()`` rather than restating the
        parent-visibility subquery it applies.
        """
        child_viewset = GHFDBChildViewSet()
        child_viewset.request = self.request
        return child_viewset.get_queryset()
