from django.contrib import admin
from django.utils.translation import gettext as _
from heat_flow.models import HeatFlow, HeatFlowChild


class HeatFlowChildInline(admin.StackedInline):
    model = HeatFlowChild
    max_num = 0


@admin.register(HeatFlow)
class HeatFlowAdmin(admin.ModelAdmin):
    list_display = [  # noqa: RUF012
        "id",
        "q",
        "q_uncertainty",
    ]

    list_filter = ["environment", "explo_method", "explo_purpose"]

    inlines = [HeatFlowChildInline]
    readonly_fields = ["uuid"]
    fieldsets = [  # noqa: RUF012
        (
            "Heat Flow",
            {"fields": ["uuid", "q", "q_uncertainty"]},
        ),
    ]

    search_fields = [
        "uuid",
    ]
    point_zoom = 8
    map_width = 900
    modifiable = True


@admin.register(HeatFlowChild)
class HeatFlowChildAdmin(admin.ModelAdmin):
    list_display = [
        "relevant_child",
        "q_top",
        "q_bottom",
        "qc",
        "qc_uncertainty",
        "q_method",
        "water_temperature",
        "tc_mean",
        "tc_saturation",
        "tc_pT_conditions",
        "tc_strategy",
    ]
    list_filter = [
        "q_method",
        "probe_type",
        "tc_source",
        "tc_strategy",
    ]

    # inlines = [CorrectionInline]

    fieldsets = [  # noqa: RUF012
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
                    ("qc", "qc_uncertainty"),
                    "q_method",
                    "q_top",
                    "q_bottom",
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
                    "probe_type",
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
