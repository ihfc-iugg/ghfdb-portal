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

    def test_a_concept_column_renders_as_its_stored_code_and_a_coordinate_as_a_float(
        self, client, public_dataset
    ):
        from decimal import Decimal

        from fairdm.contrib.location.models import Point
        from heat_flow.models import HeatFlowSite

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        site = HeatFlowSite.objects.get(pk=parent.sample_id)
        site.explo_method = "drilling"
        site.location = Point.objects.create(
            x=Decimal("11.56780"), y=Decimal("48.12340")
        )
        site.save()

        response = client.get(reverse("api:ghfdb-parents-list"))

        record = response.json()["results"][0]
        assert record["environment"] == "onshore_continental"
        assert record["explo_method"] == "drilling"
        assert record["lat_NS"] == 48.1234
        assert record["long_EW"] == 11.5678
        assert isinstance(record["lat_NS"], float)
        assert isinstance(record["long_EW"], float)

    def test_following_the_self_link_returns_the_same_parent(
        self, client, public_dataset
    ):
        build_published_chain(public_dataset)

        list_response = client.get(reverse("api:ghfdb-parents-list"))
        record = list_response.json()["results"][0]

        detail_response = client.get(record["url"])

        assert detail_response.status_code == 200
        detail = detail_response.json()
        del detail["children"]
        assert detail == record

    def test_following_the_self_link_returns_the_parent_with_its_determinations_attached(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)
        build_child(public_dataset, parent, ghfdb_id=12)

        list_response = client.get(reverse("api:ghfdb-parents-list"))
        record = list_response.json()["results"][0]

        detail_response = client.get(record["url"])

        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert list(detail)[:4] == ["url", "total_children", "relevant_children", "children"]
        assert {child["ID"] for child in detail["children"]} == {11, 12}

        children_response = client.get(reverse("api:ghfdb-children-list"))
        assert detail["children"] == children_response.json()["results"]

    def test_a_published_determination_in_a_private_dataset_under_a_public_parent_is_absent_from_the_anonymous_parent_detail(
        self, client, public_dataset, dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)

        response = client.get(
            reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
        )

        assert response.status_code == 200
        assert response.json()["children"] == []

    def test_the_parent_detail_query_count_does_not_grow_with_attached_determinations(
        self, client, public_dataset, constant_query_count
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        counter = iter(range(1, 1000))

        def build(count):
            for _ in range(count):
                build_child(public_dataset, parent, ghfdb_id=next(counter))

        def call():
            client.get(reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1}))

        constant_query_count(build, call, low=1, high=20)

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

    def test_a_determination_carries_its_sites_coordinates_as_floats(
        self, client, public_dataset
    ):
        from decimal import Decimal

        from fairdm.contrib.location.models import Point
        from heat_flow.models import HeatFlowSite

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)
        site = HeatFlowSite.objects.get(pk=parent.sample_id)
        site.location = Point.objects.create(
            x=Decimal("11.56780"), y=Decimal("48.12340")
        )
        site.save()

        response = client.get(
            reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
        )

        record = response.json()
        assert record["lat_NS"] == 48.1234
        assert record["long_EW"] == 11.5678
        assert isinstance(record["lat_NS"], float)
        assert isinstance(record["long_EW"], float)

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


