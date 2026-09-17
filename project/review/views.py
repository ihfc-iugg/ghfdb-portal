"""Assessment upload workflow views (T011, plan.md "The pages").

The list is the first of seven views the plan names; the rest (starting an
assessment, uploading a file, the decision queue) are built from US-2
onward.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, View
from django.views.generic.detail import SingleObjectMixin
from fairdm.core.dataset.models import Dataset
from fairdm.utils.permissions import assign_all_model_perms
from fairdm.views import FairDMCreateView, FairDMListView

from project.ghfdb.forms import GHFDBImportForm
from project.ghfdb.importers import import_ghfdb_template
from project.ghfdb.report import build_report

from .forms import ReviewDescriptionForm
from .models import Review, SubmittedFile
from .permissions import (
    can_manage_upload,
    is_assessment_team_member,
    is_data_curator,
)
from .states import States, approve, confirm_upload, send_back


class ReviewListView(UserPassesTestMixin, FairDMListView):
    """The assessment list (FR-001, FR-002).

    Served to a Data Assessor or a Data Curator; refused to anyone else,
    whether they reach it through the navigation entry or a direct URL —
    ``UserPassesTestMixin`` redirects an anonymous visitor to log in and
    raises ``PermissionDenied`` for a signed-in user outside both roles,
    in neither case rendering the list.
    """

    model = Review
    list_item_template = "review/review_list_item.html"
    page_title = _("Assessments")
    # FairDMListView auto-generates a FilterSet from every model field when
    # none is configured, and django-filter has no mapping for the
    # PartialDateField start_date/end_date carry — filtering is not part of
    # this story, so the field list stays empty rather than crashing.
    filterset_fields: list[str] = []

    def test_func(self):
        user = self.request.user
        return is_assessment_team_member(user)

    def get_queryset(self):
        return super().get_queryset().select_related("literature", "uploaded_by")


class ReviewQueueView(UserPassesTestMixin, FairDMListView):
    """The decision queue (T033, plan.md "The pages", FR-002, FR-019,
    spec.md User Story 6 scenario 1): assessments waiting on a Data
    Curator's decision. Served to a Data Curator; refused to anyone else,
    including the Data Assessor who uploaded one of the waiting
    assessments.
    """

    model = Review
    template_name = "review/queue.html"
    list_item_template = "review/review_queue_item.html"
    page_title = _("Assessments awaiting a decision")
    filterset_fields: list[str] = []

    def test_func(self):
        return is_data_curator(self.request.user)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(state=States.AWAITING_DECISION)
            .select_related("literature", "uploaded_by")
        )


class ReviewCreateView(UserPassesTestMixin, FairDMCreateView):
    """Start an assessment (FR-003 through FR-007, FR-016; T017).

    Object permissions on the new dataset follow ``uploaded_by`` — the
    submitting user — never the assessor list: an assessor may be a
    contributor profile with no account, for whom object permissions would
    be meaningless. The retired ``ReviewCreateView`` (``git show
    78c12d1``) called ``assign_all_model_perms`` once per reviewer instead;
    that same helper is called once here, for the uploader alone. Assessors
    are credited as dataset contributors, which is attribution rather than
    access.

    The dataset is left private: neither ``visibility`` nor ``published`` is
    set, so the framework's own defaults (both private) are what take
    effect.
    """

    model = Review
    form_class = ReviewDescriptionForm
    page_title = _("Start an assessment")

    def test_func(self):
        user = self.request.user
        return is_assessment_team_member(user)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.uploaded_by = self.request.user

        title = form.cleaned_data.get("title") or form.cleaned_data["literature"].title
        dataset = Dataset.objects.create(name=title)
        self.object.dataset = dataset
        self.object.save()
        form.save_m2m()

        assign_all_model_perms(self.request.user, dataset)

        for assessor in self.object.reviewers.all():
            dataset.add_contributor(assessor, with_roles=["DataCollector"])

        return redirect(dataset.get_absolute_url())


class ReviewUploadView(UserPassesTestMixin, DetailView):
    """Upload a file and see its check report (T020, plan.md "The pages",
    FR-008 through FR-010, D5).

    The upload form and its check report share one route and one response:
    a GET shows the blank form, and a POST stores the submission, runs the
    reader in ``check_only`` mode and renders the report in the same
    response — the dataset is never written to here (D6 leaves that to
    confirmation). The submitted file is kept regardless of whether the
    check passes, per FR-015.
    """

    model = Review
    template_name = "review/upload.html"
    context_object_name = "review"

    def test_func(self):
        return can_manage_upload(self.request.user, self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", GHFDBImportForm())
        review = self.object
        if review.state == States.CHANGES_REQUESTED:
            context.setdefault("decision_comment", review.decision_comment)
        return context

    def post(self, request, *args, **kwargs):
        self.object = review = self.get_object()
        form = GHFDBImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        uploaded_file = form.cleaned_data["file"]
        content = uploaded_file.read()
        SubmittedFile.objects.create(
            review=review,
            file=ContentFile(content, name=uploaded_file.name),
            submitted_by=request.user,
        )
        try:
            outcome = import_ghfdb_template(content, review.dataset, check_only=True)
        except ValueError:
            # ADR 0003: the team's current template still carries two
            # misspelled columns this refuses, so the header refusal is a
            # decision, not a defect (research.md "The blocker nothing here
            # can fix"). The raised message quotes column names the reader
            # cannot act on (FR-012), so nothing from it reaches the page —
            # only the fact that the template is out of date.
            return self.render_to_response(
                self.get_context_data(form=GHFDBImportForm(), header_refused=True)
            )
        report = build_report(outcome)
        return self.render_to_response(
            self.get_context_data(form=GHFDBImportForm(), report=report)
        )


def _publish_if_complete(review):
    """Write the dataset public exactly when the assessment's own state
    reached ``COMPLETE`` (T029/T034, data-model.md "Dataset visibility").

    A curator's confirmation and a curator's approval both make a dataset
    public through this one path rather than each writing the fields for
    itself.

    "Public" is both of the framework's fields. ``visibility`` governs the
    metadata and ``published`` governs the data beneath it, so a dataset that
    is one without the other is half-published — its record is discoverable
    while the measurements it exists to carry are not.
    """
    if review.state == States.COMPLETE:
        review.dataset.visibility = Dataset.VISIBILITY_CHOICES.PUBLIC
        review.dataset.published = True
        review.dataset.save(update_fields=["visibility", "published"])


class ReviewConfirmView(UserPassesTestMixin, SingleObjectMixin, View):
    """Confirm a checked upload, POST only (T022/T023, plan.md "Confirmation
    safety", FR-024, D6).

    Re-runs the check against the assessment's stored file rather than
    trusting the report the uploader saw, and writes in the same
    transaction. The assessment's own state is the idempotency key: a
    confirmation for an assessment that has already moved past ``DESCRIBED``
    or ``CHANGES_REQUESTED`` is a no-op redirect, which covers both a
    doubled submission (T023) and a report that has gone stale.
    """

    model = Review
    http_method_names = ["post"]

    def test_func(self):
        return can_manage_upload(self.request.user, self.get_object())

    def post(self, request, *args, **kwargs):
        review = self.get_object()

        if review.state not in (States.DESCRIBED, States.CHANGES_REQUESTED):
            return redirect(review.dataset.get_absolute_url())

        submission = review.current
        if submission is None:
            return redirect("review-upload", pk=review.pk)

        outcome = import_ghfdb_template(
            submission.file, review.dataset, check_only=False
        )
        if outcome.has_errors():
            return redirect("review-upload", pk=review.pk)

        submission.imported_at = timezone.now()
        submission.save(update_fields=["imported_at"])
        confirm_upload(review, request.user)
        review.save(update_fields=["state"])
        _publish_if_complete(review)

        return redirect(review.dataset.get_absolute_url())


class ReviewDecideView(UserPassesTestMixin, SingleObjectMixin, View):
    """Approve a waiting assessment, POST only (T034, plan.md "The pages",
    FR-019, FR-021, spec.md User Story 6 scenarios 2 and 5).

    Curators only — ``approve`` raises ``IllegalTransition`` for anyone
    else too (states.py's own rule), but ``test_func`` refuses the request
    before that is ever reached, the same shape ``ReviewQueueView`` uses.
    An assessment no longer ``AWAITING_DECISION`` is a no-op redirect, the
    same idempotency shape ``ReviewConfirmView`` uses.
    """

    model = Review
    http_method_names = ["post"]

    def test_func(self):
        return is_data_curator(self.request.user)

    def post(self, request, *args, **kwargs):
        review = self.get_object()

        if review.state != States.AWAITING_DECISION:
            return redirect("review-queue")

        action = request.POST.get("action")
        if action == "approve":
            approve(review, request.user)
        elif action == "send_back":
            send_back(review, request.user)
            review.decision_comment = request.POST.get("comment", "")
        else:
            return redirect("review-queue")

        review.decided_by = request.user
        review.decided_at = timezone.now()
        review.save(
            update_fields=["state", "decided_by", "decided_at", "decision_comment"]
        )
        _publish_if_complete(review)

        return redirect("review-queue")
