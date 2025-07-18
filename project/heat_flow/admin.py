from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from fairdm.core.admin import MeasurementAdmin, SampleAdmin
from fairdm.db import models

from .models import HeatFlow, HeatFlowInterval, HeatFlowSite, SurfaceHeatFlow


class UploadForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


def admin_urlname(opts, name):
    return f"admin:{opts.app_label}_{opts.model_name}_{name}"


@admin.register(SurfaceHeatFlow)
class SurfaceHeatFlowAdmin(MeasurementAdmin):
    list_display = ["value", "uncertainty", "corr_HP_flag"]

    fields = (
        "sample",
        ("value", "uncertainty"),
        "corr_HP_flag",
    )


@admin.register(HeatFlow)
class HeatFlowAdmin(admin.ModelAdmin):
    list_display = [
        "parent",
        "value",
        "uncertainty",
    ]

    fieldsets = (
        ("", {"fields": ("sample",)}),
        (
            "Heat Flow",
            {
                "fields": (
                    "parent",
                    "relevant_child",
                    ("value", "uncertainty"),
                    # ("depth_top", "depth_bottom"),
                    "method",
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
