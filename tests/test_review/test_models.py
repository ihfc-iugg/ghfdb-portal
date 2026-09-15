"""Tests for review.models.Review (T006, data-model.md "review.Review").

Fixtures use direct ORM calls, deliberately (tests/README.md): factories fill
fields with generated values, which would hide whether ``uploaded_by`` etc.
behave the way the model declares.
"""

import pytest
from django.core.exceptions import FieldDoesNotExist
from fairdm.factories import DatasetFactory, LiteratureItemFactory

from review.models import Review
from review.states import States
from tests.test_review.factories import ClaimedPersonFactory


@pytest.fixture
def literature(db):
    return LiteratureItemFactory()


@pytest.fixture
def dataset(db):
    return DatasetFactory()


@pytest.mark.django_db
@pytest.mark.review
class TestReviewWorkflowFields:
    def test_status_field_no_longer_exists(self):
        with pytest.raises(FieldDoesNotExist):
            Review._meta.get_field("status")

    def test_new_review_defaults_to_described_state(self, literature, dataset):
        review = Review.objects.create(literature=literature, dataset=dataset)

        assert review.state == States.DESCRIBED

    def test_uploaded_by_can_be_set_at_creation(self, literature, dataset):
        uploader = ClaimedPersonFactory()

        review = Review.objects.create(
            literature=literature, dataset=dataset, uploaded_by=uploader
        )

        assert review.uploaded_by_id == uploader.pk

    def test_decision_fields_accept_a_curators_decision(self, literature, dataset):
        from django.utils import timezone

        curator = ClaimedPersonFactory()
        now = timezone.now()

        review = Review.objects.create(
            literature=literature,
            dataset=dataset,
            state=States.COMPLETE,
            decided_by=curator,
            decided_at=now,
            decision_comment="Looks good.",
        )

        review.refresh_from_db()
        assert review.decided_by_id == curator.pk
        assert review.decided_at == now
        assert review.decision_comment == "Looks good."

    @pytest.mark.parametrize(
        "field_name",
        ["uploaded_by", "state", "decided_by", "decided_at", "decision_comment"],
    )
    def test_every_new_field_has_a_verbose_name_and_help_text(self, field_name):
        field = Review._meta.get_field(field_name)

        assert str(field.verbose_name).strip()
        assert str(field.help_text).strip()


@pytest.mark.django_db
@pytest.mark.review
class TestSubmittedFile:
    """T007, data-model.md "review.SubmittedFile" — a file per submission,
    not a field on the assessment, because a curator can send an assessment
    back and the replacement must not erase what was rejected."""

    def test_current_returns_the_most_recent_submission(
        self, literature, dataset, tmp_path, settings
    ):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from review.models import SubmittedFile

        settings.MEDIA_ROOT = str(tmp_path)
        review = Review.objects.create(literature=literature, dataset=dataset)
        uploader = ClaimedPersonFactory()

        first = SubmittedFile.objects.create(
            review=review,
            file=SimpleUploadedFile("first.xlsx", b"first"),
            submitted_by=uploader,
        )
        second = SubmittedFile.objects.create(
            review=review,
            file=SimpleUploadedFile("second.xlsx", b"second"),
            submitted_by=uploader,
        )

        assert review.current.pk == second.pk

    def test_every_earlier_submission_remains_retrievable(
        self, literature, dataset, tmp_path, settings
    ):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from review.models import SubmittedFile

        settings.MEDIA_ROOT = str(tmp_path)
        review = Review.objects.create(literature=literature, dataset=dataset)
        uploader = ClaimedPersonFactory()

        first = SubmittedFile.objects.create(
            review=review,
            file=SimpleUploadedFile("first.xlsx", b"first"),
            submitted_by=uploader,
        )
        second = SubmittedFile.objects.create(
            review=review,
            file=SimpleUploadedFile("second.xlsx", b"second"),
            submitted_by=uploader,
        )

        assert set(review.submissions.values_list("pk", flat=True)) == {
            first.pk,
            second.pk,
        }

    @pytest.mark.parametrize("field_name", ["file", "submitted_by", "submitted_at", "imported_at"])
    def test_every_field_has_a_verbose_name_and_help_text(self, field_name):
        from review.models import SubmittedFile

        field = SubmittedFile._meta.get_field(field_name)

        assert str(field.verbose_name).strip()
        assert str(field.help_text).strip()
