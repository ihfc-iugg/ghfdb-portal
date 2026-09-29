"""HTTP-level tests for the GHFDB published-structure viewsets (FS-006 US1, US2)."""

import pytest
from django.urls import reverse

from project.ghfdb.constants import CHILD_COLUMNS, PARENT_COLUMNS, REJECTED_MISSPELLED_COLUMNS
from project.ghfdb.models import GHFDBChild, GHFDBParent

from .conftest import build_child, build_published_chain, build_site_and_parent


@pytest.mark.django_db
class TestGHFDBParentViewSet:
    def test_list_returns_published_parent_columns_in_published_order(
        self, client, public_dataset
    ):
        build_published_chain(public_dataset)

        response = client.get(reverse("api:ghfdb-parents-list"))

        assert response.status_code == 200
        record = response.json()["results"][0]
        assert list(record) == [
            "url",
            "total_children",
            "relevant_children",
            *PARENT_COLUMNS,
        ]

    def test_query_count_is_constant_between_a_page_of_one_and_a_full_page(
        self, client, public_dataset, constant_query_count
    ):
        counter = iter(range(1, 1000))

        def build(count):
            for _ in range(count):
                build_site_and_parent(public_dataset, ghfdb_id=next(counter))

        def call():
            client.get(reverse("api:ghfdb-parents-list"), {"page_size": 100})

        constant_query_count(build, call, low=1, high=99)

    def test_counts_the_total_and_relevant_children(self, client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, is_relevant=True, ghfdb_id=11)
        build_child(public_dataset, parent, is_relevant=False, ghfdb_id=12)

        response = client.get(reverse("api:ghfdb-parents-list"))

        record = response.json()["results"][0]
        assert record["total_children"] == 2
        assert record["relevant_children"] == 1

    def test_a_parent_with_no_children_carries_zero_counts(
        self, client, public_dataset
    ):
        build_site_and_parent(public_dataset, ghfdb_id=1)

        response = client.get(reverse("api:ghfdb-parents-list"))

        record = response.json()["results"][0]
        assert record["total_children"] == 0
        assert record["relevant_children"] == 0

    def test_following_the_self_link_returns_the_same_parent(
        self, client, public_dataset
    ):
        build_published_chain(public_dataset)

        list_response = client.get(reverse("api:ghfdb-parents-list"))
        record = list_response.json()["results"][0]

        detail_response = client.get(record["url"])

        assert detail_response.status_code == 200
        assert detail_response.json() == record

    def test_an_unpublished_parent_is_absent_from_the_list_and_its_route_404s(
        self, client, public_dataset
    ):
        build_site_and_parent(public_dataset, published=False)

        list_response = client.get(reverse("api:ghfdb-parents-list"))
        assert list_response.json()["results"] == []

        detail_response = client.get(
            reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 999999})
        )
        assert detail_response.status_code == 404

    def test_a_published_parent_in_a_private_dataset_is_hidden_anonymously(
        self, client, dataset
    ):
        build_site_and_parent(dataset, ghfdb_id=42)

        list_response = client.get(reverse("api:ghfdb-parents-list"))
        assert list_response.json()["results"] == []

        detail_response = client.get(
            reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 42})
        )
        assert detail_response.status_code == 404

    def test_an_anonymous_request_is_served_not_refused(self, client, public_dataset):
        build_published_chain(public_dataset)

        response = client.get(reverse("api:ghfdb-parents-list"))

        assert response.status_code == 200

    def test_a_signed_in_request_succeeds(self, staff_client, public_dataset):
        build_published_chain(public_dataset)

        response = staff_client.get(reverse("api:ghfdb-parents-list"))

        assert response.status_code == 200

    def test_a_page_past_the_end_is_404(self, client, public_dataset):
        build_site_and_parent(public_dataset, ghfdb_id=1)

        response = client.get(reverse("api:ghfdb-parents-list"), {"page": 999})

        assert response.status_code == 404

    def test_an_oversized_page_size_is_capped_at_the_framework_maximum(
        self, client, public_dataset
    ):
        for ghfdb_id in range(1, 106):
            build_site_and_parent(public_dataset, ghfdb_id=ghfdb_id)

        response = client.get(
            reverse("api:ghfdb-parents-list"), {"page_size": 1000}
        )

        assert response.status_code == 200
        assert len(response.json()["results"]) == 100

    def test_a_non_numeric_identifier_is_404(self, client):
        response = client.get("/api/v1/ghfdb/parents/abc/")

        assert response.status_code == 404

    def test_a_create_request_is_refused_and_nothing_changes(
        self, client, public_dataset
    ):
        before = GHFDBParent.objects.count()

        response = client.post(
            reverse("api:ghfdb-parents-list"), {}, content_type="application/json"
        )

        assert response.status_code >= 400
        assert GHFDBParent.objects.count() == before

    @pytest.mark.parametrize("method", ["put", "patch", "delete"])
    def test_a_modifying_request_is_refused_and_nothing_changes(
        self, client, public_dataset, method
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        url = reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})

        response = getattr(client, method)(url, {}, content_type="application/json")

        assert response.status_code >= 400
        parent.refresh_from_db()
        assert parent.value.magnitude == 70.0


