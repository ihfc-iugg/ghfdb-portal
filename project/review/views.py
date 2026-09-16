"""Assessment upload workflow views (T011, plan.md "The pages").

The list is the first of seven views the plan names; the rest (starting an
assessment, uploading a file, the decision queue) are built from US-2
onward.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext as _
from fairdm.views import FairDMListView

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
