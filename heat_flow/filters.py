from fairdm.core.filters import MeasurementFilter, SampleFilter

from .models import HeatFlow, HeatFlowSite


class HeatFlowSiteFilter(SampleFilter):
    class Meta:
        model = HeatFlowSite
        fields = ["name", "environment", "explo_method", "explo_purpose", "lithology", "age", "stratigraphy"]


class HeatFlowFilter(MeasurementFilter):
    class Meta:
        model = HeatFlow
        exclude = ["created", "modified", "polymorphic_ctype", "options", "measurement_ptr", "image", "tags"]
