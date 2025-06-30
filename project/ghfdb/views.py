import json
import os
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.files import File
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_downloadview import PathDownloadView
from django_downloadview.exceptions import FileNotFound
from drf_spectacular.utils import extend_schema
from fairdm import plugins
from fairdm.contrib.import_export.views import DataExportView, DataImportView
from fairdm.layouts import ApplicationLayout
from fairdm.registry import registry
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import GHFDBImportForm
from .models import HeatFlow
from .resources import GHFDBImportFormat, GHFDBResource
from .serializers import MyJSONSchemaSerializer

plugins.dataset.unregister(DataImportView)

data_dir = Path(__file__).resolve().parent / "data"


@extend_schema(
    summary="Metadata reflecting field the contents of my_data.json",
    description="Serves a JSON file from disk as a DRF API endpoint.",
    tags=["ghfdb"],
    # responses={200: dict},
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


@plugins.dataset.register()
class GHFDBImport(DataImportView):
    name = "import"
    title = _("GHFDB Import")
    description = _(
        "This data import workflow allows you to upload an existing dataset formatted according to the latest specifications of the Global Heat Flow Database. "
    )
    form_class = GHFDBImportForm
    template_name = "ghfdb_import.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_button_config"] = {
            "text": _("Import"),
            "icon": "upload",
            "style": "primary",
        }
        context["samples"] = self.base_object.samples.exists()
        context["measurements"] = self.base_object.measurements.exists()
        if context["samples"] and context["measurements"]:
            context["form"] = None
        return context

    def get_resource(self):
        return GHFDBResource(dataset=self.get_object())

    def get_resource_model(self):
        """
        Retrieves the model class based on the 'type' query parameter.
        """
        self.meta = registry.get_model(HeatFlow)
        self.dtype = f"{self.meta['app_label']}.{self.meta['model']}"  # Ensures dtype is still assigned
        return HeatFlow

    def get_meta_title(self, context):
        return _("GHFDB Upload")

    def get_dataset_format(self, file):
        return GHFDBImportFormat(encoding=self.from_encoding)


class GHFDBExport(DataExportView):
    template_path = "ghfdb/template.xlsx"

    def get_file(self):
        if not self.request.POST.get("template"):
            return super().get_file()

        filename = finders.find(self.template_path)

        if not os.path.isfile(filename):
            raise FileNotFound(f'File "{filename}" does not exists')
        with open(filename, "rb") as f:
            return File(f)

    def get_resource(self):
        return GHFDBResource(dataset=self.get_object())

    def get_resource_model(self):
        """
        Retrieves the model class based on the 'type' query parameter.
        """
        self.meta = registry.get_model(HeatFlow)
        self.dtype = f"{self.meta['app_label']}.{self.meta['model']}"  # Ensures dtype is still assigned
        return HeatFlow

    def get_basename(self):
        if self.request.POST.get("template"):
            return os.path.basename(self.template_path)
        return f"GHFDB.{self.format_class.get_extension()}"


class GHFDBExploreView(ApplicationLayout, TemplateView):
    template_name = "explore.html"
