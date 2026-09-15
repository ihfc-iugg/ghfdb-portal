"""Tests for review.factories (T002).

Every test needing an assessment, a claimed person, a ghost person or a
publication gets one from a factory here — reusing the framework's own
factories (``DatasetFactory``, ``LiteratureItemFactory``, ``PersonFactory``)
rather than redefining them.
"""

import pytest
from fairdm.factories import LiteratureItemFactory


@pytest.mark.django_db
@pytest.mark.review
class TestReviewFactories:
    def test_review_factory_produces_a_saved_instance(self):
        from tests.test_review.factories import ReviewFactory

        review = ReviewFactory()

        assert review.pk is not None
        assert review.literature_id is not None
        assert review.dataset_id is not None

    def test_claimed_person_factory_produces_a_claimed_person(self):
        from tests.test_review.factories import ClaimedPersonFactory

        person = ClaimedPersonFactory()

        assert person.pk is not None
        assert person.is_claimed is True
        assert person.has_usable_password()

    def test_ghost_person_factory_produces_an_unclaimed_person_with_no_email(self):
        from tests.test_review.factories import GhostPersonFactory

        person = GhostPersonFactory()

        assert person.pk is not None
        assert person.is_claimed is False
        assert person.email is None

    def test_literature_item_factory_is_reused_from_the_framework(self):
        """A publication is supplied by the framework's own factory, not a
        review-specific redefinition of it."""
        item = LiteratureItemFactory()

        assert item.pk is not None
