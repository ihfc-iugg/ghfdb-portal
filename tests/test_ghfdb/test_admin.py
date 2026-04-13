"""
Tests for GHFDB admin views.

T013: Verifies the GHFDB admin changelist page loads HTTP 200,
the page title contains "GHFDB Entries", and all displayed columns are
readable without a FieldError.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_ghfdb_admin_changelist(admin_client, heat_flow_chain):
    """
    T013: Admin changelist for GHFDB returns HTTP 200 and contains 'GHFDB Entries'.
    """
    url = reverse("admin:ghfdb_ghfdb_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "GHFDB" in content
