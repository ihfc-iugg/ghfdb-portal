"""DRF viewsets for the GHFDB published-structure API (FS-006)."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from fairdm.api.filters import FairDMVisibilityFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import GHFDBParent
from .serializers import GHFDBParentSerializer


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
    retrieve=extend_schema(summary=_("Retrieve a published parent"), tags=["ghfdb"]),
)
class GHFDBParentViewSet(GHFDBBaseViewSet):
    """Published parent heat-flow records, one per site (FS-006 US1)."""

    serializer_class = GHFDBParentSerializer

    @property
    def queryset(self):
        return self.get_queryset()

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
