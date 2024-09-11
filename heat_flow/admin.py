from admin_extra_buttons.api import ExtraButtonsMixin, button
from django import forms
from django.contrib import admin
from django.db import models
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from geoluminate.contrib.datasets.admin import DatasetAdmin
from geoluminate.contrib.datasets.models import Dataset
from geoluminate.contrib.measurements.admin import MeasurementAdmin
from geoluminate.contrib.samples.admin import SampleAdmin

from .importer import HeatFlowParentImporter
from .models import ChildHeatFlow, HeatFlowInterval, HeatFlowSite, ParentHeatFlow

admin.site.unregister(Dataset)


class UploadForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


def admin_urlname(opts, name):
    return f"admin:{opts.app_label}_{opts.model_name}_{name}"


@admin.register(Dataset)
class HeatFlowDatasetAdmin(ExtraButtonsMixin, DatasetAdmin):
    actions_detail = ["custom_detail_action"]

    @button(
        label=_("Upload"),
    )
    def upload(self, request, pk=None):
        context = self.get_common_context(request, title="Upload")
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                dataset = Dataset.objects.get(pk=pk)
                import_file = request.FILES["docfile"]
                importer = HeatFlowParentImporter(import_file, dataset)
                errors = importer.process_import()
                if errors:
                    context["errors"] = errors
                else:
                    # message user
                    self.message_user(request, "Import successful")
                    return redirect(admin_urlname(context["opts"], "changelist"))
        else:
            form = UploadForm()
        context["form"] = form
        return TemplateResponse(request, "admin_extra_buttons/upload.html", context)


@admin.register(ParentHeatFlow)
class HeatFlowAdmin(MeasurementAdmin):
    list_display = ["q", "q_uncertainty", "corr_HP_flag"]

    fields = (
        "sample",
        ("q", "q_uncertainty"),
        "corr_HP_flag",
    )


@admin.register(ChildHeatFlow)
class ChildHeatFlowAdmin(admin.ModelAdmin):
    list_display = [
        "parent",
        "qc",
        "qc_uncertainty",
    ]

    # list_filter = ["parent__uuid"]

    fieldsets = (
        ("", {"fields": ("sample",)}),
        (
            "Heat Flow",
            {
                "fields": (
                    "parent",
                    "relevant_child",
                    ("qc", "qc_uncertainty"),
                    # ("depth_top", "depth_bottom"),
                    "q_method",
                )
            },
        ),
        (
            "Probe Sensing",
            {
                "fields": (
                    ("probe_type", "probe_length"),
                    ("probe_penetration", "probe_tilt"),
                )
            },
        ),
        (
            "Temperature",
            {
                "fields": (
                    ("T_grad_mean", "T_grad_uncertainty"),
                    ("T_grad_mean_cor", "T_grad_uncertainty_cor"),
                    ("T_method_top", "T_method_bottom"),
                    ("T_shutin_top", "T_shutin_bottom"),
                    ("T_corr_top", "T_corr_bottom"),
                    "T_number",
                )
            },
        ),
        (
            "Thermal Conductivity",
            {
                "fields": (
                    ("tc_mean", "tc_uncertainty"),
                    "tc_source",
                    "tc_location",
                    "tc_method",
                    "tc_saturation",
                    ("tc_pT_conditions", "tc_pT_function"),
                    "tc_strategy",
                    "tc_number",
                )
            },
        ),
        (
            "Corrections",
            {
                "fields": (
                    "corr_IS_flag",
                    "corr_T_flag",
                    "corr_S_flag",
                    "corr_E_flag",
                    "corr_TOPO_flag",
                    "corr_PAL_flag",
                    "corr_SUR_flag",
                    "corr_CONV_flag",
                    "corr_HR_flag",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    # "expedition",
                    "water_temperature",
                    # "lithology",
                    # "IGSN",
                )
            },
        ),
    )

    formfield_overrides = {
        models.ManyToManyField: {"widget": Select2MultipleWidget},
        models.ForeignKey: {"widget": Select2Widget},
    }


@admin.register(HeatFlowInterval)
class HeatFlowIntervalAdmin(SampleAdmin):
    list_display = [
        # "parent",
        "top",
        "bottom",
        # "geo_lithology",
        # "geo_stratigraphy",
    ]

    formfield_overrides = {
        models.ManyToManyField: {"widget": Select2MultipleWidget},
    }


@admin.register(HeatFlowSite)
class HeatFlowSiteAdmin(SampleAdmin):
    list_display = ["top", "bottom"]

    formfield_overrides = {
        models.ManyToManyField: {"widget": Select2MultipleWidget},
        models.ForeignKey: {"widget": Select2Widget},
    }

    fieldsets = (
        (
            _("Heat flow specific"),
            {
                "fields": (
                    ("environment", "explo_method"),
                    "explo_purpose",
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        store = set()
        fieldsets = []
        for admin_class in reversed(self.__class__.mro()):
            if hasattr(admin_class, "fieldsets") and admin_class.fieldsets is not None:
                for set_ in admin_class.fieldsets:
                    if set_[0] not in store:
                        fieldsets.append(set_)
                        store.add(set_[0])

        return fieldsets
