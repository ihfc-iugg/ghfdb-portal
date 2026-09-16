"""Tests for review.models.Review (T006, data-model.md "review.Review").

Fixtures use direct ORM calls, deliberately (tests/README.md): factories fill
fields with generated values, which would hide whether ``uploaded_by`` etc.
behave the way the model declares.
"""

from pathlib import Path

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


# T010a: the tree must never hold two answers at once. Asserted by a grep-style
# test rather than by eye: no reference to ``STATUS_CHOICES``, ``review__status``
# or the old "Reviewers" group may survive anywhere in ``project/`` once the code
# the new record supersedes is retired.
#
# Migrations are excluded deliberately: a migration is a historical record of what
# the schema used to be and is never edited once written, so the mapping comment in
# ``0003_review_workflow_fields.py`` is expected to name the old ``STATUS_CHOICES``
# values it translates away from.

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "project"

FORBIDDEN_IN_PYTHON = [
    "STATUS_CHOICES",
    "review__status",
    'groups__name="Reviewers"',
    "groups__name='Reviewers'",
    'groups__name="reviewers"',
    "groups__name='reviewers'",
    'group_required = ["Reviewers"]',
]


def _python_files():
    for path in PROJECT_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or "migrations" in path.parts:
            continue
        yield path


def _html_files():
    for path in PROJECT_ROOT.rglob("*.html"):
        yield path


class TestOldRecordVocabularyIsRetired:
    def test_no_forbidden_python_reference_remains(self):
        matches = [
            f"{path}: {pattern!r}"
            for path in _python_files()
            for pattern in FORBIDDEN_IN_PYTHON
            if pattern in path.read_text()
        ]
        assert not matches, matches

    def test_no_template_reads_the_retired_status_attribute(self):
        matches = [
            str(path) for path in _html_files() if "review.status" in path.read_text()
        ]
        assert not matches, matches
