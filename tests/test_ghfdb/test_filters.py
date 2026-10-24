import pytest

from project.ghfdb.filters import BoundsInput, GHFDBParentFilter

from .test_tables import make_parent, parents


def bound(data):
    """The filter set for a query string given as a dict."""
    return GHFDBParentFilter(data, queryset=parents())


def listed(data):
    """The published identifiers the filters leave, in id order."""
    return sorted(bound(data).qs.values_list("ghfdb_id", flat=True))


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
