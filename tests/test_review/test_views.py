"""Tests for review.views (T011).

Access is refused rather than the list rendering empty (spec.md User Story
1, acceptance scenarios 3 and 4).

The refusal paths go through the full request/response cycle via the test
client: ``PermissionDenied`` and the anonymous redirect both short-circuit
in ``dispatch()``, before any template renders, so the client's normal
rendering is never reached.

The served paths use ``RequestFactory`` and stop at the unrendered
``TemplateResponse`` deliberately. This project's shared page chrome
currently raises for *any* authenticated request — reproduces on the
pre-existing ``/datasets/`` page too, so it predates this story and is
flagged separately rather than fixed here (out of ``project/review/``'s
scope). What these tests exist to prove is narrower and unaffected by that
defect: ``ReviewListView.test_func`` grants entry to both roles and the
view builds a normal 200 response for each.
"""

from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.urls import reverse
from fairdm.factories import LiteratureItemFactory
from guardian.shortcuts import get_perms

from review.models import Review, SubmittedFile
from review.states import States
from review.views import ReviewCreateView, ReviewListView, ReviewUploadView
from tests.test_review.factories import ClaimedPersonFactory, ReviewFactory


@pytest.mark.django_db
@pytest.mark.review
class TestReviewListViewAccess:
    def test_a_data_assessor_is_granted_entry(self, rf, assessor):
        request = rf.get(reverse("review-list"))
        request.user = assessor

        response = ReviewListView.as_view()(request)

        assert response.status_code == 200

    def test_a_data_curator_is_granted_entry(self, rf, curator):
        request = rf.get(reverse("review-list"))
        request.user = curator

        response = ReviewListView.as_view()(request)

        assert response.status_code == 200

    def test_a_signed_in_user_in_neither_role_is_refused(self, client, outsider):
        client.force_login(outsider)

        response = client.get(reverse("review-list"))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client
    ):
        response = client.get(reverse("review-list"))

        assert response.status_code == 302
        assert response.url != reverse("review-list")


@pytest.mark.django_db
@pytest.mark.review
class TestReviewCreateViewAccess:
    """T019: the description route is served to either role and refused to
    anyone else (plan.md's access table)."""

    def test_a_data_assessor_is_granted_entry(self, rf, assessor):
        request = rf.get(reverse("review-create"))
        request.user = assessor

        response = ReviewCreateView.as_view()(request)

        assert response.status_code == 200

    def test_a_data_curator_is_granted_entry(self, rf, curator):
        request = rf.get(reverse("review-create"))
        request.user = curator

        response = ReviewCreateView.as_view()(request)

        assert response.status_code == 200

    def test_a_signed_in_user_in_neither_role_is_refused(self, client, outsider):
        client.force_login(outsider)

        response = client.get(reverse("review-create"))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client
    ):
        response = client.get(reverse("review-create"))

        assert response.status_code == 302
        assert response.url != reverse("review-create")


@pytest.mark.django_db
@pytest.mark.review
class TestReviewCreateView:
    """T017: submitting the description form writes the assessment (spec.md
    User Story 2 scenarios 1, 3 and 5, FR-003 through FR-007, FR-016).

    Built with ``RequestFactory`` directly, calling the view rather than
    ``reverse("review-create")`` — T019 registers that route, and the two
    tasks stay independent of one another's landing order this way, unlike
    T011/T014 (see decisions.md D15).

    A successful submission redirects without rendering any template, so it
    is unaffected by the chrome defect (D16) the granted-path list tests
    work around.
    """

    def _post(self, rf, user, **overrides):
        literature = overrides.pop("literature", None) or LiteratureItemFactory()
        assessor = overrides.pop("assessor", None) or ClaimedPersonFactory()
        data = {
            "literature": literature.pk,
            "reviewers": [assessor.pk],
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
            "title": "",
        }
        data.update(overrides)
        request = rf.post("/assessments/new/", data=data)
        request.user = user
        return ReviewCreateView.as_view()(request), literature, assessor

    def test_submitting_creates_an_assessment_in_described_state(self, rf, assessor):
        response, literature, _ = self._post(rf, assessor)

        assert response.status_code == 302
        review = Review.objects.get(literature=literature)
        assert review.state == States.DESCRIBED

    def test_the_new_dataset_holds_no_data_and_is_not_public(self, rf, assessor):
        self._post(rf, assessor)

        review = Review.objects.get()
        assert not review.dataset.has_data
        assert review.dataset.visibility == review.dataset.VISIBILITY_CHOICES.PRIVATE

    def test_uploaded_by_is_the_submitting_user(self, rf, assessor):
        self._post(rf, assessor)

        review = Review.objects.get()
        assert review.uploaded_by_id == assessor.pk

    def test_the_uploader_holds_object_permissions_on_the_dataset(self, rf, assessor):
        self._post(rf, assessor)

        review = Review.objects.get()
        perms = get_perms(assessor, review.dataset)
        assert "view_dataset" in perms
        assert "change_dataset" in perms
        assert "delete_dataset" in perms

    def test_each_named_assessor_is_credited_as_a_contributor(self, rf, assessor):
        _, _, named_assessor = self._post(rf, assessor)

        review = Review.objects.get()
        assert review.dataset.is_contributor(named_assessor)

    def test_a_blank_title_takes_the_publications_own_title(self, rf, assessor):
        literature = LiteratureItemFactory()
        self._post(rf, assessor, literature=literature, title="")

        review = Review.objects.get()
        assert review.dataset.name == literature.title

    def test_a_given_title_is_used_over_the_publications_own(self, rf, assessor):
        self._post(rf, assessor, title="A custom dataset title")

        review = Review.objects.get()
        assert review.dataset.name == "A custom dataset title"


