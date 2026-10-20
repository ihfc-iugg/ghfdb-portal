import random

import pytest
from django.core.exceptions import ValidationError
from heat_flow import demo
from heat_flow.demo import CHILDREN_CYCLE, REGIONS, SITES_PER_DATASET, DemoGraph, Region
from heat_flow.models import (
    HeatFlow,
    HeatFlowCorrection,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ProbeMetadata,
    ThermalGradient,
)
from heat_flow.overview import HeatFlowPage
from heat_flow.quality import SCHEME_REVISION, Reading

MULTI_TABLE_MODELS = (
    HeatFlowSite,
    HeatFlowInterval,
    ParentHeatFlow,
    HeatFlow,
    ThermalGradient,
    IntervalConductivity,
)

CONCEPT_FIELDS = (
    (HeatFlowSite, "explo_purpose"),
    (HeatFlow, "method"),
    (ThermalGradient, "method_top"),
    (ThermalGradient, "method_bottom"),
    (ThermalGradient, "correction_top"),
    (ThermalGradient, "correction_bottom"),
    (IntervalConductivity, "source"),
    (IntervalConductivity, "conductivity_location"),
    (IntervalConductivity, "method"),
    (IntervalConductivity, "saturation"),
    (IntervalConductivity, "pT_conditions"),
    (IntervalConductivity, "pT_function"),
    (IntervalConductivity, "strategy"),
    (ProbeMetadata, "probe_type"),
)


def metres(quantity):
    return Reading.magnitude(quantity, "m")


@pytest.fixture
def graph(dataset):
    """One dataset's full graph, built once per test with a fixed seed."""
    DemoGraph(dataset, random.Random(8)).build(sites=8)
    return dataset


class TestRegions:
    def test_every_region_names_vocabulary_values(self):
        for region in REGIONS:
            assert region.environment in HeatFlowSite.environment_vocab.values
            assert region.explo_method in HeatFlowSite.explo_method_vocab.values

    def test_every_region_has_valid_bounds(self):
        for region in REGIONS:
            assert -90 <= region.min_lat < region.max_lat <= 90
            assert -180 <= region.min_lon < region.max_lon <= 180

    def test_about_forty_percent_of_regions_are_marine(self):
        share = sum(region.marine for region in REGIONS) / len(REGIONS)

        assert 0.3 <= share <= 0.5

    def test_marine_regions_are_probed_and_land_regions_drilled(self):
        for region in REGIONS:
            expected = "probing_offshore" if region.marine else "drilling"
            assert region.explo_method == expected

    def test_a_region_is_a_named_tuple(self):
        assert isinstance(REGIONS[0], Region)


