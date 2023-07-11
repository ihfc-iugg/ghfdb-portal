from django.contrib import admin

# from django.db.models import F
from django.utils.translation import gettext as _
from geoluminate.contrib.gis.admin import SiteAdminMixin

# from heat_flow.resources import IntervalResource, SiteResource
# from quantityfield.fields import QuantityField
# from geoluminate.widgets import QuantityFormField
from heat_flow.models import HeatFlow, Interval, Temperature


class CorrectionInline(admin.TabularInline):
    model = Interval.corrections.through
    extra = 0


class TemperatureInline(admin.StackedInline):
    model = Temperature
    can_delete = False
    show_change_link = False
    max_num = 0


class IntervalInline(admin.StackedInline):
    model = Interval
    max_num = 0


@admin.register(HeatFlow)
class HeatFlowAdmin(SiteAdminMixin):
    # resource_class = SiteResource

    list_display = [
        "id",
        # "name",
        # "lon",
        # "lat",
        # "elevation",
        # "__str__",
        "q",
        "q_unc",
        "q_date_acq",
        # "environment",
        "water_temp",
        # "explo_method",
        # "explo_purpose",
        # "_reference",
    ]
    readonly_fields = ["id"]

    list_filter = ["environment", "explo_method", "explo_purpose"]

    inlines = [IntervalInline]
    fieldsets = [
        (
            "Geographic",
            {
                "fields": [
                    "id",
                    # "name",
                    # "geom",
                    # "elevation",
                    "borehole_depth",
                    "expedition",
                    # ('year', 'month'),
                    "q_date_acq",
                    # "environment",
                    # "water_temp",
                ]
            },
        ),
        (
            "Heat Flow",
            {"fields": ["q", "q_unc"]},
        ),
        (
            "Marine",
            {
                "fields": [
                    "water_temp",
                ]
            },
        ),
        (
            "References",
            {
                "fields": [
                    "literature",
                ]
            },
        ),
        (
            "Comment",
            {
                "fields": [
                    "comment",
                ]
            },
        ),
    ]

    search_fields = [
        "id",
        # "name",
    ]
    point_zoom = 8
    map_width = 900
    modifiable = True

    def coords(self, obj):
        return obj.geom.coords


@admin.register(Interval)
class IntervalAdmin(admin.ModelAdmin):
    list_display = [
        "relevant_child",
        "q_top",
        "q_bot",
        "qc",
        "qc_unc",
        "q_method",
        "tc_mean",
        "tc_saturation",
        "tc_pT_conditions",
        "tc_strategy",
    ]
    list_filter = [
        "q_tf_mech",
        "q_method",
        "hf_probe",
        "tc_source",
        "tc_strategy",
    ]

    inlines = [
        TemperatureInline,
        CorrectionInline,
    ]

    fieldsets = [
        (
            _("Metadata"),
            {
                "fields": [
                    "relevant_child",
                    # "lithology",
                    # "stratigraphy",
                ],
            },
        ),
        (
            _("Heat Flow"),
            {
                "fields": [
                    ("qc", "qc_unc"),
                    # "q_tf_mech",
                    "q_method",
                    "q_top",
                    "q_bot",
                    # 'corrections',
                ],
            },
        ),
        (
            _("Probe Sensing"),
            {
                "fields": [
                    "hf_pen",
                    "probe_tilt",
                    "hf_probe",
                    "hf_probeL",
                ],
            },
        ),
        # (
        #     _("Temperature"),
        #     {
        #         "fields": [
        #             ("T_grad_mean", "T_grad_uncertainty"),
        #             ("T_grad_mean_cor", "T_grad_uncertainty_cor"),
        #             ("T_method_top", "T_correction_top", "T_shutin_top"),
        #             ("T_method_bottom", "T_correction_bottom", "T_shutin_bottom"),
        #             "T_count",
        #         ],
        #     },
        # ),
        (
            _("Thermal Conductivity"),
            {
                "fields": [
                    ("tc_mean", "tc_uncertainty"),
                    "tc_source",
                    "tc_method",
                    "tc_saturation",
                    "tc_pT_conditions",
                    "tc_pT_function",
                    "tc_strategy",
                    "tc_count",
                ],
            },
        ),
    ]