@pytest.mark.django_db
class TestGHFDBFlatViewSet:
    def test_list_returns_every_published_column_in_published_order(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        assert response.status_code == 200
        record = response.json()["results"][0]
        assert list(record) == [*PARENT_COLUMNS, *CHILD_COLUMNS, "ID"]

    def test_a_row_carries_no_key_that_is_not_a_published_column(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        record = response.json()["results"][0]
        assert set(record) == set(PARENT_COLUMNS) | set(CHILD_COLUMNS) | {"ID"}

    def test_two_determinations_under_one_parent_repeat_its_values(
        self, client, public_dataset
    ):
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        parent.quality = "A1"
        parent.save()
        purposes = list(Concept.get_for_vocabulary(ExplorationPurpose)[:2])
        parent.sample.explo_purpose.set(purposes)
        build_child(public_dataset, parent, ghfdb_id=11)
        build_child(public_dataset, parent, ghfdb_id=12)

        response = client.get(reverse("api:ghfdb-flat-list"))

        rows = response.json()["results"]
        assert len(rows) == 2
        for row in rows:
            assert row["ID_parent"] == 1
            assert row["name"] == parent.sample.name
            assert set(row["explo_purpose"]) == {purpose.label for purpose in purposes}
            assert row["quality_parent"] == "A1"

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
            client.get(reverse("api:ghfdb-flat-list"), {"page_size": 100})

        constant_query_count(build, call, low=1, high=99)

    def test_the_concept_and_coordinate_columns_render_with_their_real_types(
        self, client, public_dataset
    ):
        from decimal import Decimal

        from fairdm.contrib.location.models import Point
        from heat_flow.models import HeatFlowSite

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)
        site = HeatFlowSite.objects.get(pk=parent.sample_id)
        site.explo_method = "drilling"
        site.location = Point.objects.create(
            x=Decimal("11.56780"), y=Decimal("48.12340")
        )
        site.save()

        response = client.get(
            reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})
        )

        record = response.json()
        assert record["environment"] == "onshore_continental"
        assert record["explo_method"] == "drilling"
        assert record["lat_NS"] == 48.1234
        assert record["long_EW"] == 11.5678
        assert isinstance(record["lat_NS"], float)
        assert isinstance(record["long_EW"], float)

    def test_the_detail_route_returns_the_same_row_the_list_carries(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        list_response = client.get(reverse("api:ghfdb-flat-list"))
        record = list_response.json()["results"][0]

        detail_response = client.get(
            reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})
        )

        assert detail_response.status_code == 200
        assert detail_response.json() == record

    def test_an_unpublished_determination_is_absent(self, client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, published=False, ghfdb_id=999999)

        response = client.get(reverse("api:ghfdb-flat-list"))

        assert response.json()["results"] == []

    def test_a_determination_in_a_private_dataset_is_absent(
        self, client, public_dataset, dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        assert response.json()["results"] == []

    def test_a_determination_whose_parent_is_not_served_is_absent(
        self, client, public_dataset, dataset
    ):
        parent = build_site_and_parent(dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        assert response.json()["results"] == []

    def test_neither_misspelled_column_appears_anywhere_in_the_response_body(
        self, client, public_dataset
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        body = response.content.decode()
        for misspelled in REJECTED_MISSPELLED_COLUMNS:
            assert misspelled not in body

    def test_an_anonymous_request_is_served_not_refused(self, client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = client.get(reverse("api:ghfdb-flat-list"))

        assert response.status_code == 200

    def test_a_signed_in_request_succeeds(self, staff_client, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)

        response = staff_client.get(reverse("api:ghfdb-flat-list"))

        assert response.status_code == 200

    def test_a_create_request_is_refused_and_nothing_changes(
        self, client, public_dataset
    ):
        before = GHFDBChild.objects.count()

        response = client.post(
            reverse("api:ghfdb-flat-list"), {}, content_type="application/json"
        )

        assert response.status_code >= 400
        assert GHFDBChild.objects.count() == before

    @pytest.mark.parametrize("method", ["put", "patch", "delete"])
    def test_a_modifying_request_is_refused_and_nothing_changes(
        self, client, public_dataset, method
    ):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        child = build_child(public_dataset, parent, ghfdb_id=11)
        url = reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})

        response = getattr(client, method)(url, {}, content_type="application/json")

        assert response.status_code >= 400
        child.refresh_from_db()
        assert child.value.magnitude == 70.0


@pytest.mark.django_db
class TestGHFDBSingleRecordObjectPermissions:
    # A single-record route decides visibility instead of crashing.
    #
    # The proxy's own `ghfdb.view_ghfdb*` permission has no row on the concrete
    # `heat_flow` model these routes serve, so checking it against the object
    # raised an unhandled error rather than answering yes or no.

    def test_a_data_curator_reads_a_private_record_on_every_single_record_route(
        self, data_curator_client, dataset
    ):
        parent = build_site_and_parent(dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)

        parent_response = data_curator_client.get(
            reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
        )
        child_response = data_curator_client.get(
            reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
        )
        flat_response = data_curator_client.get(
            reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})
        )

        assert parent_response.status_code == 200
        assert child_response.status_code == 200
        assert flat_response.status_code == 200

    def test_a_signed_in_user_with_no_grant_gets_404_on_every_single_record_route(
        self, client, dataset
    ):
        from fairdm.factories import UserFactory

        parent = build_site_and_parent(dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)
        client.force_login(UserFactory())

        assert (
            client.get(
                reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
            ).status_code
            == 404
        )
        assert (
            client.get(
                reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
            ).status_code
            == 404
        )
        assert (
            client.get(
                reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})
            ).status_code
            == 404
        )

    def test_a_guardian_object_grant_on_a_private_parent_allows_its_detail_route(
        self, client, public_dataset, dataset
    ):
        from fairdm.core.utils import assign_perm
        from fairdm.factories import UserFactory
        from heat_flow.models import HeatFlowSite, ParentHeatFlow

        # The site stays in the public dataset; only the parent (the measurement the
        # grant below targets) moves to the private one, so this scenario tests the
        # object grant alone rather than also depending on site visibility.
        site = HeatFlowSite.objects.create(
            dataset=public_dataset,
            name="Test Site",
            country="Germany",
            continent="Europe",
            environment="onshore_continental",
        )
        parent = ParentHeatFlow.objects.create(
            dataset=dataset, sample=site, name="Test Parent", value=70.0, ghfdb_id=1
        )
        user = UserFactory()
        assign_perm("view_measurement", user, ParentHeatFlow.objects.get(pk=parent.pk))
        client.force_login(user)

        response = client.get(
            reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
        )

        assert response.status_code == 200


