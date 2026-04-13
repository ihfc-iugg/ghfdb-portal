"""Tests for GHFDB views."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_explore_page_is_public_and_returns_200(client):
    """Anonymous users can access the explore page without login redirect."""
    response = client.get(reverse("ghfdb-explore"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_explore_page_contains_iframe_with_expected_src(client):
    """Rendered explore page contains the IHFC map iframe URL."""
    response = client.get(reverse("ghfdb-explore"))
    content = response.content.decode("utf-8")
    assert "<iframe" in content
    assert 'src="https://ihfc-iugg.github.io/HeatFlowMapping/"' in content


@pytest.mark.django_db
def test_explore_page_contains_visible_fallback_markup(client):
    """Template includes a fallback element used when iframe loading fails."""
    response = client.get(reverse("ghfdb-explore"))
    content = response.content.decode("utf-8")
    assert 'id="map-error"' in content
    assert "explore-fallback" in content
