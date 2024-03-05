from django.contrib import admin

from .models import HeatFlow, HeatFlowChild

admin.site.unregister(HeatFlow)
admin.site.unregister(HeatFlowChild)


@admin.register(HeatFlow)
class HeatFlowAdmin(admin.ModelAdmin):
    list_display = [
        "q",
        "q_uncertainty",
        "environment",
        "total_depth_MD",
        "total_depth_TVD",
        "explo_method",
        "explo_purpose",
        "corr_HP_flag",
    ]

    list_filter = [
        "environment",
        "explo_method",
        "explo_purpose",
        "corr_HP_flag",
    ]

    fieldsets = (
        (
            None,
            {"fields": ("sample",)},
        ),
        (
            "Heat Flow",
            {
                "fields": (
                    ("q", "q_uncertainty"),
                    "environment",
                    "corr_hp_flag",
                    ("total_depth_MD", "total_depth_TVD"),
                    ("explo_method", "explo_purpose"),
                )
            },
        ),
    )


@admin.register(HeatFlowChild)
class HeatFlowChildAdmin(admin.ModelAdmin):
    list_display = [
        "parent",
        "qc",
        "qc_uncertainty",
    ]

    list_filter = ["parent__uuid"]

    fieldsets = (
        (
            "Heat Flow",
            {
                "fields": (
                    "parent",
                    "relevant_child",
                    ("qc", "qc_uncertainty"),
                    ("q_top", "q_bottom"),
                    "q_method",
                )
            },
        ),
        (
            "Probe Sensing",
            {
                "fields": (
                    ("probe_penetration", "probe_type", "probe_length"),
                    "probe_tilt",
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
                    ("T_correction_top", "T_correction_bottom"),
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
                    "expedition",
                    "water_temperature",
                    "lithology",
                    "IGSN",
                )
            },
        ),
    )
