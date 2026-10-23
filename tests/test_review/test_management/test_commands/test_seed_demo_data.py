# Tests for ``project/review/management/commands/seed_demo_data.py``. The command runs at
# the smallest size.

from io import StringIO

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from fairdm.core.dataset.models import Dataset, DatasetLiteratureRelation
from fairdm.core.project.models import Project
from fairdm.factories import DatasetFactory
from fairdm.management.commands.create_dev_accounts import DEV_ACCOUNTS
from heat_flow.demo import CHILDREN_CYCLE, SITES_PER_DATASET
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
from heat_flow.quality import SCHEME_REVISION
from literature.models import LiteratureItem
from research_vocabs.models import Concept
from review.management.commands import seed_demo_data
from review.models import Review
from review.permissions import is_data_curator
from review.states import States

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


@pytest.fixture(autouse=True)
def role_groups(data_assessor_group, data_curator_group):
    """The groups the migration and ``PortalRoles.reconcile()`` create outside the tests."""


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
    def test_production_is_refused_and_nothing_is_written(
        self, db, settings, monkeypatch
    ):
        settings.DJANGO_ENV = "production"
        counts = {
            model: model.objects.count()
            for model in (*HEAT_FLOW_MODELS, Dataset, LiteratureItem, Review, Concept)
        }
        called = []
        monkeypatch.setattr(
            seed_demo_data, "call_command", lambda *args, **kwargs: called.append(args)
        )

        with pytest.raises(CommandError, match="Refusing to add demo data"):
            seed()

        assert called == []
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


DEMO_ASSESSOR = "data-assessor.user@example.com"
DEMO_CURATOR = "data-curator.user@example.com"
EXAMPLE_ADDRESSES = (
    "regular.user@example.com",
    "staff.user@example.com",
    "super.user@example.com",
    DEMO_ASSESSOR,
    DEMO_CURATOR,
)
FAIRDM_ADDRESSES = tuple(account["email"] for account in DEV_ACCOUNTS)
PASSWORD = "password"


def decided_by(state):
    return {
        review.decided_by.email if review.decided_by else None
        for review in Review.objects.filter(state=state)
    }


class TestSeedDemoDataStates:
    def test_the_smallest_run_holds_one_assessment_in_each_state(self, seeded):
        states = sorted(Review.objects.values_list("state", flat=True))

        assert states == sorted(States.values)

    def test_complete_datasets_are_public_and_published_and_the_rest_private(
        self, seeded
    ):
        for review in Review.objects.select_related("dataset"):
            complete = review.state == States.COMPLETE
            dataset = Dataset.all_objects.get(pk=review.dataset_id)

            assert (dataset.visibility == Dataset.VISIBILITY_CHOICES.PUBLIC) is complete
            assert dataset.published is complete

    def test_records_of_unpublished_datasets_carry_no_ghfdb_id(self, seeded):
        for review in Review.objects.all():
            complete = review.state == States.COMPLETE
            for model in (ParentHeatFlow, HeatFlow):
                records = model.objects.filter(dataset=review.dataset_id)

                assert records.exists()
                assert not records.filter(ghfdb_id__isnull=complete).exists()

    def test_the_curator_decides_changes_requested_and_complete_assessments(
        self, seeded
    ):
        assert decided_by(States.CHANGES_REQUESTED) == {DEMO_CURATOR}
        assert decided_by(States.COMPLETE) == {DEMO_CURATOR}
        assert decided_by(States.DESCRIBED) == {None}
        assert decided_by(States.AWAITING_DECISION) == {None}

    def test_every_assessment_is_uploaded_by_the_assessor_who_is_also_its_reviewer(
        self, seeded
    ):
        for review in Review.objects.all():
            assert review.uploaded_by.email == DEMO_ASSESSOR
            assert [person.email for person in review.reviewers.all()] == [
                DEMO_ASSESSOR
            ]

    def test_the_assessor_is_credited_on_every_dataset(self, seeded):
        for dataset in demo_datasets():
            assert dataset.contributors.filter(
                contributor__person__email=DEMO_ASSESSOR
            ).exists()


class TestSeedDemoDataAccounts:
    def test_every_development_account_exists_with_a_confirmed_address(
        self, seeded, data_assessor_group, data_curator_group
    ):
        for email in (*FAIRDM_ADDRESSES, *EXAMPLE_ADDRESSES):
            assert EmailAddress.objects.filter(email=email, verified=True).exists()
            assert get_user_model().objects.filter(email=email).exists()

    @pytest.mark.parametrize("email", [*FAIRDM_ADDRESSES, *EXAMPLE_ADDRESSES])
    def test_each_account_can_log_in(self, seeded, client, email):
        assert client.login(username=email, password=PASSWORD)

    def test_the_assessor_and_the_curator_hold_their_groups(
        self, seeded, data_assessor_group, data_curator_group
    ):
        Person = get_user_model()

        assert (
            data_assessor_group in Person.objects.get(email=DEMO_ASSESSOR).groups.all()
        )
        assert data_curator_group in Person.objects.get(email=DEMO_CURATOR).groups.all()

    def test_the_staff_and_super_accounts_have_their_flags(self, seeded):
        Person = get_user_model()

        assert Person.objects.get(email="staff.user@example.com").is_staff
        assert Person.objects.get(email="super.user@example.com").is_superuser

    def test_a_rerun_creates_no_second_account(self, seeded):
        addresses = (*FAIRDM_ADDRESSES, *EXAMPLE_ADDRESSES)
        before = get_user_model().objects.filter(email__in=addresses).count()

        seed()

        assert (
            get_user_model().objects.filter(email__in=addresses).count()
            == before
            == len(set(addresses))
        )

    def test_the_curator_sees_an_assessment_waiting_for_a_decision(self, seeded):
        curator = get_user_model().objects.get(email=DEMO_CURATOR)

        assert is_data_curator(curator)
        assert Review.objects.filter(state=States.AWAITING_DECISION).exists()


