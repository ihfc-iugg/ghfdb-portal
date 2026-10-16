"""Table definitions for the heat flow schema's list views."""

import django_tables2 as tables
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.collections.tables import MeasurementTable, SampleTable

from heat_flow.models.child import ThermalGradient

from .models import HeatFlow, HeatFlowInterval, HeatFlowSite, IntervalConductivity


class SiteCoordinatesTable(tables.Table):
    """Latitude and longitude of the site a row is placed at.

    A site is a named location, so an interval and its measurements are
    placed at their site and show its coordinates. They are shown only to a
    viewer who may see the site itself.

    Attributes:
        site_path: The lookup from a row to its ``HeatFlowSite``, empty when
            the row is the site.
    """

    site_path = ""

    latitude = tables.Column(
        empty_values=(), verbose_name=_("Latitude"), orderable=False
    )
    longitude = tables.Column(
        empty_values=(), verbose_name=_("Longitude"), orderable=False
    )

    def render_latitude(self, record):
        """Return the latitude of the row's site, where the viewer may see it."""
        location = self.site_location(record)
        return self.default if location is None else location.y

    def render_longitude(self, record):
        """Return the longitude of the row's site, where the viewer may see it."""
        location = self.site_location(record)
        return self.default if location is None else location.x

    def site_of(self, record):
        """Return the site a row is placed at.

        Args:
            record: The row's object.

        Returns:
            The ``HeatFlowSite``, or None when the row has none.
        """
        site = record
        for name in filter(None, self.site_path.split("__")):
            site = getattr(site, name, None)
        return site

    def site_location(self, record):
        """Return the point of the row's site, for a viewer who may see the site.

        Args:
            record: The row's object.

        Returns:
            The site's ``location``, or None where there is none to show.
        """
        site = self.site_of(record)
        if site is None or site.location is None:
            return None
        return site.location if site.pk in self.visible_site_ids else None

    @cached_property
    def visible_site_ids(self):
        """Return the keys of the sites on this page that the viewer may see."""
        rows = self.page.object_list if hasattr(self, "page") else self.rows
        sites = {site.pk for site in (self.site_of(row.record) for row in rows) if site}
        user = getattr(getattr(self, "request", None), "user", None)
        return set(
            HeatFlowSite.objects.visible_to(user)
            .filter(pk__in=sites)
            .values_list("pk", flat=True)
        )


class HeatFlowSiteTable(SampleTable, SiteCoordinatesTable):
    """Table of heat flow sites for the site list view."""

    name = tables.Column(verbose_name=_("Site name"), linkify=True)

    class Meta:
        model = HeatFlowSite
        fields = [
            "id",
            "dataset",
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


class HeatFlowIntervalTable(SampleTable, SiteCoordinatesTable):
    """Table of heat flow depth intervals for the interval list view."""

    site_path = "site"

    class Meta:
        model = HeatFlowInterval
        fields = [
            "id",
            "dataset",
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
        super().__init__(*args, data=data.select_related("site"), **kwargs)


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


class IntervalConductivityTable(MeasurementTable, SiteCoordinatesTable):
    """Table of interval thermal conductivities for the measurement list view."""

    site_path = "sample__heatflowinterval__site"

    class Meta:
        model = IntervalConductivity
        # The columns the registry built for this type before it had a table of
        # its own: these and the ones every measurement table declares.
        fields = [
            "value",
            "uncertainty",
            "method",
            "strategy",
            "source",
            "saturation",
            "pT_conditions",
            "pT_function",
        ]

    def __init__(self, data=None, *args, **kwargs):
        data = data.select_related("sample__heatflowinterval__site")
        super().__init__(*args, data=data, **kwargs)
