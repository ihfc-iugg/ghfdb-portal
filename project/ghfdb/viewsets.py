"""DRF viewsets for the GHFDB published-structure API (FS-006)."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from fairdm.api.filters import FairDMVisibilityFilter
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


class GHFDBBaseViewSet(ReadOnlyModelViewSet):
    """Shared read-only base for the GHFDB published-structure viewsets.

    Keeps DRF's own ``get_object()`` unmodified, so the visibility filter and
    the object permission check run on the single-record route too (spec
    D12). Permission, pagination and throttling are the framework's own
    settings — nothing here overrides them.
    """

    lookup_field = "ghfdb_id"
    lookup_value_regex = "[0-9]+"
    filter_backends = [FairDMVisibilityFilter]


@extend_schema_view(
    list=extend_schema(summary=_("List published parents"), tags=["ghfdb"]),
    retrieve=extend_schema(
        summary=_("Retrieve a published parent"),
        tags=["ghfdb"],
        responses=GHFDBParentDetailSerializer,
    ),
)
class GHFDBParentViewSet(GHFDBBaseViewSet):
    """Published parent heat-flow records, one per site (FS-006 US1, US2)."""

    serializer_class = GHFDBParentSerializer

    @property
    def queryset(self):
        return self.get_queryset()

    def get_serializer_class(self):
        """Use the children-attached shape on the single-record route (FR-006)."""
        if self.action == "retrieve":
            return GHFDBParentDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """Attach the determinations the determination route would serve.

        Reuses ``GHFDBChildViewSet``'s own queryset, narrowed to this parent,
        so the attached list is exactly what ``/children/`` would serve this
        requester for this parent (spec D16).
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

        Ordered by published identifier then primary key, so a page is
        stable (research R4). Constant query count regardless of row count
        (research R7).
        """
        return (
            GHFDBParent.objects.as_ghfdb_flat()
            .with_child_counts()
            .prefetch_related("sample__heatflowsite__explo_purpose")
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
    """Published heat-flow determinations, one per measurement (FS-006 US2)."""

    serializer_class = GHFDBChildListSerializer

    @property
    def queryset(self):
        return self.get_queryset()

    def get_serializer_class(self):
        """Use the parent-nesting shape on the single-record route (D3)."""
        if self.action == "retrieve":
            return GHFDBChildDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """Nest the parent's full US1 record, in one further query (D3).

        ``get_queryset()``'s ``select_related("parent")`` on the underlying
        ``HeatFlow`` row carries no counts or column annotations, so the
        nested parent is loaded through the parent route's own queryset
        instead, the same shape ``GHFDBParentViewSet`` serves.
        """
        instance = self.get_object()
        instance.parent = GHFDBParentViewSet().get_queryset().get(pk=instance.parent_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        """Return determinations whose parent the parent route also serves.

        Visibility is decided per record, and a determination and its parent
        can sit in different datasets, so a determination is narrowed to
        parents the parent route's own queryset serves to this requester, as
        a subquery — a determination with no served parent is not served
        either (spec D16, research R13). Ordered by published identifier
        then primary key, so a page is stable, and constant query count
        regardless of row count (research R7).
        """
        served_parents = FairDMVisibilityFilter().filter_queryset(
            self.request, GHFDBParentViewSet().get_queryset(), self
        )
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
    (FS-006 US3).
    """

    serializer_class = GHFDBFlatSerializer

    @property
    def queryset(self):
        return self.get_queryset()

    def get_queryset(self):
        """Return the determination route's own queryset (spec D16).

        Reuses ``GHFDBChildViewSet.get_queryset()`` rather than restating the
        parent-visibility subquery it applies.
        """
        child_viewset = GHFDBChildViewSet()
        child_viewset.request = self.request
        return child_viewset.get_queryset()
