"""Tests for review.states (T003).

Four states, five transitions (data-model.md): every legal transition
succeeds, and at least one illegal transition per state is refused —
including the one rule enforced by actor rather than by state alone: only a
Data Curator may reach COMPLETE from AWAITING_DECISION.
"""

import pytest
from django.contrib.auth.models import Group

from tests.test_review.factories import ClaimedPersonFactory


@pytest.fixture
def curator(db):
    person = ClaimedPersonFactory()
    person.groups.add(Group.objects.get_or_create(name="Data Curator")[0])
    return person


@pytest.fixture
def assessor(db):
    person = ClaimedPersonFactory()
    person.groups.add(Group.objects.get_or_create(name="Data Assessor")[0])
    return person


class _AssessmentStub:
    """A stand-in carrying just the one attribute the state machine reads
    and writes. ``states.py`` operates on any object shaped like this — it
    does not import ``Review`` — so this task's tests do not depend on
    ``Review`` growing a ``state`` field, which is T006's job."""

    def __init__(self, state):
        self.state = state


def review_in(state):
    return _AssessmentStub(state)


@pytest.mark.django_db
@pytest.mark.review
class TestConfirmUpload:
    """DESCRIBED or CHANGES_REQUESTED -> AWAITING_DECISION (assessor) or
    COMPLETE (curator) — FR-017/FR-018 hold regardless of which of the two
    origin states the confirmation started from."""

    def test_assessor_confirming_from_described_reaches_awaiting_decision(
        self, assessor
    ):
        from review.states import States, confirm_upload

        review = review_in(States.DESCRIBED)
        confirm_upload(review, assessor)

        assert review.state == States.AWAITING_DECISION

    def test_curator_confirming_from_described_reaches_complete_directly(self, curator):
        from review.states import States, confirm_upload

        review = review_in(States.DESCRIBED)
        confirm_upload(review, curator)

        assert review.state == States.COMPLETE

    def test_assessor_confirming_a_replacement_from_changes_requested_reaches_awaiting_decision(
        self, assessor
    ):
        from review.states import States, confirm_upload

        review = review_in(States.CHANGES_REQUESTED)
        confirm_upload(review, assessor)

        assert review.state == States.AWAITING_DECISION

    def test_refused_from_awaiting_decision(self, assessor):
        from review.states import IllegalTransition, States, confirm_upload

        review = review_in(States.AWAITING_DECISION)

        with pytest.raises(IllegalTransition):
            confirm_upload(review, assessor)

    def test_refused_from_complete(self, assessor):
        from review.states import IllegalTransition, States, confirm_upload

        review = review_in(States.COMPLETE)

        with pytest.raises(IllegalTransition):
            confirm_upload(review, assessor)


@pytest.mark.django_db
@pytest.mark.review
class TestApprove:
    """AWAITING_DECISION -> COMPLETE, curator only."""

    def test_curator_approves_a_waiting_assessment(self, curator):
        from review.states import States, approve

        review = review_in(States.AWAITING_DECISION)
        approve(review, curator)

        assert review.state == States.COMPLETE

    def test_a_non_curator_cannot_approve(self, assessor):
        """The one rule T003's acceptance names explicitly: a non-curator
        must not reach COMPLETE from AWAITING_DECISION."""
        from review.states import IllegalTransition, States, approve

        review = review_in(States.AWAITING_DECISION)

        with pytest.raises(IllegalTransition):
            approve(review, assessor)

        assert review.state == States.AWAITING_DECISION

    def test_refused_from_described(self, curator):
        from review.states import IllegalTransition, States, approve

        review = review_in(States.DESCRIBED)

        with pytest.raises(IllegalTransition):
            approve(review, curator)


@pytest.mark.django_db
@pytest.mark.review
class TestSendBack:
    """AWAITING_DECISION -> CHANGES_REQUESTED, curator only."""

    def test_curator_sends_a_waiting_assessment_back(self, curator):
        from review.states import States, send_back

        review = review_in(States.AWAITING_DECISION)
        send_back(review, curator)

        assert review.state == States.CHANGES_REQUESTED

    def test_a_non_curator_cannot_send_back(self, assessor):
        from review.states import IllegalTransition, States, send_back

        review = review_in(States.AWAITING_DECISION)

        with pytest.raises(IllegalTransition):
            send_back(review, assessor)

    def test_refused_from_changes_requested(self, curator):
        from review.states import IllegalTransition, States, send_back

        review = review_in(States.CHANGES_REQUESTED)

        with pytest.raises(IllegalTransition):
            send_back(review, curator)
