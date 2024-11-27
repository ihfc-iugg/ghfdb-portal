from datetime import date

from django import forms
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic.edit import FormView
from django_downloadview import PathDownloadView
from django_htmx.http import HttpResponseClientRedirect
from geoluminate.core.view_mixins import HTMXMixin
from geoluminate.models import Dataset
from meta.views import MetadataMixin
from neapolitan.views import CRUDView

from .importer import HeatFlowParentImporter
from .models import Review


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
        return HttpResponseClientRedirect(self.object.dataset.get_absolute_url())


class UploadForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


class GHFDBUpload(HTMXMixin, MetadataMixin, FormView):
    title = _("Upload")
    template_name = "geoluminate/import.html"
    form_class = UploadForm
    extra_context = {"title": _("GHFDB Upload")}
    importer_class = HeatFlowParentImporter

    def process_import(self, dataset, import_file):
        importer = self.importer_class(import_file, dataset)
        return importer.process_import()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        self.dataset = Dataset.objects.get(pk=self.kwargs["pk"])
        errors = self.process_import(self.dataset, form.cleaned_data["docfile"])
        if errors:
            # add errors to context and re-render form
            context = self.get_context_data(form=form)
            context["errors"] = errors
            return self.render_to_response(context)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dataset-measurements", kwargs={"pk": self.dataset.pk})
