import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from project.ghfdb.visibility import served_parents

from .conftest import build_site_and_parent


def request_for(user):
    request = RequestFactory().get("/")
    request.user = user
    return request


@pytest.mark.django_db
class TestServedParents:
    def test_a_public_parent_with_a_public_site_is_served(self, public_dataset):
        parent = build_site_and_parent(public_dataset, ghfdb_id=1)

        served = served_parents(request_for(AnonymousUser()))

        assert list(served) == [parent]

    def test_a_parent_in_a_private_dataset_is_not_served(self, public_dataset, dataset):
        build_site_and_parent(public_dataset, name="Open", ghfdb_id=1)
        build_site_and_parent(dataset, name="Closed", ghfdb_id=2)

        served = served_parents(request_for(AnonymousUser()))

        assert [parent.ghfdb_id for parent in served] == [1]

    def test_a_public_parent_whose_site_is_private_is_not_served(
        self, public_dataset, dataset
    ):
        from heat_flow.models import HeatFlowSite

        parent = build_site_and_parent(public_dataset, ghfdb_id=1)
        HeatFlowSite.objects.filter(pk=parent.sample_id).update(dataset=dataset)

        served = served_parents(request_for(AnonymousUser()))

        assert list(served) == []

    def test_a_contributor_on_the_private_dataset_is_served_its_parent(
        self, public_dataset, dataset
    ):
        from fairdm.contrib.contributors.services.crediting import Crediting
        from fairdm.factories import UserFactory

        build_site_and_parent(public_dataset, name="Open", ghfdb_id=1)
        build_site_and_parent(dataset, name="Closed", ghfdb_id=2)
        user = UserFactory()
        Crediting(dataset).add(user)

        served = served_parents(request_for(user))

        assert {parent.ghfdb_id for parent in served} == {1, 2}
