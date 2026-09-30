# Fixtures for the measurement page tests. The page is read through its URL, and the
# quality card is found by the data- hooks the template carries for this purpose.

from html.parser import HTMLParser

import pytest
from django.urls import reverse
from django.test.utils import CaptureQueriesContext
from django.db import connection

from tests.factories import (
    HeatFlowCorrectionFactory,
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ProbeMetadataFactory,
    ThermalGradientFactory,
)


class Hook:
    """One element carrying a ``data-quality`` hook: its attributes and visible text."""

    def __init__(self, attrs):
        self.attrs = attrs
        self.text = ""
        self.marks = []

    @property
    def value(self):
        return self.attrs.get("data-value")

    @property
    def state(self):
        return self.attrs.get("data-state")

    @property
    def missing(self):
        return self.attrs.get("data-missing")


class Page(HTMLParser):
    """The hooks found in a rendered page, keyed by their ``data-quality`` value."""

    def __init__(self, html):
        super().__init__()
        self.hooks = {}
        self.cards = []
        self.alerts = 0
        self._open = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("role") == "alert":
            self.alerts += 1
        if "data-quality-card" in attrs:
            self.cards.append(attrs["data-quality-card"])
        if "data-quality" in attrs:
            hook = Hook(attrs)
            self.hooks[attrs["data-quality"]] = hook
            self._open.append((tag, hook))
        elif "data-quality-mark" in attrs and self._open:
            mark = Hook(attrs)
            self._open[-1][1].marks.append(mark)
            self._open.append((tag, mark))

    def handle_endtag(self, tag):
        if self._open and self._open[-1][0] == tag:
            self._open.pop()

    def handle_data(self, data):
        for _, hook in self._open:
            hook.text += data


@pytest.fixture
def page(client, db):
    """Return a function that fetches a measurement's page and parses it."""

    def fetch(measurement):
        response = client.get(
            reverse("measurement:overview", kwargs={"uuid": measurement.uuid})
        )
        assert response.status_code == 200
        return Page(response.content.decode())

    return fetch


@pytest.fixture
def query_count(client, db):
    """Return a function that counts the queries one request to a measurement's page makes.

    The first request fills process-wide caches, so it is made before the one that is counted.
    """

    def count(measurement):
        url = reverse("measurement:overview", kwargs={"uuid": measurement.uuid})
        client.get(url)
        with CaptureQueriesContext(connection) as queries:
            client.get(url)
        return len(queries)

    return count


@pytest.fixture
def probe_interval(db):
    """An offshore probe interval 1000 m under water.

    The water depth costs the gradient 0.2, which a bottom-water correction waives, so a
    child that records that correction scores 0.2 above the gradient's own score.
    """
    site = HeatFlowSiteFactory(explo_method="probing_offshore", elevation=-1000)
    interval = HeatFlowIntervalFactory(site=site)
    ProbeMetadataFactory(interval=interval, penetration=5, tilt=0, probe_type=[])
    return interval


@pytest.fixture
def gradient(probe_interval):
    gradient = ThermalGradientFactory(
        sample=probe_interval, number=6, method_top=[], method_bottom=[]
    )
    gradient.refresh_from_db()
    return gradient


@pytest.fixture
def conductivity(probe_interval):
    """A conductivity whose scored concepts are all empty, so its TC-score is marked."""
    conductivity = IntervalConductivityFactory(
        sample=probe_interval,
        number=4,
        source=[],
        location=[],
        method=[],
        saturation=[],
        pT_conditions=[],
    )
    conductivity.refresh_from_db()
    return conductivity


@pytest.fixture
def child(probe_interval, gradient, conductivity):
    """A child whose bottom-water correction changes its T-score."""
    child = HeatFlowFactory(
        sample=probe_interval,
        value=70,
        uncertainty=7,
        method=[],
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
    )
    HeatFlowCorrectionFactory(
        heat_flow=child, correction_type="SUR", status="present_corrected"
    )
    child.refresh_from_db()
    return child
