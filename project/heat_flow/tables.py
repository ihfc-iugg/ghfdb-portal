"""Table definitions for the heat flow schema's list views."""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.collections.tables import MeasurementTable, SampleTable

from heat_flow.models.child import ThermalGradient

from .models import HeatFlow, HeatFlowInterval, HeatFlowSite


class HeatFlowSiteTable(SampleTable):
    """Table of heat flow sites for the site list view."""

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
            "length",
            "environment",
            "explo_method",
            "explo_purpose",
            "lithology",
            "age",
        ]
        attrs = {"thead": {"th": {"class": "text-nowrap"}}}


class HeatFlowIntervalTable(SampleTable):
    """Table of heat flow depth intervals for the interval list view."""

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
            "lithology",
            "age",
        ]
        exclude = ["name"]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, data=data, **kwargs)


class IntervalMixin:
    """Prefetch the sample's heat flow interval for tables that display it."""

    def __init__(self, data=None, *args, **kwargs):
        data = data.prefetch_related("sample__heatflowinterval")
        super().__init__(*args, data=data, **kwargs)


class HeatFlowTable(IntervalMixin, MeasurementTable):
    """Table of child heat flow measurements for the measurement list view."""

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
            "surface_temperature",
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
    """Table of thermal gradient measurements for the measurement list view."""

    class Meta:
        model = ThermalGradient
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
