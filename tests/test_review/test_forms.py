# Tests for review.forms.ReviewDescriptionForm (FS-005 User Story 2).
# Publication, assessors, dates and an optional title, collected before any file is
# chosen (FR-003 through FR-007).

import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from fairdm.factories import LiteratureItemFactory, PersonFactory
from literature.models import LiteratureItem
from review.forms import ReviewDescriptionForm

from tests.factories import ReviewFactory


@pytest.mark.django_db
@pytest.mark.review
class TestReviewDescriptionFormValidation:
    def test_valid_with_catalogued_publication_assessors_and_dates(self):
        literature = LiteratureItemFactory()
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")

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
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")

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
        ghost = PersonFactory(email=None, is_claimed=False)

        form = ReviewDescriptionForm(
            data={
                "literature": literature.pk,
                "reviewers": [ghost.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert form.is_valid(), form.errors


@pytest.mark.django_db
@pytest.mark.review
class TestReviewDescriptionFormBibliographyFile:
    # A publication absent from the catalogue is added from a bibliography file supplied
    # through the same form (FS-005 User Story 2 scenario 2, FR-004).

    def test_a_bibliography_file_adds_the_publication_and_links_it(self):
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")
        bibliography_file = SimpleUploadedFile(
            "publication.json",
            json.dumps({"title": "A New Paper", "type": "article-journal"}).encode(),
            content_type="application/json",
        )

        form = ReviewDescriptionForm(
            data={
                "reviewers": [assessor.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            },
            files={"bibliography_file": bibliography_file},
        )

        assert form.is_valid(), form.errors
        literature = form.cleaned_data["literature"]
        assert literature.title == "A New Paper"
        assert LiteratureItem.objects.filter(pk=literature.pk).exists()

    def test_a_rejected_form_leaves_no_publication_behind(self):
        # A publication is written only once the rest of the form is sound.
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")
        bibliography_file = SimpleUploadedFile(
            "publication.json",
            json.dumps(
                {"title": "Never Asked For", "type": "article-journal"}
            ).encode(),
            content_type="application/json",
        )
        before = LiteratureItem.objects.count()

        form = ReviewDescriptionForm(
            data={
                "reviewers": [assessor.pk],
                "start_date": "2026-02-01",
                "end_date": "2026-01-01",  # the wrong way round
            },
            files={"bibliography_file": bibliography_file},
        )

        assert not form.is_valid()
        assert LiteratureItem.objects.count() == before
        assert not LiteratureItem.objects.filter(title="Never Asked For").exists()

    def test_neither_a_publication_nor_a_file_is_refused(self):
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")

        form = ReviewDescriptionForm(
            data={
                "reviewers": [assessor.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert not form.is_valid()
        assert "literature" in form.errors

    def test_an_invalid_bibliography_file_is_refused(self):
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")
        bibliography_file = SimpleUploadedFile(
            "publication.json", b"not json", content_type="application/json"
        )

        form = ReviewDescriptionForm(
            data={
                "reviewers": [assessor.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            },
            files={"bibliography_file": bibliography_file},
        )

        assert not form.is_valid()
        assert "bibliography_file" in form.errors


@pytest.mark.django_db
@pytest.mark.review
class TestReviewDescriptionFormDuplicateLiterature:
    # A publication that already has an assessment is refused, naming the existing
    # assessment (FS-005 User Story 2 scenario 4, FR-007).

    def test_a_publication_with_an_existing_assessment_is_refused(self):
        existing = ReviewFactory()
        assessor = PersonFactory(is_claimed=True, password="test-pass-123")

        form = ReviewDescriptionForm(
            data={
                "literature": existing.literature.pk,
                "reviewers": [assessor.pk],
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert not form.is_valid()
        errors = " ".join(form.errors.get("literature", []))
        assert existing.dataset.name in errors
