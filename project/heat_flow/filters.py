"""Filter sets for heat flow sites and measurements."""

from fairdm.core.measurement.filters import MeasurementFilter
from fairdm.core.sample.filters import SampleFilter

from .models import HeatFlow, HeatFlowSite


class HeatFlowSiteFilter(SampleFilter):
    """Filter heat flow sites by location and geological attributes."""

    class Meta:
        model = HeatFlowSite
        fields = [
            "name",
            "environment",
            "explo_method",
            "explo_purpose",
            "country",
            "continent",
            "region",
            "domain",
            "lithology",
            "age",
            "stratigraphy",
        ]


class HeatFlowFilter(MeasurementFilter):
    """Filter heat flow measurements, excluding internal bookkeeping fields."""

    class Meta:
        model = HeatFlow
        exclude = [
            "created",
            "modified",
            "polymorphic_ctype",
            "options",
            "measurement_ptr",
            "image",
            "tags",
            "date_acquired",
        ]
