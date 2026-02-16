import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.collections.tables import MeasurementTable, SampleTable

from heat_flow.models.measurements import IntervalConductivity, ThermalGradient

from .models import HeatFlow, HeatFlowInterval, HeatFlowSite


class HeatFlowSiteTable(SampleTable):
    name = tables.Column(verbose_name=_("Site name"), linkify=True)

    class Meta:
        model = HeatFlowSite
        fields = [
            "id",
            "dataset",
            "location",
            "name",
            "latitude",
            "longitude",
            "elevation",
            "country",
            "region",
            "continent",
            "domain",
            # "elevation_datum",
            # "azimuth",
            # "inclination",
            "length",
            "environment",
            "explo_method",
            "explo_purpose",
            "lithology",
            "age",
            # "stratigraphy",
        ]
        attrs = {
            "thead": {
                "th": {"class": "text-nowrap"}  # class for all <th> elements
            }
        }


class HeatFlowIntervalTable(SampleTable):
    class Meta:
        model = HeatFlowInterval
        fields = [
            "id",
            "dataset",
            "location",
            "latitude",
            "longitude",
            "top",
            "bottom",
            "vertical_depth",
            # "vertical_datum",
            "lithology",
            "age",
            # "stratigraphy",
            # "status",
            # "local_id",
        ]
        exclude = ["name"]

    def __init__(self, data=None, *args, **kwargs):
        # data = data.prefetch_related("sample__heatflowsite")
        # modify the queryset (data) here if required
        super().__init__(*args, data=data, **kwargs)


class IntervalMixin:
    def __init__(self, data=None, *args, **kwargs):
        # modify the queryset (data) here if required
        data = data.prefetch_related("sample__heatflowinterval")
        super().__init__(*args, data=data, **kwargs)


class HeatFlowTable(IntervalMixin, MeasurementTable):
    class Meta:
        model = HeatFlow
        exclude = ["latitude", "longitude"]
        fields = [
            "id",
            "dataset",
            "location",
            "sample",
            "sample__heatflowinterval__top",
            "sample__heatflowinterval__bottom",
            "value",
            "uncertainty",
            "method",
            "thermal_gradient",
            "thermal_conductivity",
            "expedition",
            "probe_penetration",
            "probe_length",
            "probe_tilt",
            "water_temperature",
            "corr_IS_flag",
            "corr_T_flag",
            "corr_S_flag",
            "corr_E_flag",
            "corr_TOPO_flag",
            "corr_PAL_flag",
            "corr_SUR_flag",
            "corr_CONV_flag",
            "corr_HR_flag",
        ]


class ThermalGradientTable(IntervalMixin, MeasurementTable):
    # depth_top = tables.Column(verbose_name=_("Top depth"), empty_values=())

    class Meta:
        model = ThermalGradient
        exclude = ["latitude", "longitude"]
        fields = [
            "id",
            "dataset",
            "location",
            "sample",
            # "sample_type",
            "sample__heatflowinterval__top",
            "sample__heatflowinterval__bottom",
            # "sample__top",
            # "sample__bottom",
            # "depth_top",
            "value",
            "uncertainty",
            "corrected_value",
            "corrected_uncertainty",
            "method_top",
            "method_bottom",
            "shutin_top",
            "shutin_bottom",
            "correction_top",
            "correction_bottom",
            "number",
        ]


class ThermalConductivityTable(IntervalMixin, MeasurementTable):
    # depth_top = tables.Column(verbose_name=_("Top depth"), empty_values=())

    class Meta:
        model = IntervalConductivity
        fields = [
            "id",
            "dataset",
            "location",
            "sample",
            # "sample_type",
            "sample__heatflowinterval__top",
            "sample__heatflowinterval__bottom",
            # "sample__top",
            # "sample__bottom",
            # "depth_top",
            "value",
            "uncertainty",
            "corrected_value",
            "corrected_uncertainty",
            "method_top",
            "method_bottom",
            "shutin_top",
            "shutin_bottom",
            "correction_top",
            "correction_bottom",
            "number",
        ]

