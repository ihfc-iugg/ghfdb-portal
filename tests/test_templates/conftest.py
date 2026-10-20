# Fixtures for the measurement page tests. The page is read through its URL, and the
# quality card is found by the data- hooks the template carries for this purpose.

from html.parser import HTMLParser

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

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
def page(client, admin_user):
    """Return a function that fetches a measurement's page, signed in, and parses it.

    The reader is a superuser, who may open every record, so the quality card is found
    whichever dataset a fixture's records are in.
    """
    client.force_login(admin_user)

    def fetch(measurement):
        response = client.get(
            reverse("measurement:overview", kwargs={"uuid": measurement.uuid})
        )
        assert response.status_code == 200
        return Page(response.content.decode())

    return fetch


@pytest.fixture
def query_count(client, admin_user):
    """Return a function that counts the queries one request to a measurement's page makes.

    The first request fills process-wide caches, so it is made before the one that is counted.
    The reader is a superuser, as in ``page``.
    """
    client.force_login(admin_user)

    def count(measurement):
        url = reverse("measurement:overview", kwargs={"uuid": measurement.uuid})
        client.get(url)
        with CaptureQueriesContext(connection) as queries:
            client.get(url)
        return len(queries)

    return count


@pytest.fixture
def probe_interval(published_dataset):
    """An offshore probe interval 1000 m under water, in a dataset anyone may open.

    The water depth costs the gradient 0.2, which a bottom-water correction waives, so a
    child that records that correction scores 0.2 above the gradient's own score.
    """
    site = HeatFlowSiteFactory(
        dataset=published_dataset, explo_method="probing_offshore", elevation=-1000
    )
    interval = HeatFlowIntervalFactory(dataset=published_dataset, site=site)
    ProbeMetadataFactory(interval=interval, penetration=5, tilt=0, probe_type=[])
    return interval


@pytest.fixture
def gradient(probe_interval, published_dataset):
    gradient = ThermalGradientFactory(
        dataset=published_dataset,
        sample=probe_interval,
        number=6,
        method_top=[],
        method_bottom=[],
    )
    gradient.refresh_from_db()
    return gradient


@pytest.fixture
def conductivity(probe_interval, published_dataset):
    """A conductivity whose scored concepts are all empty, so its TC-score is marked."""
    conductivity = IntervalConductivityFactory(
        dataset=published_dataset,
        sample=probe_interval,
        number=4,
        source=[],
        conductivity_location=[],
        method=[],
        saturation=[],
        pT_conditions=[],
    )
    conductivity.refresh_from_db()
    return conductivity


@pytest.fixture
def child(probe_interval, gradient, conductivity, published_dataset):
    """A child whose bottom-water correction changes its T-score."""
    child = HeatFlowFactory(
        dataset=published_dataset,
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


class Node:
    """One element of a parsed page: its attributes, children and text."""

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = attrs
        self.children = []

    @property
    def text(self):
        """All the text under the element, with its whitespace collapsed."""
        parts = [c if isinstance(c, str) else c.text for c in self.children]
        return " ".join(" ".join(parts).split())

    def descendants(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.descendants()

    def find_all(self, attr, value=None):
        """Return the elements below this one that carry ``attr`` (with ``value``)."""
        return [
            node
            for node in self.descendants()
            if attr in node.attrs and (value is None or node.attrs[attr] == value)
        ]

    def find(self, attr, value=None):
        """Return the first element carrying ``attr`` (with ``value``), or ``None``."""
        found = self.find_all(attr, value)
        return found[0] if found else None

    @property
    def hrefs(self):
        """The link targets below this element."""
        return [n.attrs.get("href") for n in self.descendants() if n.tag == "a"]


class Document(HTMLParser):
    """A page parsed into elements that tests find by their ``data-`` attributes."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta"}

    def __init__(self, html):
        super().__init__()
        self.root = Node("document", {})
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def find_all(self, attr, value=None):
        return self.root.find_all(attr, value)

    def find(self, attr, value=None):
        return self.root.find(attr, value)


@pytest.fixture
def document(client, db):
    """Return a function that fetches a record's overview page and parses it.

    Pass ``user`` to read the page signed in, and any other keyword as a query
    parameter.
    """

    def fetch(record, user=None, **query):
        if user is not None:
            client.force_login(user)
        response = client.get(record.get_absolute_url(), query)
        assert response.status_code == 200
        return Document(response.content.decode())

    return fetch


@pytest.fixture
def quality_hooks(client, db):
    """Return a function that fetches a record's page and parses its quality hooks."""

    def fetch(record):
        response = client.get(record.get_absolute_url())
        assert response.status_code == 200
        return Page(response.content.decode())

    return fetch
