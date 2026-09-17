"""The assessment workflow's navigation entry (T013, plan.md "Notification").

The entries this module used to hold, pointing at ``review-list`` and
``reviewer-list``, were retired in T010a along with the views and routes
they named; ``review-list`` is restored, ``reviewer-list`` is not (US-1
does not touch the reviewer directory).
"""

from django.utils.translation import gettext_lazy as _
from fairdm.menus import AppMenu
from flex_menu import MenuItem

from .models import Review
from .permissions import is_data_curator
from .states import States


class AssessmentMenuItem(MenuItem):
    """The entry everyone sees (FR-001), carrying for a Data Curator the
    number of assessments waiting on a decision (FR-022, D8: no notification
    framework, this count is how a curator is told there is something to
    look at).

    Shown to every visitor, signed in or not, because the page it leads to
    is public — a public page reachable only by typing its URL is not
    public in any useful sense.

    ``extra_context["badge"]`` depends on the signed-in user and on the
    current queue, both of which only exist per request, so it is computed
    here in ``check()`` — the one hook flex_menu calls with the request —
    rather than at import time like the rest of this item's
    ``extra_context``. The item is a module-level singleton reused across
    every request, so a stale badge from one request's curator must not
    survive into the next request's anonymous visitor: every call rebuilds
    ``extra_context`` from scratch rather than only adding to it.
    """

    def check(self, request, **kwargs):
        user = getattr(request, "user", None)
        extra_context = {k: v for k, v in self.extra_context.items() if k != "badge"}
        if user is not None and is_data_curator(user):
            extra_context["badge"] = Review.objects.filter(
                state=States.AWAITING_DECISION
            ).count()
        self.extra_context = extra_context
        return True


assessment_entry = AssessmentMenuItem(
    name="assessments",
    view_name="review-list",
    extra_context={"label": _("Data Assessments"), "icon": "verified"},
)

#: The section the entry sits in. A heading of its own rather than an entry
#: appended to the end of the navigation, which filed it under whichever
#: heading happened to be last.
#:
#: A plain parent item, the same shape the framework's own Community and
#: Documentation headings take: the sidebar draws a parent as a section
#: heading unless its context marks it collapsible, and its name is the
#: heading text.
assessment_group = MenuItem(_("Data Assessment"), children=[assessment_entry])


def position_of(menu, name):
    """Where the child called *name* sits among *menu*'s direct children.

    Looked up rather than written down as a number: the navigation is
    assembled from the framework's own entries and this project's, so the
    index any one of them lands at depends on what else has been added by the
    time this module is imported. Falls back to the end when the framework no
    longer ships that entry, which puts the group in the position it held
    before rather than raising on a page that has nothing to do with it.
    """
    match = menu.get(name, maxlevel=1)
    children = list(menu.children)
    return children.index(match) if match in children else len(children)


AppMenu.insert(assessment_group, position=position_of(AppMenu, "Community"))