class TestDemoGraph:
    def test_every_model_has_rows(self, graph):
        for model in (*MULTI_TABLE_MODELS, HeatFlowCorrection, ProbeMetadata):
            assert model.objects.exists()

    def test_children_follow_the_cycle(self, dataset):
        DemoGraph(dataset, random.Random(8)).build()

        per_site = [
            site.intervals.count()
            for site in HeatFlowSite.objects.filter(dataset=dataset).order_by("pk")
        ]

        cycle = [CHILDREN_CYCLE[n % len(CHILDREN_CYCLE)] for n in range(len(per_site))]
        assert len(per_site) == SITES_PER_DATASET
        assert per_site == cycle
        assert HeatFlow.objects.filter(dataset=dataset).count() == sum(cycle)

    def test_every_multi_table_record_passes_full_clean(self, graph):
        for model in MULTI_TABLE_MODELS:
            for record in model.objects.filter(dataset=graph):
                record.full_clean()

    def test_every_multi_table_record_carries_the_graphs_dataset(self, graph):
        for model in MULTI_TABLE_MODELS:
            records = model.objects.all()
            assert records.count() > 0
            assert set(records.values_list("dataset_id", flat=True)) == {graph.pk}

    def test_a_conductivity_is_within_the_model_range_and_above_its_uncertainty(
        self, graph
    ):
        for conductivity in IntervalConductivity.objects.all():
            value = Reading.magnitude(conductivity.value, "W/mK")
            uncertainty = Reading.magnitude(conductivity.uncertainty, "W/mK")

            assert 0.1 <= value <= 50
            assert uncertainty <= value

    def test_every_child_value_is_its_gradient_times_its_conductivity(self, graph):
        for child in HeatFlow.objects.select_related(
            "thermal_gradient", "thermal_conductivity"
        ):
            product = Reading.magnitude(
                child.thermal_gradient.value, "K/km"
            ) * Reading.magnitude(child.thermal_conductivity.value, "W/mK")

            assert Reading.magnitude(child.value, "mW / m^2") == pytest.approx(
                product, abs=0.01
            )

    def test_every_site_has_exactly_one_parent(self, graph):
        for site in HeatFlowSite.objects.all():
            assert ParentHeatFlow.objects.filter(sample=site).count() == 1

    def test_every_child_belongs_to_a_parent_of_its_own_site(self, graph):
        for child in HeatFlow.objects.select_related("parent"):
            assert child.parent.sample_id == child.sample.site_id

    def test_a_parent_is_the_mean_of_its_relevant_children(self, graph):
        for parent in ParentHeatFlow.objects.all():
            relevant = [
                Reading.magnitude(child.value, "mW / m^2")
                for child in parent.children.filter(is_relevant=True)
            ]

            assert Reading.magnitude(parent.value, "mW / m^2") == pytest.approx(
                sum(relevant) / len(relevant), abs=0.01
            )

    def test_the_last_child_of_a_large_parent_is_not_relevant(self, graph):
        for parent in ParentHeatFlow.objects.all():
            children = list(parent.children.order_by("pk"))
            expected = [True] * len(children)
            if len(children) >= 3:
                expected[-1] = False

            assert [child.is_relevant for child in children] == expected

    def test_coordinates_are_pairwise_distinct(self, graph):
        points = [
            (site.location.x, site.location.y) for site in HeatFlowSite.objects.all()
        ]

        assert len(set(points)) == len(points)

    def test_top_is_above_bottom(self, graph):
        for interval in HeatFlowInterval.objects.all():
            assert metres(interval.top) < metres(interval.bottom)

    def test_every_interval_belongs_to_its_site(self, graph):
        assert not HeatFlowInterval.objects.filter(site__isnull=True).exists()

    def test_probe_intervals_have_probe_metadata_and_borehole_ones_do_not(self, graph):
        for interval in HeatFlowInterval.objects.select_related("site"):
            probed = interval.site.explo_method.name == "probing_offshore"

            assert hasattr(interval, "probe_metadata") is probed

    def test_both_probe_and_borehole_sites_are_built(self, graph):
        methods = {site.explo_method.name for site in HeatFlowSite.objects.all()}

        assert methods == {"probing_offshore", "drilling"}

    def test_corrections_satisfy_the_status_rules_for_their_type(self, graph):
        valid = {
            **HeatFlowCorrection.VALID_STATUS_FOR_TYPE,
            **dict.fromkeys(
                HeatFlowCorrection._ENVIRONMENTAL_TYPES,
                HeatFlowCorrection.ENVIRONMENTAL_VALID,
            ),
        }
        corrections = HeatFlowCorrection.objects.all()

        assert corrections.exists()
        for correction in corrections:
            assert correction.status in valid[correction.correction_type]

    def test_every_correction_is_accepted_by_save(self, graph):
        for correction in HeatFlowCorrection.objects.all():
            correction.save()

    def test_no_child_has_a_correction_type_twice(self, graph):
        pairs = list(
            HeatFlowCorrection.objects.values_list("heat_flow_id", "correction_type")
        )

        assert len(set(pairs)) == len(pairs)

    def test_probe_children_always_have_a_temperature_correction(self, graph):
        probed = HeatFlow.objects.filter(
            sample__heatflowinterval__probe_metadata__isnull=False
        )

        assert probed.exists()
        for child in probed:
            assert child.corrections.filter(correction_type="T").exists()

    @pytest.mark.parametrize(("model", "field"), CONCEPT_FIELDS)
    def test_every_concept_field_holds_a_concept_of_its_own_vocabulary(
        self, graph, model, field
    ):
        records = model.objects.all()
        vocabulary = model._meta.get_field(field).vocabulary().scheme().name

        assert records.exists()
        for record in records:
            concepts = list(getattr(record, field).all())
            assert len(concepts) == 1
            assert concepts[0].vocabulary.name == vocabulary

    def test_ghfdb_ids_are_set_on_parents_and_children_when_a_counter_is_given(
        self, dataset
    ):
        counter = iter(range(500, 10_000))

        DemoGraph(dataset, random.Random(3), lambda: next(counter)).build(sites=4)

        ids = [
            *ParentHeatFlow.objects.values_list("ghfdb_id", flat=True),
            *HeatFlow.objects.values_list("ghfdb_id", flat=True),
        ]
        assert None not in ids
        assert len(set(ids)) == len(ids)
        assert min(ids) == 500

    def test_no_ghfdb_id_is_set_without_a_counter(self, graph):
        assert not ParentHeatFlow.objects.exclude(ghfdb_id=None).exists()
        assert not HeatFlow.objects.exclude(ghfdb_id=None).exists()

    def test_a_second_graph_raises_no_collision_and_redraws(self, graph):
        first = {(s.location.x, s.location.y) for s in HeatFlowSite.objects.all()}

        DemoGraph(graph, random.Random(8)).build(sites=8)

        points = [(s.location.x, s.location.y) for s in HeatFlowSite.objects.all()]
        assert len(points) == 16
        assert len(set(points)) == len(points)
        assert first < set(points)

    def test_a_site_that_cannot_find_a_free_point_raises(self, dataset, monkeypatch):
        fixed = Region(
            "Fixed", 10.0, 10.0, 20.0, 20.0, False, "onshore_continental", "drilling"
        )
        monkeypatch.setattr(demo, "REGIONS", (fixed,))
        DemoGraph(dataset, random.Random(1)).build(sites=1)

        with pytest.raises(ValidationError):
            DemoGraph(dataset, random.Random(1)).build(sites=1)


