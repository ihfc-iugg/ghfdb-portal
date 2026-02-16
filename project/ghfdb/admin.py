from django.contrib import admin
from django.utils.translation import gettext as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from fairdm.core.admin import MeasurementAdmin
from fairdm.db import models

from .models import ParentChildRelation, ParentHeatFlow


class ParentChildRelationInline(admin.TabularInline):
    model = ParentChildRelation
    extra = 1
    verbose_name = _("Child Heat Flow")
    verbose_name_plural = _("Child Heat Flows")
    fields = ("child", "is_relevant")
    raw_id_fields = ("child",)


@admin.register(ParentHeatFlow)
class ParentHeatFlowAdmin(MeasurementAdmin):
    list_display = ["sample", "value", "uncertainty", "is_ghfdb", "corr_HP_flag"]
    list_filter = ["is_ghfdb", "corr_HP_flag"]
    search_fields = ["sample__name"]

    inlines = [ParentChildRelationInline]

    fieldsets = (
        ("", {"fields": ("sample",)}),
        (
            "Heat Flow",
            {
                "fields": (
                    ("value", "uncertainty"),
                    "corr_HP_flag",
                    "is_ghfdb",
                )
            },
        ),
        (
            "Comments",
            {
                "fields": ("comment",)
            },
        ),
    )

    formfield_overrides = {
        models.ManyToManyField: {"widget": Select2MultipleWidget},
        models.ForeignKey: {"widget": Select2Widget},
    }
