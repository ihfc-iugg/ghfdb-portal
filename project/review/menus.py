"""The assessment workflow's navigation entries (T013, plan.md
"Notification").

Two entries under one heading. The first leads to the assessments and is
shown to everyone, because the page it leads to is public. The second is a
Data Curator's alone: it carries the count of assessments waiting on a
decision and leads to the list narrowed to them, which is what the decision
queue used to need a page of its own for.
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from fairdm.menus import AppMenu
from flex_menu import MenuItem

from .models import Review
from .permissions import is_data_curator
from .states import States


def awaiting_decision_count():
    """How many assessments are waiting on a Data Curator."""
    return Review.objects.filter(state=States.AWAITING_DECISION).count()


class AwaitingDecisionMenuItem(MenuItem):
    """What is waiting on the signed-in Data Curator (FR-022, D8: no
    notification framework, this entry and its count are how a curator is
    told there is something to look at).

    Shown to Data Curators alone, because it leads to work only they can do.
    It points at the assessment list narrowed to the one state, which is
    what the decision queue used to be a page for.

    ``extra_context["badge"]`` depends on the signed-in user and on what is
    currently waiting, both of which only exist per request, so it is
    computed here in ``check()`` — the one hook flex_menu calls with the
    request — rather than at import time like the rest of this item's
    ``extra_context``. The item is a module-level singleton reused across
    every request, so a stale count from one request's curator must not
    survive into the next request's: every call rebuilds ``extra_context``
    from scratch rather than only adding to it.
    """

    def check(self, request, **kwargs):
        user = getattr(request, "user", None)
        if user is None or not is_data_curator(user):
            return False
        self.extra_context = {
            **{k: v for k, v in self.extra_context.items() if k != "badge"},
            "badge": awaiting_decision_count(),
        }
        return True


def narrowed_to_awaiting_decision(request, *args, **kwargs):
    """The assessment list, showing only what is waiting on a decision.

    A callable rather than ``view_name`` plus ``params``: flex_menu appends
    query parameters only to a URL given as a literal string, and caches a
    reversed one for the life of the process.
    """
    return f"{reverse('review-list')}?state={States.AWAITING_DECISION.value}"


assessment_entry = MenuItem(
    name="assessments",
    view_name="review-list",
    extra_context={"label": _("Data Assessments"), "icon": "verified"},
)

awaiting_decision_entry = AwaitingDecisionMenuItem(
    name="assessments_awaiting_decision",
    url=narrowed_to_awaiting_decision,
    extra_context={"label": _("Awaiting a decision"), "icon": "pending"},
)

#: The section the entry sits in. A heading of its own rather than an entry
#: appended to the end of the navigation, which filed it under whichever
#: heading happened to be last.
#:
#: A plain parent item, the same shape the framework's own Community and
#: Documentation headings take: the sidebar draws a parent as a section
#: heading unless its context marks it collapsible, and its name is the
#: heading text.
assessment_group = MenuItem(
    _("Data Assessment"), children=[assessment_entry, awaiting_decision_entry]
)


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