class TestSeedDemoDataVisibility:
    def public(self):
        return Dataset.all_objects.filter(
            options__demo_data=True, visibility=Dataset.VISIBILITY_CHOICES.PUBLIC
        )

    def private(self):
        return Dataset.all_objects.filter(
            options__demo_data=True, visibility=Dataset.VISIBILITY_CHOICES.PRIVATE
        )

    @pytest.mark.parametrize("route", ["/datasets/", "/api/v1/datasets/"])
    def test_an_anonymous_request_lists_only_the_public_demo_datasets(
        self, seeded, client, route
    ):
        content = client.get(route).content.decode()

        assert self.public().exists()
        assert self.private().exists()
        for dataset in self.public():
            assert dataset.uuid in content
        for dataset in self.private():
            assert dataset.uuid not in content

    def test_the_demo_assessor_opens_its_private_demo_datasets_and_a_visitor_cannot(
        self, seeded, client
    ):
        # The list page leaves private datasets out for everyone, because it reads the
        # default manager, so a contributor reaches a private dataset through its own page.
        private = list(self.private())
        anonymous = [client.get(f"/datasets/{d.uuid}/").status_code for d in private]
        client.login(username=DEMO_ASSESSOR, password=PASSWORD)

        signed_in = [client.get(f"/datasets/{d.uuid}/").status_code for d in private]

        assert private
        assert set(signed_in) == {200}
        assert 200 not in anonymous


def demo_projects():
    return Project.objects.filter(options__demo_data=True)


class TestSeedDemoDataProjects:
    def test_a_run_creates_projects_marked_as_demo_data(self, seeded):
        assert demo_projects().exists()

    def test_some_datasets_belong_to_a_project_and_some_to_none(self, seeded):
        assert demo_datasets().filter(project__isnull=False).exists()
        assert demo_datasets().filter(project__isnull=True).exists()

    def test_every_demo_project_holds_demo_datasets(self, seeded):
        for project in demo_projects():
            assert demo_datasets().filter(project=project).exists()

    def test_every_demo_project_is_public_owned_and_credited(self, seeded):
        for project in demo_projects():
            assert project.visibility == Project.VISIBILITY.PUBLIC
            assert project.owner is not None
            assert project.contributors.exists()

    def test_a_second_run_adds_projects_beside_the_first(self, db):
        seed()
        first = set(demo_projects().values_list("pk", flat=True))
        seed()

        assert first < set(demo_projects().values_list("pk", flat=True))

    def test_an_anonymous_request_lists_the_demo_projects(self, seeded, client):
        content = client.get("/projects/").content.decode()

        for project in demo_projects():
            assert project.uuid in content


@pytest.fixture
def seeded_with_page_states(db):
    seed("--size", str(SMALLEST_SIZE), "--page-states")


class TestSeedDemoDataPageStates:
    def varied_dataset(self):
        """The one published dataset with a site that has no location."""
        return Dataset.all_objects.get(
            pk__in=HeatFlowSite.objects.filter(location=None).values("dataset")
        )

    def test_a_run_varies_one_published_dataset(self, seeded_with_page_states):
        dataset = self.varied_dataset()

        assert dataset.published is True
        assert dataset.visibility == Dataset.VISIBILITY_CHOICES.PUBLIC

    def test_that_dataset_holds_every_state_a_record_page_answers_for(
        self, seeded_with_page_states
    ):
        dataset = self.varied_dataset()
        sites = HeatFlowSite.objects.filter(dataset=dataset)
        parents = ParentHeatFlow.objects.filter(sample__in=sites, dataset=dataset)

        assert sites.exclude(pk__in=ParentHeatFlow.objects.values("sample")).exists()
        assert parents.filter(children__isnull=True).exists()
        assert HeatFlow.objects.filter(
            dataset=dataset, thermal_gradient=None, parent=None
        ).exists()
        assert HeatFlow.objects.filter(dataset=dataset, quality_scheme="").exists()
        assert (
            HeatFlow.objects.filter(dataset=dataset)
            .exclude(quality_scheme__in=["", SCHEME_REVISION])
            .exists()
        )
        assert max(site.intervals.count() for site in sites) > (
            HeatFlowPage.intervals_shown
        )

    def test_the_first_dataset_holds_the_records_it_hides_beside_published_ones(
        self, seeded_with_page_states
    ):
        dataset = self.varied_dataset()
        hidden = Dataset.all_objects.get(review__state=States.DESCRIBED)

        moved = HeatFlowInterval.objects.filter(site__dataset=dataset, dataset=hidden)

        assert moved.exists()
        assert hidden.published is False

    def test_a_second_run_varies_another_dataset_and_fails_on_nothing(self, db):
        seed("--size", str(SMALLEST_SIZE), "--page-states")
        seed("--size", str(SMALLEST_SIZE), "--page-states")

        varied = Dataset.all_objects.filter(
            pk__in=HeatFlowSite.objects.filter(location=None).values("dataset")
        )

        assert varied.count() == 2

    def test_a_run_without_the_option_varies_nothing(self, seeded):
        assert not HeatFlowSite.objects.filter(location=None).exists()
