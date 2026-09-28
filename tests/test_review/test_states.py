# Tests for review.states .

import pytest
from django.contrib.auth.models import Group
from fairdm.factories import PersonFactory


@pytest.fixture
def curator(db):
    person = PersonFactory(is_claimed=True, password="test-pass-123")
    person.groups.add(Group.objects.get_or_create(name="Data Curator")[0])
    return person


@pytest.fixture
def assessor(db):
    person = PersonFactory(is_claimed=True, password="test-pass-123")
    person.groups.add(Group.objects.get_or_create(name="Data Assessor")[0])
    return person


class _AssessmentStub:
    """A stand-in carrying just the one attribute the state machine reads
    and writes. ``states.py`` operates on any object shaped like this — it
    does not import ``Review`` — so these tests do not depend on
    ``Review`` growing a ``state`` field."""

    def __init__(self, state):
        self.state = state


def review_in(state):
    return _AssessmentStub(state)


@pytest.mark.django_db
@pytest.mark.review
class TestConfirmUpload:
    # DESCRIBED or CHANGES_REQUESTED -> AWAITING_DECISION (assessor) or COMPLETE
    # (curator) — FS-005 FR-017/FR-018 hold regardless of which of the two origin
    # states the confirmation started from.

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
    def test_curator_approves_a_waiting_assessment(self, curator):
        from review.states import States, approve

        review = review_in(States.AWAITING_DECISION)
        approve(review, curator)

        assert review.state == States.COMPLETE

    def test_a_non_curator_cannot_approve(self, assessor):
        # The one rule FS-005's acceptance criteria name explicitly: a non-curator must
        # not reach COMPLETE from AWAITING_DECISION.
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
