import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import Point
from django.test import RequestFactory
from heat_flow import vocabularies

from project.ghfdb.filters import BoundsInput, GHFDBParentFilter

from .conftest import build_child, make_parent, parents


def bound(data, user=None):
    """The filter set for a query string given as a dict, asked for by ``user``."""
    request = RequestFactory().get("/")
    request.user = user or AnonymousUser()
    return GHFDBParentFilter(data, queryset=parents(), request=request)


def listed(data, user=None):
    """The published identifiers the filters leave, in id order."""
    return sorted(bound(data, user).qs.values_list("ghfdb_id", flat=True))


@pytest.mark.django_db
class TestBoundsFilter:
    @pytest.fixture
    def three(self, published_dataset):
        for ghfdb_id, value in ((1, -20), (2, 60), (3, 140)):
            make_parent(published_dataset, ghfdb_id, value=value)

    def test_both_bounds_list_the_parents_between_them(self, three):
        assert listed({"q_min": "-30", "q_max": "100"}) == [1, 2]

    def test_a_lower_bound_alone_leaves_the_upper_side_open(self, three):
        assert listed({"q_min": "0"}) == [2, 3]

    def test_an_upper_bound_alone_leaves_the_lower_side_open(self, three):
        assert listed({"q_max": "60"}) == [1, 2]

    def test_a_negative_bound_works(self, three):
        assert listed({"q_max": "-10"}) == [1]

    def test_text_in_a_bound_is_an_error_on_that_filter_and_narrows_nothing(
        self, three
    ):
        filterset = bound({"q_min": "abc"})

        assert [error.code for error in filterset.form.errors.as_data()["q"]] == [
            "invalid"
        ]
        assert sorted(filterset.qs.values_list("ghfdb_id", flat=True)) == [1, 2, 3]

    def test_an_upper_bound_below_the_lower_is_an_error_and_narrows_nothing(
        self, three
    ):
        filterset = bound({"q_min": "100", "q_max": "10"})

        assert [error.code for error in filterset.form.errors.as_data()["q"]] == [
            "inverted"
        ]
        assert sorted(filterset.qs.values_list("ghfdb_id", flat=True)) == [1, 2, 3]

    def test_the_widget_names_its_ends_after_the_filter(self):
        html = BoundsInput().render("q", None)

        assert 'name="q_min"' in html
        assert 'name="q_max"' in html


@pytest.mark.django_db
class TestCoordinateBounds:
    @pytest.fixture
    def sites(self, published_dataset):
        for ghfdb_id, (longitude, latitude) in {
            1: (40, 20),
            2: (20, 20),
            3: (20, 40),
        }.items():
            make_parent(
                published_dataset,
                ghfdb_id,
                site={"location": Point(longitude, latitude, srid=4326)},
            )

    def test_a_box_lists_only_the_parents_whose_site_is_inside_it(self, sites):
        box = {
            "lat_NS_min": "15",
            "lat_NS_max": "35",
            "long_EW_min": "5",
            "long_EW_max": "25",
        }

        assert listed(box) == [2]

    def test_a_latitude_of_ninety_one_is_refused_on_that_filter(self, sites):
        filterset = bound({"lat_NS_max": "91"})

        assert [error.code for error in filterset.form.errors.as_data()["lat_NS"]] == [
            "max_value"
        ]
        assert listed({"lat_NS_max": "91"}) == [1, 2, 3]

    def test_a_longitude_of_one_hundred_eighty_one_is_refused_on_that_filter(
        self, sites
    ):
        filterset = bound({"long_EW_max": "181"})

        assert [error.code for error in filterset.form.errors.as_data()["long_EW"]] == [
            "max_value"
        ]


def exploration(name):
    return vocabularies.term(vocabularies.EXPLORATION_METHOD, name)


def purpose_terms(*names):
    return [vocabularies.term(vocabularies.EXPLORATION_PURPOSE, name) for name in names]