@pytest.mark.django_db
class TestGHFDBChildViewSet:
    def test_list_returns_published_child_columns_in_published_order(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        assert response.status_code == 200
        record = response.json()["results"][0]
        assert list(record) == [
            "url",
            "parent",
            "lat_NS",
            "long_EW",
            *CHILD_COLUMNS,
            "ID",
        ]

    def test_a_determination_carries_no_parent_column_other_than_coordinates(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        other_parent_columns = set(PARENT_COLUMNS) - {"lat_NS", "long_EW"}
        assert not other_parent_columns & set(record)

    def test_a_determination_with_no_coordinates_still_carries_them_empty(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        assert record["lat_NS"] is None
        assert record["long_EW"] is None

    def test_a_many_valued_column_with_several_members_renders_as_a_list(
        self, client, public_dataset
    ):
        from heat_flow.vocabularies import HeatFlowMethod
        from research_vocabs.models import Concept

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        child = build_child(public_dataset, parent, ghfdb_id=11)
        methods = list(Concept.get_for_vocabulary(HeatFlowMethod)[:2])
        child.method.set(methods)

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        assert set(record["q_method"]) == {method.label for method in methods}

    def test_a_many_valued_column_with_no_members_renders_as_an_empty_list(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        assert record["q_method"] == []

    def test_a_determination_missing_gradient_conductivity_or_probe_metadata_renders_those_columns_empty(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(
            public_dataset,
            parent,
            ghfdb_id=11,
            include_gradient=False,
            include_conductivity=False,
            include_probe_metadata=False,
        )

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        assert record["T_grad_mean"] is None
        assert record["tc_mean"] is None
        assert record["probe_penetration"] is None

    def test_a_determination_missing_one_correction_type_renders_that_column_empty(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11, missing_correction="IS")

        response = client.get(reverse("api:ghfdb-children-list"))

        record = response.json()["results"][0]
        assert record["corr_IS_flag"] is None

    def test_following_the_parent_link_returns_that_determinations_parent(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        list_response = client.get(reverse("api:ghfdb-children-list"))
        record = list_response.json()["results"][0]

        parent_response = client.get(record["parent"])

        assert parent_response.status_code == 200
        assert parent_response.json()["ID_parent"] == 1

    def test_a_single_determination_nests_the_full_parent_record(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(
            reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
        )

        assert response.status_code == 200
        parent_record = response.json()["parent"]
        assert parent_record["ID_parent"] == 1
        assert "total_children" in parent_record
        assert "children" not in parent_record

    def test_query_count_is_constant_between_a_page_of_one_and_a_full_page(
        self, client, public_dataset, constant_query_count
    ):
        counter = iter(range(1, 1000))

        def build(count):
            for _ in range(count):
                next_id = next(counter)
                parent = build_site_and_parent(public_dataset, ghfdb_id=next_id)
                build_child(public_dataset, parent, ghfdb_id=next_id)

        def call():
            client.get(reverse("api:ghfdb-children-list"), {"page_size": 100})

        constant_query_count(build, call, low=1, high=99)

    def test_an_unpublished_determination_is_absent_from_the_list_and_its_route_404s(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, published=False, ghfdb_id=999999)

        list_response = client.get(reverse("api:ghfdb-children-list"))
        assert list_response.json()["results"] == []

        detail_response = client.get(
            reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 999999})
        )
        assert detail_response.status_code == 404

    def test_a_determination_in_a_private_dataset_is_hidden_anonymously(
        self, client, public_dataset, dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)

        list_response = client.get(reverse("api:ghfdb-children-list"))
        assert list_response.json()["results"] == []

        detail_response = client.get(
            reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
        )
        assert detail_response.status_code == 404

    def test_a_public_determination_whose_parent_is_in_a_private_dataset_is_hidden_anonymously(
        self, client, public_dataset, dataset
    ):
        parent = build_site_and_parent(dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        assert response.json()["results"] == []

    def test_a_determination_whose_parent_has_no_published_identifier_is_absent(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, published=False)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        assert response.json()["results"] == []

    def test_an_anonymous_request_is_served_not_refused(self, client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        assert response.status_code == 200

    def test_a_signed_in_request_succeeds(self, staff_client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = staff_client.get(reverse("api:ghfdb-children-list"))

        assert response.status_code == 200

    def test_neither_misspelled_column_appears_anywhere_in_the_response_body(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-children-list"))

        body = response.content.decode()
        for misspelled in REJECTED_MISSPELLED_COLUMNS:
            assert misspelled not in body

    def test_a_create_request_is_refused_and_nothing_changes(
        self, client, public_dataset
    ):
        before = GHFDBChild.objects.count()

        response = client.post(
            reverse("api:ghfdb-children-list"), {}, content_type="application/json"
        )

        assert response.status_code >= 400
        assert GHFDBChild.objects.count() == before

    @pytest.mark.parametrize("method", ["put", "patch", "delete"])
    def test_a_modifying_request_is_refused_and_nothing_changes(
        self, client, public_dataset, method
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        child = build_child(public_dataset, parent, ghfdb_id=11)
        url = reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})

        response = getattr(client, method)(url, {}, content_type="application/json")

        assert response.status_code >= 400
        child.refresh_from_db()
        assert child.value.magnitude == 70.0
