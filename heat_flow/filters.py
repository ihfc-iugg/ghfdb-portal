import django_filters as df
from geoluminate.contrib.core.filters import SampleFilter

from .models import ChildHeatFlow, HeatFlowSite


class HeatFlowSiteFilter(SampleFilter):
    class Meta:
        model = HeatFlowSite
        fields = ["name", "environment", "explo_method", "explo_purpose", "lithology", "age", "stratigraphy"]


class ChildHeatFlowFilter(df.FilterSet):
    class Meta:
        model = ChildHeatFlow
        exclude = ["created", "modified", "polymorphic_ctype", "options", "measurement_ptr", "image"]
