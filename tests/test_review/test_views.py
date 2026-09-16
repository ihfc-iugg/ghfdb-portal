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
    ReviewQueueView,
    ReviewUploadView,
)
from tests.test_ghfdb.test_importers import ROW, _build_official_xlsx, make_dataset
from tests.test_review.factories import ClaimedPersonFactory, ReviewFactory

_XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def _xlsx_upload(name: str, content: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content, content_type=_XLSX_CONTENT_TYPE)


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
class TestReviewQueueViewAccess:
    """T033, plan.md's access table: the decision queue is served to a Data
    Curator and refused to everyone else, including a Data Assessor,
    whether reached through the navigation or a direct URL — the same
    refusal shape ``ReviewListView`` uses."""

    def test_a_data_curator_is_granted_entry(self, rf, curator):
        request = rf.get(reverse("review-queue"))
        request.user = curator

        response = ReviewQueueView.as_view()(request)

        assert response.status_code == 200

    def test_a_data_assessor_is_refused(self, client, assessor):
        client.force_login(assessor)

        response = client.get(reverse("review-queue"))

        assert response.status_code == 403

    def test_a_signed_in_user_in_neither_role_is_refused(self, client, outsider):
        client.force_login(outsider)

        response = client.get(reverse("review-queue"))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client
    ):
        response = client.get(reverse("review-queue"))

        assert response.status_code == 302
        assert response.url != reverse("review-queue")


@pytest.mark.django_db
@pytest.mark.review
class TestReviewQueueViewContent:
    """T033, spec.md User Story 6 scenario 1: an assessment waiting on a
    decision appears in the queue, and one that has not reached
    ``AWAITING_DECISION`` does not."""

    def test_only_awaiting_decision_assessments_are_listed(self, rf, curator):
        waiting = ReviewFactory(state=States.AWAITING_DECISION)
        ReviewFactory(state=States.DESCRIBED)
        request = rf.get(reverse("review-queue"))
        request.user = curator

        response = ReviewQueueView.as_view()(request)

        assert list(response.context_data["object_list"]) == [waiting]


