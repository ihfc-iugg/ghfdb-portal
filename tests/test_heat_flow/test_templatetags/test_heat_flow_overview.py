# Tests for the heat flow overview tag library. Mirrors
# ``project/heat_flow/templatetags/heat_flow_overview.py``.

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.template import engines
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.utils import translation
from heat_flow.models import HeatFlow
from heat_flow.templatetags.heat_flow_overview import labels, plus_minus

from tests.factories import HeatFlowFactory, HeatFlowSiteFactory, ThermalGradientFactory

pytestmark = pytest.mark.django_db


def render(source, **context):
    """Render a template string the way a page does, for an anonymous visitor."""
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    template = engines["django"].from_string("{% load heat_flow_overview %}" + source)
    return template.render({"request": request, **context})


class TestLabels:
    def test_a_graph_concept_gives_its_label(self):
        site = HeatFlowSiteFactory(environment="onshore_continental")
        site.refresh_from_db()

        assert labels(site.environment) == site.environment.label("en")
        assert labels(site.environment) != ""

    def test_a_graph_concept_gives_its_label_in_the_active_language(self):
        class Concept:
            """A graph concept, whose label is asked for in a language."""

            def label(self, lang="en"):
                return f"term-{lang}"

        with translation.override("de"):
            assert labels(Concept()) == "term-de"

    def test_a_many_to_many_of_two_gives_both_labels_joined_by_a_comma(self):
        child = HeatFlowFactory()
        concepts = list(child.method.model.objects.all()[:2])
        child.method.set(concepts)

        result = labels(child.method)

        assert sorted(result.split(", ")) == sorted(c.label for c in concepts)

    def test_an_empty_many_to_many_gives_nothing(self):
        child = HeatFlowFactory(method=[])

        assert labels(child.method) == ""

    def test_nothing_gives_nothing(self):
        assert labels(None) == ""


class TestPlusMinus:
    @pytest.fixture
    def gradient(self):
        gradient = ThermalGradientFactory(value=17.63, uncertainty=0.91)
        gradient.refresh_from_db()
        return gradient

    def test_it_writes_the_value_and_uncertainty_before_the_unit(self, gradient):
        result = plus_minus(gradient.value, gradient.uncertainty)

        assert result == f"17.63 ± 0.91 {gradient.value.units:~P}"

    def test_it_writes_the_value_alone_without_an_uncertainty(self, gradient):
        result = plus_minus(gradient.value, None)

        assert result == f"17.63 {gradient.value.units:~P}"

    def test_it_writes_nothing_for_an_empty_value(self, gradient):
        assert plus_minus(None, gradient.uncertainty) == ""

    def test_it_is_a_filter_a_template_can_apply(self, gradient):
        result = render(
            "{{ value|plus_minus:uncertainty }}",
            value=gradient.value,
            uncertainty=gradient.uncertainty,
        )

        assert result == plus_minus(gradient.value, gradient.uncertainty)


class TestHeatFlowPage:
    @pytest.fixture
    def child(self, page_records):
        return page_records["child"]

    def queries(self, source, **context):
        with CaptureQueriesContext(connection) as captured:
            render(source, **context)
        return len(captured)

    def test_it_hands_the_template_what_the_page_gathers(self, child):
        result = render(
            "{% heat_flow_page record as hf %}{{ hf.gradient.pk }}", record=child
        )

        assert result == str(child.thermal_gradient.pk)

    def test_two_blocks_asking_for_one_record_gather_it_once(self, child):
        one = "{% heat_flow_page record as hf %}{{ hf.stale }}"
        two = one + "{% heat_flow_page record as again %}{{ again.stale }}"

        assert self.queries(two, record=child) == self.queries(one, record=child)

    def test_a_second_record_is_gathered_on_its_own(self, child, page_records):
        other = HeatFlowFactory(
            dataset=child.dataset, sample=page_records["interval"], parent=None
        )
        other = HeatFlow.objects.get(pk=other.pk)
        source = (
            "{% heat_flow_page first as a %}{% heat_flow_page second as b %}"
            "{{ a.parent.pk }}|{{ b.parent.pk }}"
        )

        result = render(source, first=child, second=other)

        assert result == f"{child.parent.pk}|"


class TestOverviewPages:
    @pytest.mark.parametrize(
        "name",
        ["site", "interval", "gradient", "conductivity", "parent", "child"],
    )
    def test_every_heat_flow_page_renders_with_the_tag_library(
        self, client, page_records, name
    ):
        response = client.get(page_records[name].get_absolute_url())

        assert response.status_code == 200
