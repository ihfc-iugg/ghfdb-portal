"""Registration tests for the GHFDB published-structure routes (FS-006 US1, US2)."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestGHFDBAPIRegistration:
    def test_the_api_index_lists_the_parent_endpoint(self, client):
        response = client.get(reverse("api:api-root"))

        assert response.status_code == 200
        assert "ghfdb/parents" in response.json()

    def test_the_schema_describes_both_parent_routes(self, client):
        response = client.get(reverse("api:api-schema"), {"format": "json"})

        assert response.status_code == 200
        paths = response.json()["paths"]
        assert "/api/v1/ghfdb/parents/" in paths
        assert "/api/v1/ghfdb/parents/{ghfdb_id}/" in paths

    def test_the_api_index_lists_the_children_endpoint(self, client):
        response = client.get(reverse("api:api-root"))

        assert response.status_code == 200
        assert "ghfdb/children" in response.json()

    def test_the_schema_describes_both_determination_shapes(self, client):
        response = client.get(reverse("api:api-schema"), {"format": "json"})

        assert response.status_code == 200
        schema = response.json()
        paths = schema["paths"]
        assert "/api/v1/ghfdb/children/" in paths
        assert "/api/v1/ghfdb/children/{ghfdb_id}/" in paths

        list_schema_ref = paths["/api/v1/ghfdb/children/"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]["$ref"]
        detail_schema_ref = paths["/api/v1/ghfdb/children/{ghfdb_id}/"]["get"][
            "responses"
        ]["200"]["content"]["application/json"]["schema"]["$ref"]

        assert list_schema_ref != detail_schema_ref
