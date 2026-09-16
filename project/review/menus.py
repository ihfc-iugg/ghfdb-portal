"""The assessment workflow's navigation entry (T013, plan.md "Notification").

The entries this module used to hold, pointing at ``review-list`` and
``reviewer-list``, were retired in T010a along with the views and routes
they named; ``review-list`` is restored, ``reviewer-list`` is not (US-1
does not touch the reviewer directory).
"""

from django.utils.translation import gettext as _
from fairdm.menus import AppMenu
from flex_menu import MenuItem

from .models import Review
from .permissions import is_data_assessor, is_data_curator
from .states import States


class AssessmentMenuItem(MenuItem):
    """The single entry both roles see (FR-001), carrying the curator's
    queue count (FR-022, D8: no notification framework, the count on this
    entry and the queue listing it are how curators are told).

    ``extra_context["badge"]`` depends on the signed-in user and the
    current queue, both of which only exist per request, so it is computed
    here in ``check()`` — the one hook flex_menu calls with the request —
    rather than at import time like the rest of this item's
    ``extra_context``. The item is a module-level singleton reused across
    every request, so a stale badge from one request's curator must not
    survive into the next request's assessor: every call rebuilds
    ``extra_context`` from scratch rather than only adding to it.
    """

    def check(self, request, **kwargs):
        user = getattr(request, "user", None)
        if user is None or not (is_data_assessor(user) or is_data_curator(user)):
            return False
        extra_context = {k: v for k, v in self.extra_context.items() if k != "badge"}
        if is_data_curator(user):
            extra_context["badge"] = Review.objects.filter(
                state=States.AWAITING_DECISION
            ).count()
        self.extra_context = extra_context
        return True


assessment_entry = AssessmentMenuItem(
    name="assessments",
    view_name="review-list",
    extra_context={"label": _("Assessments"), "icon": "clipboard-list"},
)
AppMenu.append(assessment_entry)
