"""Assessment upload workflow views (T011, plan.md "The pages").

The list is the first of seven views the plan names; the rest (starting an
assessment, uploading a file, the decision queue) are built from US-2
onward.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from fairdm.core.dataset.models import Dataset
from fairdm.utils.permissions import assign_all_model_perms
from fairdm.views import FairDMCreateView, FairDMListView

from .forms import ReviewDescriptionForm
from .models import Review
from .permissions import is_data_assessor, is_data_curator


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
        return is_data_assessor(user) or is_data_curator(user)

    def get_queryset(self):
        return super().get_queryset().select_related("literature", "uploaded_by")


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
        return is_data_assessor(user) or is_data_curator(user)

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
