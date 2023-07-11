from geoluminate import api

from .models import HeatFlow, Interval


@api.register
class SampleEndpoint(api.Endpoint):
    model = HeatFlow


@api.register
class SiteEndpoint(api.Endpoint):
    model = Interval
