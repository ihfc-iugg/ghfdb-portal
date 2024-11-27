import django_tables2 as tables
from earth_science.tables import PointTable
from geoluminate.contrib.core.tables import MeasurementTable

from .models import ChildHeatFlow, HeatFlowSite, ParentHeatFlow


class HeatFlowSiteTable(PointTable):
    class Meta:
        model = HeatFlowSite
        exclude = ["path", "status", "has_children", "has_parent", "site_icon"]
        fields = [
            "id",
            "dataset",
            "name",
            # "location",
            "latitude",
            "longitude",
            "elevation",
            "environment",
            "explo_method",
            "explo_purpose",
            "total_depth_MD",
            "total_depth_TVD",
        ]


class ParentHeatFlowTable(MeasurementTable):
    site = tables.Column(verbose_name="name", accessor="sample", linkify=True)

    class Meta:
        model = ParentHeatFlow
        fields = ["site", "lat_NS", "heat_flow"]


class ChildHeatFlowTable(MeasurementTable):
    id = tables.Column(verbose_name="id", visible=False)
    # parent = tables.Column(verbose_name="name", accessor="parent", linkify=True)
    value = tables.Column(verbose_name="qc")
    uncertainty = tables.Column(verbose_name="qc_uncertainty")
    method = tables.Column(verbose_name="q_method")
    probe_penetration = tables.Column(verbose_name="probe_penetration")
    relevant_child = tables.Column(verbose_name="relevant_child")

    class Meta:
        model = ChildHeatFlow
        exclude = [
            "created",
            "modified",
            "polymorphic_ctype",
            "name",
            "sample",
            "parent",
            "options",
            "measurement_ptr",
            "image",
        ]


class GHFDBTable(tables.Table):
    parent__value = tables.Column(verbose_name="q")
    parent__uncertainty = tables.Column(verbose_name="q_uncertainty")

    class Meta:
        model = ChildHeatFlow
        fields = [
            "id",
            "parent__sample__name",
            "parent__value",
            "parent__uncertainty",
            "value",
            "uncertainty",
        ]
