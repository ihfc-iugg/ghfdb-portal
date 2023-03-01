from django.contrib import admin
from django.db.models import F
from django.utils.translation import gettext as _

# from .admin_forms import AdminIntervalForm
from geoluminate.contrib.gis.admin import SiteAdminMixin
from geoluminate.widgets import QuantityFieldWidget, QuantityFormField
from ghfdb.models import HeatFlow, Interval
from ghfdb.resources import IntervalResource, SiteResource
from import_export.admin import ImportExportActionModelAdmin
from quantityfield import fields, widgets
from quantityfield.fields import QuantityField


class CorrectionInline(admin.TabularInline):
    model = Interval.corrections.through
    extra = 0


@admin.register(HeatFlow)
class HeatFlowAdmin(SiteAdminMixin, ImportExportActionModelAdmin):
    # form = AdminSiteForm
    resource_class = SiteResource

    list_display = [
        "id",
        "name",
        "lon",
        "lat",
        "elevation",
        "__str__",
        "q",
        "q_unc",
        "q_date_acq",
        # "environment",
        "water_temp",
        # "explo_method",
        # "explo_purpose",
        "_reference",
    ]
    readonly_fields = ["id"]

    list_filter = ["environment", "explo_method", "explo_purpose"]
    # date_hierarchy = "q_date_acq"

    # filter_horizontal = ['references']
    # raw_id_fields = ("references",)

    # autocomplete_lookup_fields = {
    #     "m2m": ["references"],
    # }

    fieldsets = [
        (
            "Geographic",
            {
                "fields": [
                    "id",
                    "name",
                    # "geom",
                    "elevation",
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
        "name",
        "references__label",
    ]
    point_zoom = 8
    map_width = 900
    modifiable = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("references")

    def _reference(self, obj):
        return ",".join([r.label for r in obj.references.all() if r.label])

    def coords(self, obj):
        return obj.geom.coords


@admin.register(Interval)
class IntervalAdmin(SiteAdminMixin, ImportExportActionModelAdmin):
    # form = AdminIntervalForm
    geom_field = "site__geom"
    resource_class = IntervalResource
    # autocomplete_fields = ["site"]
    search_fields = ["site__name"]
    list_display = [
        "site",
        "lon",
        "lat",
        "relevant_child",
        "q_top",
        "q_bot",
        "qc",
        "qc_unc",
        "q_method",
        "T_grad_mean",
        "T_method_top",
        "T_correction_top",
        "T_method_bottom",
        "T_correction_bottom",
        "tc_mean",
        "tc_saturation",
        "tc_pT_conditions",
        "tc_strategy",
        "reference",
    ]
    list_filter = [
        "q_tf_mech",
        "q_method",
        "hf_probe",
        "T_method_top",
        "T_method_bottom",
        "T_correction_top",
        "T_correction_bottom",
        "tc_source",
        "tc_strategy",
    ]

    inlines = [
        CorrectionInline,
    ]
    raw_id_fields = (
        "reference",
        "stratigraphy",
    )
    autocomplete_lookup_fields = {
        "fk": [
            "reference",
            "stratigraphy",
        ],
        "m2m": [],
    }

    fieldsets = [
        (
            _("Metadata"),
            {
                "fields": [
                    "site",
                    "reference",
                    "relevant_child",
                    "lithology",
                    "stratigraphy",
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
        (
            _("Temperature"),
            {
                "fields": [
                    ("T_grad_mean", "T_grad_uncertainty"),
                    ("T_grad_mean_cor", "T_grad_uncertainty_cor"),
                    ("T_method_top", "T_correction_top", "T_shutin_top"),
                    ("T_method_bottom", "T_correction_bottom", "T_shutin_bottom"),
                    "T_count",
                ],
            },
        ),
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

    formfield_overrides = {
        QuantityField: {
            "form_class": QuantityFormField,
        },
        # QuantityField: {"widget": QuantityFieldWidget},
    }

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("reference")
            .select_related("site")
            .annotate(name=F("site__name"))
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["lithology"].widget.can_add_related = False
        return form

    def lat(self, obj):
        return obj.site.geom.y

    def lon(self, obj):
        return obj.site.geom.x
