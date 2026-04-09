import json
from pathlib import Path

from django.contrib.staticfiles import finders
from django.views.generic import TemplateView
from django_downloadview import PathDownloadView
from drf_spectacular.utils import extend_schema

# from fairdm.contrib.import_export.views import DataExportView, DataImportView, DatasetPublishConfirm  # TODO: not yet complete in fairdm
from fairdm.contrib.plugins.utils import check_has_edit_permission
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MyJSONSchemaSerializer

data_dir = Path(__file__).resolve().parent / "data"


def can_publish_dataset(request, instance, **kwargs):
    """
    Check if the user has permission to publish the dataset.
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
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GHFDBPathDownloadView(PathDownloadView):
    def get_path(self):
        return finders.find("ghfdb/IHFC_2024_GHFDB.csv")


# TODO: GHFDBImport, GHFDBImportConfirm, and registration are disabled until
# fairdm.contrib.import_export.views is completed (DataImportView not yet stable).


# TODO: GHFDBExport is disabled until fairdm.contrib.import_export.views is completed (DataExportView not yet stable).


class GHFDBExploreView(TemplateView):
    template_name = "explore.html"


# TODO: GetPublishedView is disabled until fairdm.contrib.import_export.views is completed (DatasetPublishConfirm not yet stable).