# Each quantity's range is the tighter of research R3's table and the model's limit.
RANGES = (
    ("conductivity", IntervalConductivity, "value", "W/mK", 0.8, 6),
    ("gradient", ThermalGradient, "value", "K/km", 0, 300),
    ("corrected gradient", ThermalGradient, "corrected_value", "K/km", -999.99, 999.99),
    ("child heat flow", HeatFlow, "value", "mW / m^2", 0, 10**6),
    ("parent heat flow", ParentHeatFlow, "value", "mW / m^2", 0, 10**6),
    ("probe penetration", ProbeMetadata, "penetration", "m", 1, 10),
    ("probe length", ProbeMetadata, "length", "m", 1, 10),
    ("probe tilt", ProbeMetadata, "tilt", "°", 0, 20),
)


class TestDemoGraphRanges:
    @pytest.mark.parametrize(
        ("label", "model", "field", "unit", "low", "high"),
        RANGES,
        ids=[row[0] for row in RANGES],
    )
    def test_quantity_lies_within_its_range(
        self, graph, label, model, field, unit, low, high
    ):
        values = [
            Reading.magnitude(getattr(record, field), unit)
            for record in model.objects.all()
        ]

        assert values
        assert all(low <= value <= high for value in values)

    @pytest.mark.parametrize("model", [HeatFlow, ParentHeatFlow])
    def test_heat_flow_uncertainty_is_five_to_twenty_five_percent(self, graph, model):
        for record in model.objects.all():
            ratio = Reading.magnitude(
                record.uncertainty, "mW / m^2"
            ) / Reading.magnitude(record.value, "mW / m^2")

            assert 0.048 <= ratio <= 0.252

    def test_borehole_intervals_start_within_1500_m_and_are_50_to_1500_m_thick(
        self, graph
    ):
        boreholes = HeatFlowInterval.objects.filter(probe_metadata__isnull=True)

        assert boreholes.exists()
        for interval in boreholes:
            assert 0 <= metres(interval.top) <= 1500
            assert 50 <= metres(interval.bottom) - metres(interval.top) <= 1500

    def test_probe_intervals_run_from_the_surface_to_two_to_ten_metres(self, graph):
        probes = HeatFlowInterval.objects.filter(probe_metadata__isnull=False)

        assert probes.exists()
        for interval in probes:
            assert metres(interval.top) == 0
            assert 2 <= metres(interval.bottom) <= 10

    def test_elevation_is_below_sea_level_at_sea_and_above_it_on_land(self, graph):
        for site in HeatFlowSite.objects.all():
            elevation = metres(site.elevation)
            if site.explo_method.name == "probing_offshore":
                assert -6000 <= elevation <= -200
            else:
                assert 0 <= elevation <= 3000

    def test_every_site_is_named_and_given_a_local_id_after_its_dataset(self, graph):
        for site in HeatFlowSite.objects.all():
            assert site.name.startswith(f"DEMO-{graph.pk}-")
            assert site.local_id == site.name


