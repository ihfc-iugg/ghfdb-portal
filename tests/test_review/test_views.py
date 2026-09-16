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
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.urls import reverse
from fairdm.factories import LiteratureItemFactory
from guardian.shortcuts import get_perms

from review.models import Review, SubmittedFile
from review.states import States
from review.views import (
    ReviewConfirmView,
    ReviewCreateView,
    ReviewListView,
    ReviewUploadView,
)
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


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadReportTemplate:
    """T021, spec.md User Story 3 scenario 1, FR-009: a clean file's report
    names how many sites and determinations would be created, and how many
    existing records would be updated — asserted against the rendered HTML,
    the same way T012 tests its list item template rather than the context
    dict."""

    def test_a_clean_reports_counts_are_named_in_the_rendered_html(self):
        from project.ghfdb.report import GHFDBImportReport

        review = ReviewFactory()
        report = GHFDBImportReport(
            sites_created=4,
            sites_updated=9,
            determinations_created=6,
            determinations_updated=11,
            failures=(),
        )

        html = render_to_string(
            "review/upload_report.html", {"review": review, "report": report}
        )

        assert "4" in html
        assert "9" in html
        assert "6" in html
        assert "11" in html


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadReportTemplateFailures:
    """T025, spec.md User Story 4 scenarios 1-2, FR-011/FR-012: every
    failure is listed with its row, the template's own column heading and
    the reason, asserted against the rendered HTML rather than the context
    — the same way T021 tests the clean-report state."""

    def test_every_failure_is_listed_with_its_row_column_and_reason(self):
        from project.ghfdb.report import GHFDBImportReport, RowFailure

        review = ReviewFactory()
        report = GHFDBImportReport(
            sites_created=0,
            sites_updated=0,
            determinations_created=0,
            determinations_updated=0,
            failures=(
                RowFailure(
                    row_number=3, column="q", reason="This field cannot be blank."
                ),
                RowFailure(
                    row_number=7,
                    column="environment",
                    reason=(
                        "Invalid value 'swamp' for GeographicEnvironment "
                        "vocabulary. Valid options are: [...]"
                    ),
                ),
            ),
        )

        html = render_to_string(
            "review/upload_report.html", {"review": review, "report": report}
        )

        assert "3" in html
        assert "This field cannot be blank." in html
        assert "7" in html
        assert "environment" in html
        assert "swamp" in html
        assert "GeographicEnvironment" in html

    def test_all_failures_are_reported_together_not_only_the_first(self):
        from project.ghfdb.report import GHFDBImportReport, RowFailure

        review = ReviewFactory()
        report = GHFDBImportReport(
            sites_created=0,
            sites_updated=0,
            determinations_created=0,
            determinations_updated=0,
            failures=(
                RowFailure(row_number=1, column="q", reason="first failure text"),
                RowFailure(row_number=2, column="qc", reason="second failure text"),
                RowFailure(
                    row_number=3, column="tc_mean", reason="third failure text"
                ),
            ),
        )

        html = render_to_string(
            "review/upload_report.html", {"review": review, "report": report}
        )

        assert "first failure text" in html
        assert "second failure text" in html
        assert "third failure text" in html


def _submitted_file(review, user, content, name="assessment.xlsx"):
    return SubmittedFile.objects.create(
        review=review,
        file=ContentFile(content, name=name),
        submitted_by=user,
    )


@pytest.mark.django_db
@pytest.mark.review
class TestReviewConfirmViewAccess:
    """T022, plan.md's access table: the confirm route is open to the
    assessment's own uploader or to any Data Curator, and refused to
    everyone else, the same as the upload route (T020)."""

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_the_uploader_is_granted_entry(self, rf, assessor, valid_upload_bytes):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)

        response = self._confirm(rf, assessor, review)

        assert response.status_code == 302

    def test_a_different_assessor_is_refused(
        self, client, assessor, data_assessor_group, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)
        other = ClaimedPersonFactory()
        other.groups.add(data_assessor_group)
        client.force_login(other)

        response = client.post(reverse("review-confirm", kwargs={"pk": review.pk}))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)

        response = client.post(reverse("review-confirm", kwargs={"pk": review.pk}))

        assert response.status_code == 302
        assert response.url != reverse("review-confirm", kwargs={"pk": review.pk})


@pytest.mark.django_db
@pytest.mark.review
class TestReviewConfirmViewWriting:
    """T022, spec.md User Story 3 scenario 4, FR-008/FR-010, D6: confirming
    re-runs the check against the stored file and writes in the same
    transaction, stamping ``imported_at`` and moving the assessment out of
    ``DESCRIBED`` — with the counts written matching the counts a check of
    the same file reports.
    """

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_confirming_writes_the_checked_file_and_stamps_imported_at(
        self, rf, assessor, valid_upload_bytes
    ):
        from heat_flow.models import HeatFlowSite

        review = ReviewFactory(uploaded_by=assessor)
        submission = _submitted_file(review, assessor, valid_upload_bytes)

        response = self._confirm(rf, assessor, review)

        assert response.status_code == 302
        submission.refresh_from_db()
        assert submission.imported_at is not None
        assert HeatFlowSite.objects.filter(dataset=review.dataset).exists()

    def test_confirming_by_an_assessor_moves_the_assessment_to_awaiting_decision(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)

        self._confirm(rf, assessor, review)

        review.refresh_from_db()
        assert review.state == States.AWAITING_DECISION

    def test_confirming_by_a_curator_completes_the_assessment_immediately(
        self, rf, curator, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=curator)
        _submitted_file(review, curator, valid_upload_bytes)

        self._confirm(rf, curator, review)

        review.refresh_from_db()
        assert review.state == States.COMPLETE

    def test_confirming_redirects_to_the_dataset(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)

        response = self._confirm(rf, assessor, review)

        assert response.url == review.dataset.get_absolute_url()

    def test_the_written_counts_match_a_checks_reported_counts(
        self, rf, assessor, valid_upload_bytes
    ):
        from heat_flow.models import HeatFlow, HeatFlowSite
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)
        checked_outcome = import_ghfdb_template(
            valid_upload_bytes, review.dataset, check_only=True
        )
        report = build_report(checked_outcome)

        self._confirm(rf, assessor, review)

        assert (
            HeatFlowSite.objects.filter(dataset=review.dataset).count()
            == report.sites_created
        )
        assert (
            HeatFlow.objects.filter(dataset=review.dataset).count()
            == report.determinations_created
        )


@pytest.mark.django_db
@pytest.mark.review
class TestReviewConfirmViewIdempotency:
    """T023, spec.md User Story 3 scenario 6, FR-024, D6: a second
    confirmation for an assessment already written is a no-op redirect —
    the assessment's own state is the idempotency key, so nothing is
    written twice."""

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_a_second_confirmation_does_not_write_twice(
        self, rf, assessor, valid_upload_bytes
    ):
        from heat_flow.models import HeatFlowSite

        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)
        self._confirm(rf, assessor, review)
        count_after_first = HeatFlowSite.objects.filter(dataset=review.dataset).count()

        second = self._confirm(rf, assessor, review)

        assert second.status_code == 302
        assert (
            HeatFlowSite.objects.filter(dataset=review.dataset).count()
            == count_after_first
        )

    def test_a_second_confirmation_still_redirects_to_the_result(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)
        self._confirm(rf, assessor, review)

        second = self._confirm(rf, assessor, review)

        assert second.url == review.dataset.get_absolute_url()