@pytest.mark.django_db
class TestGHFDBSiteVisibility:
    # A parent is served only where its site is visible too (ADR 0021).
    #
    # A published parent's own dataset can be public while the ``HeatFlowSite``
    # it describes sits in a dataset that is not — the parent-level check alone
    # does not close that path.

    def test_a_public_parent_whose_site_is_in_a_private_dataset_is_absent_everywhere(
        self, client, public_dataset, dataset
    ):
        from heat_flow.models import HeatFlowSite

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        build_child(public_dataset, parent, ghfdb_id=11)
        site = HeatFlowSite.objects.get(pk=parent.sample_id)
        site.dataset = dataset
        site.save()

        assert client.get(reverse("api:ghfdb-parents-list")).json()["results"] == []
        assert (
            client.get(
                reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
            ).status_code
            == 404
        )
        assert client.get(reverse("api:ghfdb-children-list")).json()["results"] == []
        assert (
            client.get(
                reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
            ).status_code
            == 404
        )
        assert client.get(reverse("api:ghfdb-flat-list")).json()["results"] == []
        assert (
            client.get(
                reverse("api:ghfdb-flat-detail", kwargs={"ghfdb_id": 11})
            ).status_code
            == 404
        )


@pytest.mark.django_db
class TestGHFDBDatasetLevelGrant:
    # A view grant on a dataset alone does not surface its records.
    #
    # The list filter resolves a signed-in grant through ``get_objects_for_user``
    # against the record's own permission (or its measurement, via
    # ``fairdm.core.utils.get_objects_for_user``'s polymorphic-base
    # normalisation) — it never consults the dataset-to-measurement inheritance
    # ``MeasurementPermissionBackend.has_perm`` applies for an object-level
    # check, so a dataset-level grant alone stays invisible here.

    def test_a_view_grant_on_the_dataset_alone_does_not_surface_its_records(
        self, client, dataset
    ):
        from fairdm.core.utils import assign_perm
        from fairdm.factories import UserFactory

        user = UserFactory()
        assign_perm("view_dataset", user, dataset)
        parent = build_site_and_parent(dataset, ghfdb_id=1)
        build_child(dataset, parent, ghfdb_id=11)
        client.force_login(user)

        assert client.get(reverse("api:ghfdb-parents-list")).json()["results"] == []
        assert client.get(reverse("api:ghfdb-children-list")).json()["results"] == []
        assert client.get(reverse("api:ghfdb-flat-list")).json()["results"] == []
        assert (
            client.get(
                reverse("api:ghfdb-parents-detail", kwargs={"ghfdb_id": 1})
            ).status_code
            == 404
        )
        assert (
            client.get(
                reverse("api:ghfdb-children-detail", kwargs={"ghfdb_id": 11})
            ).status_code
            == 404
        )