@pytest.mark.django_db
@pytest.mark.review
class TestReviewQueueItemTemplate:
    """T033, spec.md User Story 6 scenario 1: each row names the
    publication it covers and who uploaded it, asserted against the
    rendered HTML rather than the template context (T012's pattern) —
    the full queue page extends the shared chrome that raises for a
    signed-in user under ``DEBUG=False`` (D16/#367), so this is what proves
    the row's content."""

    def test_row_names_the_publication_and_uploader(self, assessor):
        review = ReviewFactory(
            uploaded_by=assessor,
            state=States.AWAITING_DECISION,
        )

        html = render_to_string(
            "review/review_queue_item.html", {"review": review}
        )

        assert str(review.literature) in html
        assert str(assessor) in html


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
class TestReviewUploadViewHeaderRefusal:
    """T026, spec.md User Story 4 scenario 3, ADR 0003, research.md "The
    blocker nothing here can fix": a file whose header carries the two
    misspellings the currently distributed template ships with is refused
    on the header alone, before any row is read. This is a decision, not a
    defect — the test proves the refusal happens and that it is reported as
    a checkable outcome rather than an unhandled exception."""

    def _post(self, rf, user, review, file):
        request = rf.post(f"/assessments/{review.pk}/upload/", data={"file": file})
        request.user = user
        return ReviewUploadView.as_view()(request, pk=review.pk)

    def _outdated_template_bytes(self) -> bytes:
        outdated = {
            key: value for key, value in ROW.items() if key != "tc_pT_function"
        }
        outdated["tc_pT_fuction"] = ""
        outdated["Ref_ISGN"] = outdated.pop("Ref_IGSN", "")
        return _build_official_xlsx(list(outdated.keys()), [list(outdated.values())])

    def test_an_outdated_header_is_refused_without_reporting_row_failures(
        self, rf, assessor
    ):
        review = ReviewFactory(uploaded_by=assessor)
        outdated_file = _xlsx_upload(
            "assessment.xlsx", self._outdated_template_bytes()
        )

        response = self._post(rf, assessor, review, outdated_file)

        assert response.status_code == 200
        assert response.context_data.get("header_refused") is True
        assert "report" not in response.context_data

    def test_the_refused_file_is_still_kept_as_a_submission(self, rf, assessor):
        review = ReviewFactory(uploaded_by=assessor)
        outdated_file = _xlsx_upload(
            "assessment.xlsx", self._outdated_template_bytes()
        )

        self._post(rf, assessor, review, outdated_file)

        assert SubmittedFile.objects.filter(review=review).exists()


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadReportTemplateHeaderRefusal:
    """T026: the header-refusal message says the template is out of date
    rather than quoting a column name the reader cannot act on, asserted
    against the rendered HTML."""

    def test_the_message_says_the_template_is_out_of_date(self):
        review = ReviewFactory()

        html = render_to_string(
            "review/upload_report.html",
            {"review": review, "header_refused": True},
        )

        assert "out of date" in html

    def test_no_column_name_is_quoted_and_no_row_failures_appear(self):
        review = ReviewFactory()

        html = render_to_string(
            "review/upload_report.html",
            {"review": review, "header_refused": True},
        )

        assert "tc_pT_fuction" not in html
        assert "Ref_ISGN" not in html
        assert "problem" not in html
        assert "<ul>" not in html


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


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadViewReupload:
    """T027, spec.md User Story 4 scenario 4, FR-014/FR-015: uploading a
    corrected file against the same assessment checks the new file afresh
    — the earlier failure does not leak into the new response — while the
    superseded submission stays retrievable rather than being replaced."""

    def _post(self, rf, user, review, file):
        request = rf.post(f"/assessments/{review.pk}/upload/", data={"file": file})
        request.user = user
        return ReviewUploadView.as_view()(request, pk=review.pk)

    def test_a_corrected_reupload_is_checked_afresh_and_the_failed_submission_stays_retrievable(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        bad_row = dict(ROW)
        bad_row["environment"] = "not_a_real_value"
        failing_bytes = _build_official_xlsx(
            list(bad_row.keys()), [list(bad_row.values())]
        )
        failing_file = _xlsx_upload("assessment.xlsx", failing_bytes)

        first = self._post(rf, assessor, review, failing_file)
        first_report = first.context_data["report"]
        assert first_report.has_failures
        first_reason = first_report.failures[0].reason

        corrected_file = _xlsx_upload("assessment-corrected.xlsx", valid_upload_bytes)
        second = self._post(rf, assessor, review, corrected_file)

        assert second.status_code == 200
        second_report = second.context_data["report"]
        assert not second_report.has_failures
        assert first_reason not in str(second.context_data)

        submissions = list(SubmittedFile.objects.filter(review=review).order_by("id"))
        assert len(submissions) == 2
        assert submissions[0].file.read() == failing_bytes


#: T028, spec.md User Story 4 scenario 5, FR-013: none of these may appear
#: in a rendered failure report — internal field/model names, resource and
#: widget class names, exception type names, or a traceback marker.
_DENY_LIST = (
    "Traceback",
    "ValueError",
    "ValidationError",
    "KeyError",
    "TypeError",
    "AttributeError",
    "IntegrityError",
    "HeatFlowSite",
    "HeatFlow",
    "ParentHeatFlow",
    "GHFDBChild",
    "GHFDBParent",
    "GHFDBParentImportResource",
    "GHFDBChildImportResource",
    "ConceptWidget",
    "MultiConceptWidget",
    "RelatedModelWidget",
    "surface_temperature",
    'File "',
)


@pytest.mark.django_db
@pytest.mark.review
class TestReviewUploadReportDenyList:
    """T028, spec.md User Story 4 scenario 5, FR-013: no internal field
    name, model name or traceback marker reaches a rendered failure report
    — asserted against a deny list rather than by inspection."""

    def test_a_real_failing_files_report_carries_none_of_the_deny_list(self):
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        review = ReviewFactory()

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"
        row2["q"] = ""

        row3 = dict(ROW)
        row3["ID_parent"] = "3"
        row3["ID"] = "3"
        row3["name"] = "Test Site Gamma"
        row3["lat_NS"] = "52.0"
        row3["long_EW"] = "9.0"
        row3["tc_mean"] = "2.5"
        row3["tc_method"] = "not_a_real_method"

        outcome = import_ghfdb_template(
            make_dataset(row1, row2, row3), review.dataset, check_only=True
        )
        report = build_report(outcome)
        assert report.has_failures

        html = render_to_string(
            "review/upload_report.html", {"review": review, "report": report}
        )

        for term in _DENY_LIST:
            assert term not in html, f"{term!r} leaked into the failure report"

    def test_the_header_refusal_message_carries_none_of_the_deny_list_or_the_files_own_column_names(
        self,
    ):
        review = ReviewFactory()

        html = render_to_string(
            "review/upload_report.html",
            {"review": review, "header_refused": True},
        )

        for term in (*_DENY_LIST, "tc_pT_fuction", "Ref_ISGN"):
            assert term not in html, f"{term!r} leaked into the header refusal message"


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


@pytest.mark.django_db
@pytest.mark.review
class TestAssessorDatasetVisibility:
    """T029/T030, spec.md User Story 5 scenario 1, SC-004: an assessor's
    confirmation writes nothing to ``Dataset.visibility`` — the framework's
    own default (PRIVATE, data-model.md "Dataset visibility") is what stays
    in effect — so a dataset an assessor confirmed and no curator has
    decided on yet cannot be reached by an anonymous visitor.
    """

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_an_anonymous_visitor_cannot_reach_an_assessors_confirmed_dataset(
        self, client, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)
        self._confirm(rf, assessor, review)

        response = client.get(review.dataset.get_absolute_url())

        assert response.status_code == 404

    def test_an_assessors_confirmation_writes_nothing_to_visibility(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        _submitted_file(review, assessor, valid_upload_bytes)

        self._confirm(rf, assessor, review)

        review.refresh_from_db()
        assert review.dataset.visibility == review.dataset.VISIBILITY_CHOICES.PRIVATE


@pytest.mark.django_db
@pytest.mark.review
class TestCuratorConfirmationVisibility:
    """T029, spec.md User Story 5 scenario 2, D27: a Data Curator's own
    confirmation makes the dataset public by the one field the resolved
    framework carries (data-model.md "Dataset visibility") — asserted
    directly against the field, so removing the write fails this test.
    """

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_a_curators_own_confirmation_makes_the_dataset_public(
        self, rf, curator, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=curator)
        _submitted_file(review, curator, valid_upload_bytes)

        self._confirm(rf, curator, review)

        review.refresh_from_db()
        assert review.dataset.visibility == review.dataset.VISIBILITY_CHOICES.PUBLIC


@pytest.mark.django_db
@pytest.mark.review
class TestReviewSubmissionsRetrievability:
    """T031, spec.md User Story 5 scenario 4, SC-005: every file submitted
    against an assessment stays retrievable, including one superseded by a
    later submission, and each stays distinguishable from the current one
    (``Review.current``, data-model.md "review.SubmittedFile")."""

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def _post_upload(self, rf, user, review, file):
        request = rf.post(f"/assessments/{review.pk}/upload/", data={"file": file})
        request.user = user
        return ReviewUploadView.as_view()(request, pk=review.pk)

    def test_a_superseded_submission_stays_retrievable_and_distinguishable_from_the_current_one(
        self, rf, assessor, valid_upload_bytes
    ):
        review = ReviewFactory(uploaded_by=assessor)
        first = _submitted_file(review, assessor, valid_upload_bytes)
        self._confirm(rf, assessor, review)
        first.refresh_from_db()

        second_bytes = _build_official_xlsx(
            list(ROW.keys()), [[ROW[header] for header in ROW]]
        )
        second_upload = _xlsx_upload("assessment-2.xlsx", second_bytes)
        self._post_upload(rf, assessor, review, second_upload)

        submissions = list(review.submissions.all())
        assert len(submissions) == 2
        assert first in submissions

        current = review.current
        assert current.pk != first.pk
        assert first.imported_at is not None
        assert current.imported_at is None


@pytest.mark.django_db
@pytest.mark.review
class TestReviewConfirmViewIgnoresReviewerColumns:
    """T032, spec.md User Story 5 scenario 6, FR-023: the template's own
    reviewer columns (Reviewer_name/Reviewer_comment/Review_date) contribute
    nothing on confirmation, and the assessment's own assessors — named on
    the description form — stand unchanged."""

    def _confirm(self, rf, user, review):
        request = rf.post(f"/assessments/{review.pk}/confirm/")
        request.user = user
        return ReviewConfirmView.as_view()(request, pk=review.pk)

    def test_confirming_a_file_with_reviewer_columns_filled_in_leaves_the_assessors_unchanged(
        self, rf, assessor
    ):
        review = ReviewFactory(uploaded_by=assessor)
        review.reviewers.set([assessor])

        row = dict(ROW)
        row["Reviewer_name"] = "Jane Reviewer"
        row["Reviewer_comment"] = "Looks fine"
        row["Review_date"] = "2026-01-01"
        content = _build_official_xlsx(list(row.keys()), [list(row.values())])
        _submitted_file(review, assessor, content)

        response = self._confirm(rf, assessor, review)

        assert response.status_code == 302
        review.refresh_from_db()
        assert list(review.reviewers.all()) == [assessor]
