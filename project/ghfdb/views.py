import json
import os
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.files import File
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_downloadview import PathDownloadView
from django_downloadview.exceptions import FileNotFound
from drf_spectacular.utils import extend_schema
from fairdm import plugins
from fairdm.contrib.import_export.views import DataExportView, DataImportView, DatasetPublishConfirm
from fairdm.layouts import ApplicationLayout
from fairdm.plugins import check_has_edit_permission
from fairdm.registry import registry
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from review.utils import docs_link

from .forms import GHFDBImportForm
from .models import HeatFlow
from .resources import GHFDBImportFormat, GHFDBResource
from .serializers import MyJSONSchemaSerializer

plugins.dataset.unregister(DataImportView)

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


class GHFDBImport(DataImportView):
    name = "import"
    title = _("GHFDB Import")
    sections = {
        "form": "components.form.default",
    }
    heading_config = {
        "title": _("Import data"),
        "description": _(
            "This data import workflow allows you to upload an existing dataset formatted according to the latest specifications of the Global Heat Flow Database. To access the correct template or learn more about this process, please refer to the documentation linked below."
        ),
        "links": [docs_link("guides/importing-data")],
    }
    form_config = {
        "actions": True,
        "submit_button": {
            "text": _("Import"),
            "icon": "upload",
            "style": "primary",
        },
    }
    form_class = GHFDBImportForm
    template_name = "ghfdb_import.html"
    # import_kwargs = {
    #     "dry_run": True,
    #     "raise_errors": False,
    #     "rollback_on_validation_errors": True,
    # }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class GHFDBImportConfirm(GHFDBImport):
    name = "import_confirm"
    title = _("GHFDB Import Confirmation")
    heading_config = {
        "title": _("Confirm import"),
        "description": _(
            "Please review the data you are about to import. If everything looks correct, click 'Import' to proceed."
        ),
    }
    form_class = None


plugins.dataset.register(GHFDBImport)


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


plugins.dataset.unregister(DatasetPublishConfirm)


@plugins.dataset.register()
class GetPublishedView(DatasetPublishConfirm):
    """This view will override the default publishing view of FairDM so that we can integrate directly with GFZ Data Services."""

    heading_config = {
        "description": _(
            "This portal is integrated with GFZ Data Services, allowing you to submit your dataset for formal publication. "
            "When you click Confirm Submission, your dataset and its metadata will be packaged and transferred to GFZ Data "
            "Services for verification and feedback. The team there will review the submission and contact you with further "
            "information about the publication process. For more details, please refer to the link below."
        ),
        "links": [docs_link("get-published")],
    }
    menu_item = {
        "name": _("Publish Dataset"),
        "icon": "fa-solid fa-file-export",
    }
    sections = {
        "components.form.default",
    }

    check = can_publish_dataset

    def form_valid(self, form):
        """
        Override the form_valid method to handle the submission of the dataset to GFZ Data Services.
        """
        # TODO: Implement the logic to package and send the dataset to GFZ Data Services.

        self.messages.success(
            _(
                "Your dataset has been successfully submitted for publication. The GFZ Data Services team will contact you with further information."
            ),
        )
        return redirect(self.base_object.get_absolute_url())
