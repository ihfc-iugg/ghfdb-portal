import os
from datetime import date

from django import forms
from django.contrib.staticfiles import finders
from django.core.files import File
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_downloadview import PathDownloadView
from django_downloadview.exceptions import FileNotFound
from django_htmx.http import HttpResponseClientRedirect
from fairdm.contrib.import_export.views import DataExportView, DataImportView
from fairdm.registry import registry
from fairdm.utils.view_mixins import HTMXMixin
from neapolitan.views import CRUDView

from .models import HeatFlow, Review
from .resources import GHFDBImportFormat, GHFDBResource


class GHFDBPathDownloadView(PathDownloadView):
    def get_path(self):
        return finders.find("ghfdb/IHFC_2024_GHFDB.csv")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["reviewers", "comment", "start_date", "literature"]


class ReviewCRUDView(HTMXMixin, CRUDView):
    model = Review
    form_class = ReviewForm

    def get_form(self, data=None, files=None, **kwargs):
        if self.role.value == "create":
            data = data.copy()
            data["reviewers"] = self.request.user.pk
            data["start_date"] = date.today().isoformat()
        return super().get_form(data, files, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        # add user as a contributor of the dataset with the role of reviewer
        # self.request.user.add_to(self.object.dataset, ["reviewer"])

        if self.role.value == "create":
            # add user as a contributor of the dataset with the role of reviewer
            self.request.user.add_to(self.object.dataset, ["reviewer"])
            # action.send(
            #     self.request.user,
            #     verb=_("harvesting"),
            #     target=self.object.literature,
            #     description=_("is harvesting data from"),
            # )
        return HttpResponseClientRedirect(self.object.dataset.get_absolute_url())


class GHFDBImport(DataImportView):
    template_name = "heat_flow/ghfdb_import.html"

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


class GHFDBExploreView(TemplateView):
    template_name = "explore.html"
