"""Views for the GHFDB app: API endpoints and the map explorer page."""

import json
from pathlib import Path

from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_downloadview import PathDownloadView
from drf_spectacular.utils import extend_schema
from fairdm.contrib.plugins.utils import check_has_edit_permission
from fairdm.views import FairDMTableView, FairDMTemplateView
from heat_flow.models import HeatFlowSite, ParentHeatFlow
from heat_flow.overview import HeatFlowPage
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import GHFDBParentFilter
from .models import GHFDBParent
from .serializers import MyJSONSchemaSerializer
from .tables import GHFDBParentTable

data_dir = Path(__file__).resolve().parent / "data"


def can_publish_dataset(request, instance, **kwargs):
    """Check if the user has permission to publish the dataset.

    This is a placeholder function and should be replaced with actual permission logic.
    """
    if check_has_edit_permission(request, instance, **kwargs) and instance.has_data:
        return True


@extend_schema(
    summary="Metadata reflecting field the contents of my_data.json",
    description="Serves a JSON file from disk as a DRF API endpoint.",
    tags=["ghfdb"],
    responses=MyJSONSchemaSerializer,
)
class GHFDBMetaDataAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, file_format=None):
        file_path = data_dir / "ghfdb_colmeta.json"
        try:
            with open(file_path) as f:
                data = json.load(f)
            return Response(data)
        except FileNotFoundError:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GHFDBPathDownloadView(PathDownloadView):
    """Serve the static GHFDB CSV export as a download."""

    def get_path(self):
        """Return the path to the GHFDB CSV file."""
        return finders.find("ghfdb/IHFC_2024_GHFDB.csv")


# TODO: GHFDBImport, GHFDBImportConfirm, and registration are disabled until
# fairdm.contrib.import_export.views is completed (DataImportView not yet stable).


# TODO: GHFDBExport is disabled until fairdm.contrib.import_export.views is completed (DataExportView not yet stable).


class GHFDBExploreView(FairDMTemplateView):
    """Render the GHFDB map explorer page."""

    template_name = "ghfdb/explore.html"
    page_title = _("GHFDB Map Viewer")


def visible_parents(user):
    """The GHFDB parents the user may see: the parent, and its site, both visible."""
    return (
        GHFDBParent.objects.filter(
            pk__in=ParentHeatFlow.objects.visible_to(user).values("pk"),
            sample_id__in=HeatFlowSite.objects.visible_to(user).values("pk"),
        )
        .as_ghfdb_flat()
        .with_child_counts()
        .prefetch_related("sample__heatflowsite__explo_purpose")
    )


class GHFDBParentTableView(FairDMTableView):
    """The GHFDB parents as a table: filtered, sorted and paged (FS-012 sketch)."""

    model = GHFDBParent
    table_class = GHFDBParentTable
    filterset_class = GHFDBParentFilter
    template_name = "ghfdb/parent_table.html"
    toolbar_filters = ["name", "q", "environment", "U_score", "dataset"]
    paginate_by = 50
    page_title = _("GHFDB")

    def get_queryset(self):
        """Every parent the visitor may see, with its published columns."""
        return visible_parents(self.request.user)


class GHFDBParentChildrenView(TemplateView):
    """A parent's children, for the window the table opens over itself."""

    template_name = "ghfdb/parent_children.html"

    def get_context_data(self, **kwargs):
        """The parent, and its children relevant first."""
        context = super().get_context_data(**kwargs)
        parent = get_object_or_404(
            visible_parents(self.request.user), ghfdb_id=kwargs["ghfdb_id"]
        )
        page = HeatFlowPage(parent, self.request.user, show_all=True)
        context["parent"] = parent
        context["children"] = page.for_parent()["children"]
        return context


# TODO: GetPublishedView is disabled until fairdm.contrib.import_export.views is completed (DatasetPublishConfirm not yet stable).
