"""Tests for review.forms.ReviewDescriptionForm (T015, spec.md User Story 2).

Publication, assessors, dates and an optional title, collected before any
file is chosen (FR-003 through FR-007).
"""

import pytest
from fairdm.factories import LiteratureItemFactory

from review.forms import ReviewDescriptionForm
from tests.test_review.factories import ClaimedPersonFactory, GhostPersonFactory


@pytest.mark.django_db
@pytest.mark.review
class TestReviewDescriptionFormValidation:
    def test_valid_with_catalogued_publication_assessors_and_dates(self):
        literature = LiteratureItemFactory()
        assessor = ClaimedPersonFactory()

        form = ReviewDescriptionForm(
            data={
                "literature": literature.pk,
                "reviewers": [assessor.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert form.is_valid(), form.errors

    def test_end_date_before_start_date_is_refused_naming_the_dates(self):
        literature = LiteratureItemFactory()
        assessor = ClaimedPersonFactory()

        form = ReviewDescriptionForm(
            data={
                "literature": literature.pk,
                "reviewers": [assessor.pk],
                "start_date": "2026-02-01",
                "end_date": "2026-01-01",
            }
        )

        assert not form.is_valid()
        errors = " ".join(form.errors.get("end_date", []))
        assert "2026-02-01" in errors
        assert "2026-01-01" in errors

    def test_a_ghost_profile_is_accepted_as_an_assessor(self):
        literature = LiteratureItemFactory()
        ghost = GhostPersonFactory()

        form = ReviewDescriptionForm(
            data={
                "literature": literature.pk,
                "reviewers": [ghost.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert form.is_valid(), form.errors
