# Tests for ``project/heat_flow/management/commands/refresh_quality.py``.

from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command

from tests.test_heat_flow.test_signals import Network, StoredScores

pytestmark = pytest.mark.django_db

REVISION = "hfqa_tool 0.2"


def run(*options):
    out = StringIO()
    call_command("refresh_quality", *options, stdout=out)
    return out.getvalue()


def every_record():
    from heat_flow.models import (
        HeatFlow,
        IntervalConductivity,
        ParentHeatFlow,
        ThermalGradient,
    )

    return [
        record
        for model in (ThermalGradient, IntervalConductivity, HeatFlow, ParentHeatFlow)
        for record in model.objects.all()
    ]


def stored():
    return {
        (type(record).__name__, record.pk): StoredScores.read(record)
        for record in every_record()
    }


def unscore(*, scheme):
    """Overwrite every stored score with a value no calculation would give."""
    from heat_flow.models import (
        HeatFlow,
        IntervalConductivity,
        ParentHeatFlow,
        ThermalGradient,
    )

    for model in (ThermalGradient, IntervalConductivity):
        model.objects.update(score=9.9, score_missing=True, quality_scheme=scheme)
    HeatFlow.objects.update(
        U_score="U4", T_score=9.9, TC_score=9.9, M_score="M4", quality="stale", quality_scheme=scheme
    )
    ParentHeatFlow.objects.update(
        U_score="U4", M_score="M4", quality="stale", quality_scheme=scheme
    )


class TestRecordsWrittenBeforeScoringExisted:
    def test_a_record_with_no_revision_is_scored(self):
        Network(), Network()
        unscore(scheme="")
        assert StoredScores.differing()

        output = run()

        assert StoredScores.differing() == []
        assert {scheme for values in stored().values() for scheme in [values["quality_scheme"]]} == {REVISION}
        assert "2 gradients" in output
        assert "2 parents" in output

    def test_a_record_scored_by_another_revision_is_scored(self):
        Network()
        unscore(scheme="hfqa_tool 0.1")

        run()

        assert StoredScores.differing() == []

    def test_a_child_reads_the_fresh_score_of_what_it_uses(self):
        mine = Network()
        unscore(scheme="")

        run()

        child = type(mine.child).objects.get(pk=mine.child.pk)
        assert child.T_score is not None
        assert child.M_score != "Mx"
        assert StoredScores.differing() == []

    def test_a_record_with_no_determination_is_scored_not_determined(self):
        from tests.factories import ParentHeatFlowFactory

        parent = ParentHeatFlowFactory()
        type(parent).objects.filter(pk=parent.pk).update(quality_scheme="", quality="x")

        run()

        stored_parent = type(parent).objects.get(pk=parent.pk)
        assert stored_parent.quality == "Ux.Mx.-------"
        assert stored_parent.quality_scheme == REVISION


class TestRunningItAgain:
    def test_a_second_run_changes_nothing_and_refreshes_nothing(self):
        Network(), Network()
        unscore(scheme="")
        run()
        first = stored()

        output = run()

        assert stored() == first
        assert "0 gradients" in output
        assert "0 parents" in output

    def test_all_over_unchanged_inputs_gives_identical_values(self):
        Network(), Network("probing_offshore", penetration=2, tilt=5)
        first = stored()

        output = run("--all")
        second = stored()
        run("--all")

        assert second == first
        assert stored() == first
        assert "2 gradients" in output

    def test_by_default_a_current_record_is_left_alone_and_all_repairs_it(self):
        mine = Network()
        type(mine.child).objects.filter(pk=mine.child.pk).update(quality="damaged")

        run()
        assert type(mine.child).objects.get(pk=mine.child.pk).quality == "damaged"

        run("--all")
        assert type(mine.child).objects.get(pk=mine.child.pk).quality != "damaged"
        assert StoredScores.differing() == []


class TestEveryScoreReadsBackItsRevision:
    def test_after_a_run_no_record_carries_another_revision(self):
        Network(), Network("probing_offshore", penetration=2, tilt=5)
        unscore(scheme="hfqa_tool 0.1")

        run()

        assert {values["quality_scheme"] for values in stored().values()} == {REVISION}

    def test_a_record_is_scored_whatever_the_size_of_the_chunks(self):
        from heat_flow.management.commands.refresh_quality import Command

        for _ in range(3):
            Network()
        unscore(scheme="")

        original = Command.CHUNK_SIZE
        Command.CHUNK_SIZE = 2
        try:
            run()
        finally:
            Command.CHUNK_SIZE = original

        assert StoredScores.differing() == []
        assert {values["quality_scheme"] for values in stored().values()} == {REVISION}


class TestTheDeployedContainer:
    def test_it_refreshes_quality_after_migrating_and_before_serving(self):
        dockerfile = (
            Path(__file__).resolve().parents[4] / "deploy" / "Dockerfile"
        ).read_text()

        command = dockerfile[dockerfile.index("CMD ") :]

        assert (
            command.index("migrate")
            < command.index("refresh_quality")
            < command.index("gunicorn")
        )
