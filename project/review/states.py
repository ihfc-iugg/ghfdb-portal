"""The assessment state vocabulary and its transitions (T003, data-model.md
"review.states").

Four states, five transitions, and every one of them is an action a person
takes — nothing here transitions on a timer or a signal. Transitions take
the assessment and the acting person, so the one rule that depends on who is
acting (only a Data Curator may reach COMPLETE from AWAITING_DECISION) is
enforced here, in one place, rather than in each view.

These functions read and write only a ``state`` attribute, so they operate
on any assessment-shaped object — ``review.models.Review`` is the only
caller today, but nothing here imports it.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .permissions import is_data_curator


class States(models.IntegerChoices):
    DESCRIBED = 0, _("Described")
    AWAITING_DECISION = 1, _("Awaiting decision")
    CHANGES_REQUESTED = 2, _("Changes requested")
    COMPLETE = 3, _("Complete")


#: The colour each state is drawn in, as a badge variant the component library
#: understands. Declared beside the vocabulary it colours rather than in a
#: template, so every surface showing a state agrees on its colour and a state
#: added later cannot reach a page without one.
STATE_VARIANTS = {
    States.DESCRIBED: "neutral",
    States.AWAITING_DECISION: "warning",
    States.CHANGES_REQUESTED: "error",
    States.COMPLETE: "success",
}


class IllegalTransition(Exception):
    """Raised when a transition's origin state or acting person is not one
    the state machine allows."""


def confirm_upload(assessment, actor):
    """DESCRIBED or CHANGES_REQUESTED -> AWAITING_DECISION or COMPLETE.

    FR-017/FR-018: a Data Curator's confirmation is always public
    immediately, regardless of which of the two origin states it started
    from; anyone else's confirmation always waits for a decision.
    """
    if assessment.state not in (States.DESCRIBED, States.CHANGES_REQUESTED):
        raise IllegalTransition(
            f"Cannot confirm an upload from {States(assessment.state).label}."
        )
    assessment.state = (
        States.COMPLETE if is_data_curator(actor) else States.AWAITING_DECISION
    )
    return assessment


def approve(assessment, actor):
    """AWAITING_DECISION -> COMPLETE. Only a Data Curator may approve."""
    if assessment.state != States.AWAITING_DECISION:
        raise IllegalTransition(
            f"Cannot approve an assessment in {States(assessment.state).label}."
        )
    if not is_data_curator(actor):
        raise IllegalTransition("Only a Data Curator may approve an assessment.")
    assessment.state = States.COMPLETE
    return assessment


def send_back(assessment, actor):
    """AWAITING_DECISION -> CHANGES_REQUESTED. Only a Data Curator may send
    an assessment back."""
    if assessment.state != States.AWAITING_DECISION:
        raise IllegalTransition(
            f"Cannot send back an assessment in {States(assessment.state).label}."
        )
    if not is_data_curator(actor):
        raise IllegalTransition("Only a Data Curator may send an assessment back.")
    assessment.state = States.CHANGES_REQUESTED
    return assessment
