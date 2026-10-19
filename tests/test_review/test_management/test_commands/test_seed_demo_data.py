# Tests for ``project/review/management/commands/seed_demo_data.py``. The command runs at
# the smallest size.

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from fairdm.core.dataset.models import Dataset, DatasetLiteratureRelation
from fairdm.factories import DatasetFactory
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
from heat_flow.demo import CHILDREN_CYCLE, SITES_PER_DATASET
from heat_flow.quality import SCHEME_REVISION
from literature.models import LiteratureItem
from research_vocabs.models import Concept
from review.management.commands import seed_demo_data
from review.models import Review

HEAT_FLOW_MODELS = (
    HeatFlowSite,
    HeatFlowInterval,
    ParentHeatFlow,
    HeatFlow,
    ThermalGradient,
    IntervalConductivity,
    HeatFlowCorrection,
    ProbeMetadata,
)

SMALLEST_SIZE = 4

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


def seed(*options):
    call_command(
        "seed_demo_data",
        *(options or ("--size", str(SMALLEST_SIZE))),
        stdout=StringIO(),
    )


def demo_datasets():
    return Dataset.all_objects.filter(options__demo_data=True)


def stored_scores():
    """Every stored score, keyed by model and pk."""
    return {
        (model.__name__, pk, *row)
        for model, fields in (
            (ThermalGradient, ("score", "score_missing", "quality_scheme")),
            (IntervalConductivity, ("score", "score_missing", "quality_scheme")),
            (
                HeatFlow,
                (
                    "U_score",
                    "T_score",
                    "T_score_missing",
                    "TC_score",
                    "TC_score_missing",
                    "M_score",
                    "quality",
                    "quality_scheme",
                ),
            ),
            (ParentHeatFlow, ("U_score", "M_score", "quality", "quality_scheme")),
        )
        for pk, *row in model.objects.values_list("pk", *fields)
    }


@pytest.fixture
def seeded(db):
    seed()


class TestSeedDemoData:
    def test_an_empty_database_gains_rows_in_every_heat_flow_model(self, seeded):
        for model in HEAT_FLOW_MODELS:
            assert model.objects.exists()

    def test_every_dataset_is_marked_as_demo_data(self, seeded):
        assert demo_datasets().count() == SMALLEST_SIZE
        assert Dataset.all_objects.count() == SMALLEST_SIZE

    def test_every_record_carries_the_current_scheme_revision(self, seeded):
        for model in (ThermalGradient, IntervalConductivity, HeatFlow, ParentHeatFlow):
            assert not model.objects.exclude(quality_scheme=SCHEME_REVISION).exists()

    def test_scores_are_computed_for_every_child(self, seeded):
        assert not HeatFlow.objects.filter(T_score__isnull=True).exists()
        assert not HeatFlow.objects.filter(TC_score__isnull=True).exists()

    def test_scores_equal_a_fresh_recalculation(self, seeded):
        before = stored_scores()

        call_command("refresh_quality", "--all", stdout=StringIO())

        assert stored_scores() == before

    def test_the_command_loads_the_vocabularies_when_none_are_present(self, db):
        Concept.objects.all().delete()

        seed()

        for model, field in CONCEPT_FIELDS:
            for record in model.objects.all():
                assert getattr(record, field).exists()

    def test_each_dataset_has_its_literature_and_contributors(self, seeded):
        for dataset in demo_datasets():
            literature = dataset.reference

            assert literature.citation_key.startswith("demo-")
            assert "10.5072/" in literature.get_doi()
            assert DatasetLiteratureRelation.objects.filter(
                dataset=dataset,
                literature_item=literature,
                relationship_type="IsCitedBy",
            ).exists()
            assert dataset.contributors.exists()

    def test_each_dataset_has_an_assessment_of_its_own_literature(self, seeded):
        for dataset in demo_datasets():
            assert dataset.review.literature_id == dataset.reference_id

    def test_literature_count_matches_the_datasets(self, seeded):
        assert LiteratureItem.objects.count() == SMALLEST_SIZE
        assert Review.objects.count() == SMALLEST_SIZE

    def test_a_private_dataset_that_existed_before_is_unchanged(self, db):
        existing = DatasetFactory(visibility=Dataset.VISIBILITY_CHOICES.PRIVATE)
        before = Dataset.all_objects.values().get(pk=existing.pk)

        seed()

        assert Dataset.all_objects.values().get(pk=existing.pk) == before
        assert not existing.samples.exists()


class TestSeedDemoDataEnvironment:
    def test_production_is_refused_and_nothing_is_written(self, db, settings):
        settings.DJANGO_ENV = "production"
        counts = {
            model: model.objects.count()
            for model in (*HEAT_FLOW_MODELS, Dataset, LiteratureItem, Review, Concept)
        }

        with pytest.raises(CommandError):
            seed()

        assert counts == {model: model.objects.count() for model in counts}


def totals():
    return (
        demo_datasets().count(),
        HeatFlowSite.objects.count(),
        HeatFlow.objects.count(),
    )


class TestSeedDemoDataSize:
    def test_the_smallest_size_gives_four_datasets_of_twenty_sites_and_fifty_children(
        self, db
    ):
        seed("--size", "4")

        assert totals() == (4, 80, 200)

    def test_double_the_size_doubles_every_count(self, db):
        seed("--size", "8")

        assert totals() == (8, 160, 400)

    @pytest.mark.parametrize("size", ["0", "-1", "3", "201"])
    def test_a_size_outside_the_range_is_refused_and_nothing_is_written(self, db, size):
        counts = {
            model: model.objects.count()
            for model in (Dataset, LiteratureItem, Review, Concept, HeatFlowSite)
        }

        with pytest.raises(CommandError) as refusal:
            seed("--size", size)

        assert str(seed_demo_data.MIN_SIZE) in str(refusal.value)
        assert str(seed_demo_data.MAX_SIZE) in str(refusal.value)
        assert counts == {model: model.objects.count() for model in counts}

    def test_a_second_run_adds_beside_the_first(self, db):
        seed("--size", "4")
        first = {
            dataset.pk: Dataset.all_objects.values().get(pk=dataset.pk)
            for dataset in demo_datasets()
        }

        seed("--size", "4")

        assert totals() == (8, 160, 400)
        for pk, row in first.items():
            assert Dataset.all_objects.values().get(pk=pk) == row

    def test_coordinates_stay_distinct_across_runs(self, db):
        seed("--size", "4")
        seed("--size", "4")

        points = [
            (site.location.x, site.location.y) for site in HeatFlowSite.objects.all()
        ]
        assert len(set(points)) == len(points) == 160

    def test_published_identifiers_stay_unique_across_runs(self, db):
        seed("--size", "4")
        seed("--size", "4")

        parents = list(
            ParentHeatFlow.objects.exclude(ghfdb_id=None).values_list(
                "ghfdb_id", flat=True
            )
        )
        children = list(
            HeatFlow.objects.exclude(ghfdb_id=None).values_list("ghfdb_id", flat=True)
        )
        assert parents and children
        assert len(set(parents)) == len(parents)
        assert len(set(children)) == len(children)

    def test_the_largest_size_gives_at_least_ten_thousand_children(self):
        children_per_dataset = (
            SITES_PER_DATASET * sum(CHILDREN_CYCLE) / len(CHILDREN_CYCLE)
        )

        assert seed_demo_data.MAX_SIZE * children_per_dataset >= 10_000