@pytest.fixture
def varied(dataset, unpublished_dataset):
    """A dataset's graph after ``vary_page_states``, beside the unpublished dataset."""
    counter = iter(range(500, 10_000))
    DemoGraph(dataset, random.Random(8), lambda: next(counter)).build(sites=8)
    DemoGraph(dataset, random.Random(8)).vary_page_states(unpublished_dataset)
    return dataset


class TestVaryPageStates:
    def test_a_site_has_no_parent(self, varied):
        sites = HeatFlowSite.objects.filter(dataset=varied)

        assert sites.exclude(pk__in=ParentHeatFlow.objects.values("sample")).exists()

    def test_a_parent_has_no_children(self, varied):
        parents = ParentHeatFlow.objects.filter(dataset=varied)

        assert parents.filter(children__isnull=True).exists()

    def test_a_parent_has_children_and_none_is_relevant(self, varied):
        for parent in ParentHeatFlow.objects.filter(dataset=varied):
            children = parent.children.all()
            if children and not children.filter(is_relevant=True).exists():
                return
        pytest.fail("no parent has children and none relevant")

    def test_a_child_has_no_gradient_conductivity_corrections_or_parent(self, varied):
        bare = HeatFlow.objects.filter(
            dataset=varied,
            thermal_gradient=None,
            thermal_conductivity=None,
            parent=None,
            corrections__isnull=True,
        )

        assert bare.exists()

    def test_a_score_is_stored_under_another_scheme_revision(self, varied):
        stale = HeatFlow.objects.filter(dataset=varied).exclude(
            quality_scheme__in=["", SCHEME_REVISION]
        )

        assert stale.exists()

    def test_a_child_has_not_been_scored(self, varied):
        unscored = HeatFlow.objects.filter(dataset=varied, quality_scheme="")

        assert unscored.filter(quality=None).exists()

    def test_a_site_has_no_location(self, varied):
        assert HeatFlowSite.objects.filter(dataset=varied, location=None).exists()

    def test_a_site_has_more_intervals_than_its_page_lists(self, varied):
        counts = [
            site.intervals.count()
            for site in HeatFlowSite.objects.filter(dataset=varied)
        ]

        assert max(counts) > HeatFlowPage.intervals_shown

    def test_records_of_an_unpublished_dataset_sit_beside_published_ones(
        self, varied, unpublished_dataset
    ):
        site_intervals = HeatFlowInterval.objects.filter(
            site__dataset=varied, dataset=unpublished_dataset
        )
        children = HeatFlow.objects.filter(
            sample__in=HeatFlowInterval.objects.filter(site__dataset=varied),
            dataset=unpublished_dataset,
        )
        parents = ParentHeatFlow.objects.filter(
            sample__in=HeatFlowSite.objects.filter(dataset=varied),
            dataset=unpublished_dataset,
        )
        gradients = HeatFlow.objects.filter(
            dataset=varied, thermal_gradient__dataset=unpublished_dataset
        )

        assert site_intervals.exists()
        assert children.exists()
        assert parents.exists()
        assert gradients.exists()

    def test_a_site_lists_a_published_child_beside_an_unpublished_one(
        self, varied, unpublished_dataset
    ):
        for site in HeatFlowSite.objects.filter(dataset=varied):
            children = HeatFlow.objects.filter(sample__in=site.intervals.all())
            if (
                children.filter(dataset=varied).exists()
                and children.filter(dataset=unpublished_dataset).exists()
            ):
                return
        pytest.fail("no site has a published and an unpublished child")

    def test_a_record_moved_to_an_unpublished_dataset_carries_no_published_id(
        self, varied, unpublished_dataset
    ):
        for model in (ParentHeatFlow, HeatFlow):
            assert not model.objects.filter(
                dataset=unpublished_dataset, ghfdb_id__isnull=False
            ).exists()

    def test_records_left_in_the_dataset_keep_their_published_id(self, varied):
        for model in (ParentHeatFlow, HeatFlow):
            assert not model.objects.filter(dataset=varied, ghfdb_id=None).exists()

    def test_it_can_run_twice(self, varied, unpublished_dataset):
        DemoGraph(varied, random.Random(9)).vary_page_states(unpublished_dataset)

    def test_a_dataset_with_too_few_sites_is_refused(
        self, dataset, unpublished_dataset
    ):
        DemoGraph(dataset, random.Random(8)).build(sites=3)

        with pytest.raises(ValueError, match="six"):
            DemoGraph(dataset, random.Random(8)).vary_page_states(unpublished_dataset)