@pytest.mark.django_db
class TestChoiceFilters:
    def test_two_environments_list_the_parents_in_either(self, published_dataset):
        for ghfdb_id, environment in (
            (1, "onshore_continental"),
            (2, "onshore_marine"),
            (3, "offshore_marine"),
        ):
            make_parent(
                published_dataset,
                ghfdb_id,
                site={
                    "environment_id": vocabularies.term(
                        vocabularies.GEOGRAPHIC_ENVIRONMENT, environment
                    )
                },
            )

        chosen = [
            vocabularies.term(vocabularies.GEOGRAPHIC_ENVIRONMENT, name)
            for name in ("onshore_continental", "onshore_marine")
        ]

        assert listed({"environment": chosen}) == [1, 2]

    def test_the_exploration_method_narrows(self, published_dataset):
        make_parent(
            published_dataset, 1, site={"explo_method_id": exploration("drilling")}
        )
        make_parent(
            published_dataset, 2, site={"explo_method_id": exploration("mining")}
        )

        assert listed({"explo_method": [exploration("mining")]}) == [2]

    def test_a_purpose_matches_a_parent_with_several_and_lists_it_once(
        self, published_dataset
    ):
        make_parent(published_dataset, 1, purpose=["hydrocarbon", "mining"])
        make_parent(published_dataset, 2, purpose=["underground_storage"])
        make_parent(published_dataset, 3)

        filterset = bound({"explo_purpose": purpose_terms("hydrocarbon", "mining")})

        assert list(filterset.qs.values_list("ghfdb_id", flat=True)) == [1]

    def test_corr_hp_flag_unknown_lists_only_the_parents_with_no_recorded_flag(
        self, published_dataset
    ):
        make_parent(published_dataset, 1, corr_HP_flag=True)
        make_parent(published_dataset, 2, corr_HP_flag=False)
        make_parent(published_dataset, 3, corr_HP_flag=None)

        assert listed({"corr_HP_flag": ["unknown"]}) == [3]
        assert listed({"corr_HP_flag": ["yes", "unknown"]}) == [1, 3]

    def test_the_quality_scores_each_narrow(self, published_dataset):
        make_parent(published_dataset, 1, U_score="U1", M_score="M1")
        make_parent(published_dataset, 2, U_score="U2", M_score="M1")
        make_parent(published_dataset, 3, U_score="U2", M_score="M2")

        assert listed({"U_score": ["U2"]}) == [2, 3]
        assert listed({"M_score": ["M1"]}) == [1, 2]
        assert listed({"U_score": ["U2"], "M_score": ["M1"]}) == [2]

    @pytest.mark.parametrize(
        ("name", "vocabulary"),
        [
            ("environment", vocabularies.GEOGRAPHIC_ENVIRONMENT),
            ("explo_method", vocabularies.EXPLORATION_METHOD),
            ("explo_purpose", vocabularies.EXPLORATION_PURPOSE),
        ],
    )
    def test_a_vocabulary_filter_offers_the_vocabularys_terms(self, name, vocabulary):
        offered = bound({}).filters[name].extra["choices"]

        assert list(offered) == vocabularies.choices(vocabulary)

    def test_choosing_two_purposes_leaves_each_rows_counts_unchanged(
        self, published_dataset
    ):
        parent = make_parent(published_dataset, 1, purpose=["hydrocarbon", "mining"])
        for ghfdb_id, is_relevant in ((41, True), (42, True), (43, False)):
            build_child(
                published_dataset, parent, ghfdb_id=ghfdb_id, is_relevant=is_relevant
            )

        both = bound({"explo_purpose": purpose_terms("hydrocarbon", "mining")}).qs.get()

        assert (both.total_children, both.relevant_children) == (3, 2)


def made_public(dataset):
    """The dataset with its project made public, so a visitor is offered both."""
    from fairdm.utils.choices import Visibility

    type(dataset.project).objects.filter(pk=dataset.project_id).update(
        visibility=Visibility.PUBLIC
    )
    return dataset


@pytest.mark.django_db
class TestRecordFilters:
    def test_a_fragment_matches_the_site_name_in_any_case(self, published_dataset):
        make_parent(published_dataset, 1, site={"name": "Alpine Borehole"})
        make_parent(published_dataset, 2, site={"name": "Coastal Well"})

        assert listed({"name": "ALPINE"}) == [1]
        assert listed({"name": "bore"}) == [1]

    def test_a_dataset_narrows_to_its_parents(self, published_dataset):
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        other = made_public(
            DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        )
        made_public(published_dataset)
        make_parent(published_dataset, 1)
        make_parent(other, 2)

        assert listed({"dataset": [published_dataset.pk]}) == [1]

    def test_a_project_narrows_to_the_parents_of_its_datasets(self, published_dataset):
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        other = made_public(
            DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        )
        made_public(published_dataset)
        make_parent(published_dataset, 1)
        make_parent(other, 2)

        assert listed({"project": [published_dataset.project.pk]}) == [1]

    def test_a_private_dataset_is_refused_for_a_visitor_and_accepted_for_a_member(
        self, published_dataset
    ):
        from fairdm.contrib.contributors.choices import ContributionLevel
        from fairdm.factories import ContributionFactory, DatasetFactory, PersonFactory

        private = DatasetFactory()
        member = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=member, content_object=private, level=ContributionLevel.VIEW
        )
        make_parent(published_dataset, 1)
        make_parent(private, 2)
        chosen = {"dataset": [private.pk]}

        refused = bound(chosen)

        assert [error.code for error in refused.form.errors.as_data()["dataset"]] == [
            "invalid_choice"
        ]
        assert listed(chosen, member) == [2]