@pytest.mark.django_db
@pytest.mark.review
class TestReviewListItemTemplate:
    """T012: each row names the publication it covers, its uploader and its
    state (spec.md User Story 1, acceptance scenario 5), asserted against
    the rendered HTML rather than the template context.

    Rendered directly rather than through the full list page: the page
    chrome around it is affected by the pre-existing defect noted on
    ReviewListView's tests above, and this is what T012 owns.
    """

    def test_row_names_the_publication_uploader_and_state(self, assessor):
        review = ReviewFactory(
            uploaded_by=assessor,
            state=States.AWAITING_DECISION,
        )

        html = render_to_string(
            "review/review_list_item.html", {"review": review, "object": review}
        )

        assert str(review.literature) in html
        assert str(assessor) in html
        assert review.get_state_display() in html


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadViewAccess:
    """T020, plan.md's access table: the upload route is open to the
    assessment's own uploader or to any Data Curator, and refused to
    everyone else."""

    def test_the_uploader_is_granted_entry(self, rf, assessor):
        review = ReviewFactory(uploaded_by=assessor)
        request = rf.get(f"/assessments/{review.pk}/upload/")
        request.user = assessor

        response = ReviewUploadView.as_view()(request, pk=review.pk)

        assert response.status_code == 200

    def test_any_curator_is_granted_entry_even_when_not_the_uploader(
        self, rf, assessor, curator
    ):
        review = ReviewFactory(uploaded_by=assessor)
        request = rf.get(f"/assessments/{review.pk}/upload/")
        request.user = curator

        response = ReviewUploadView.as_view()(request, pk=review.pk)

        assert response.status_code == 200

    def test_a_different_assessor_is_refused(self, client, assessor, data_assessor_group):
        review = ReviewFactory(uploaded_by=assessor)
        other = ClaimedPersonFactory()
        other.groups.add(data_assessor_group)
        client.force_login(other)

        response = client.get(reverse("review-upload", kwargs={"pk": review.pk}))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client, assessor
    ):
        review = ReviewFactory(uploaded_by=assessor)

        response = client.get(reverse("review-upload", kwargs={"pk": review.pk}))

        assert response.status_code == 302
        assert response.url != reverse("review-upload", kwargs={"pk": review.pk})


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadViewChecking:
    """T020, spec.md User Story 3 scenarios 1-2, FR-008/FR-010: a valid file
    is checked and reported without writing to the dataset, and a
    non-spreadsheet file is refused by the form before the reader ever sees
    it (D5).

    Built with ``RequestFactory`` rather than ``reverse`` + the test client,
    for the same reason T017's own tests are (decisions.md D21): the
    response renders the shared page chrome, which raises for a signed-in
    user under ``DEBUG=False`` (predates this story, django-mvp/django-mvp
    #367) — these tests stop at the unrendered ``TemplateResponse``, the
    same way T011/T019's granted-path tests do.
    """

    def _post(self, rf, user, review, file):
        request = rf.post(f"/assessments/{review.pk}/upload/", data={"file": file})
        request.user = user
        return ReviewUploadView.as_view()(request, pk=review.pk)

    def test_a_valid_file_is_checked_without_writing_to_the_dataset(
        self, rf, assessor, valid_upload_file
    ):
        review = ReviewFactory(uploaded_by=assessor)

        response = self._post(rf, assessor, review, valid_upload_file)

        assert response.status_code == 200
        review.refresh_from_db()
        assert not review.dataset.has_data

    def test_a_valid_file_creates_a_submitted_file_row(
        self, rf, assessor, valid_upload_file
    ):
        review = ReviewFactory(uploaded_by=assessor)

        self._post(rf, assessor, review, valid_upload_file)

        submission = SubmittedFile.objects.get(review=review)
        assert submission.submitted_by_id == assessor.pk
        assert submission.imported_at is None

    def test_a_non_spreadsheet_file_is_refused_before_the_reader_runs(
        self, rf, assessor
    ):
        review = ReviewFactory(uploaded_by=assessor)
        not_a_spreadsheet = SimpleUploadedFile(
            "notes.txt", b"this is not a spreadsheet", content_type="text/plain"
        )

        with mock.patch("review.views.import_ghfdb_template") as reader:
            response = self._post(rf, assessor, review, not_a_spreadsheet)

        assert response.status_code == 200
        reader.assert_not_called()
        assert not SubmittedFile.objects.filter(review=review).exists()
