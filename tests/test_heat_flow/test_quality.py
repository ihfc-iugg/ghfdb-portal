# Tests for the quality scheme. Mirrors ``project/heat_flow/quality.py``.
#
# The expected values of the conformance cases are the output of the toolbox's own
# functions (hfqa_tool V0.2, specs/007-quality-scores/research.md R3). They are never
# re-derived here. The factories attach random concepts, so every concept a score reads
# is set explicitly.

import pytest
from heat_flow import vocabularies
from research_vocabs.models import Concept

from tests.factories import (
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ProbeMetadataFactory,
    ThermalGradientFactory,
)

pytestmark = pytest.mark.django_db


def concepts(vocabulary, *names):
    """Return the concepts of *vocabulary* called *names*, refusing a misspelt name."""
    found = list(Concept.get_for_vocabulary(vocabulary).filter(name__in=names))
    assert {concept.name for concept in found} == set(names)
    return found


def build_interval(
    explo_method,
    *,
    elevation=None,
    top=None,
    bottom=None,
    penetration=None,
    tilt=None,
):
    """Build an interval at a site, with probe metadata when a probe input is given."""
    site = HeatFlowSiteFactory(explo_method=explo_method, elevation=elevation)
    interval = HeatFlowIntervalFactory(site=site, top=top, bottom=bottom)
    if penetration is not None or tilt is not None:
        ProbeMetadataFactory(
            interval=interval, penetration=penetration, tilt=tilt, probe_type=[]
        )
    return interval


def build_gradient(interval, *, number=None, top=(), bottom=()):
    """Build a gradient on *interval* whose scored concepts are exactly those given."""
    return ThermalGradientFactory(
        sample=interval,
        number=number,
        method_top=concepts(vocabularies.TemperatureMethod, *top),
        method_bottom=concepts(vocabularies.TemperatureMethod, *bottom),
    )


def build_conductivity(
    interval,
    *,
    number=None,
    source=(),
    location=(),
    method=(),
    saturation=(),
    pT=(),
):
    """Build a conductivity on *interval* whose scored concepts are exactly those given."""
    return IntervalConductivityFactory(
        sample=interval,
        number=number,
        source=concepts(vocabularies.ConductivitySource, *source),
        location=concepts(vocabularies.ConductivityLocation, *location),
        method=concepts(vocabularies.ConductivityMethod, *method),
        saturation=concepts(vocabularies.ConductivitySaturation, *saturation),
        pT_conditions=concepts(vocabularies.ConductivityPTConditions, *pT),
    )


def case(name, explo, **fields):
    """One conformance case: its inputs and the toolbox's output for them."""
    return pytest.param(dict(explo=explo, **fields), id=name)


# Each case carries the toolbox's T and TC (research R3, equal to the child's corrected
# scores), whether the toolbox marked the M-score, and the uncorrected value where a child
# rule changes it.
CONFORMANCE_CASES = [
    case(
        "X1-continuous-eq",
        "drilling",
        recordings=10,
        top=("LOGeq",),
        bottom=("LOGeq",),
        depths=(0, 1000),
        location=("actual",),
        source=("insitu_probe",),
        count=20,
        saturation=("saturatedMeasured",),
        pT=("actualInSitu",),
        in_situ=None,
        T=1.1,
        TC=0.9,
        marked=True,
        TC_uncorrected=1.1,
    ),
    case(
        "X2-continuous-pert",
        "drilling",
        recordings=8,
        top=("LOGpert",),
        bottom=("LOGpert",),
        depths=(0, 800),
        location=("actual",),
        source=("core_samples",),
        count=10,
        saturation=("saturatedMeasured",),
        pT=("actualInSitu",),
        in_situ=None,
        T=0.9,
        TC=0.7,
        marked=True,
        TC_uncorrected=0.9,
    ),
    case(
        "X3-multiple-single-points",
        "drilling",
        recordings=2,
        top=("BHT",),
        bottom=("BHT",),
        depths=(0, 500),
        location=("other",),
        source=("core_samples",),
        count=5,
        saturation=("recovered",),
        pT=("replicatedT",),
        in_situ=None,
        T=0.7,
        TC=0.5,
        marked=True,
        TC_uncorrected=0.6,
    ),
    case(
        "X4-single-point-plus-surface",
        "drilling",
        recordings=1,
        top=("SUR",),
        bottom=("BHT",),
        depths=(0, 300),
        location=("other",),
        source=("cutting_samples",),
        count=1,
        saturation=("dryMeasured",),
        pT=("recordedAmbient",),
        in_situ=None,
        T=0.5,
        TC=0.3,
        marked=True,
        TC_uncorrected=0.3,
    ),
    case(
        "X5-interval-gate",
        "drilling",
        recordings=6,
        top=("LOGeq",),
        bottom=("LOGeq",),
        depths=(None, None),
        location=("literature",),
        source=("assumed_from_literature",),
        count=None,
        saturation=("unspecified",),
        pT=("unspecified",),
        in_situ=None,
        T=1.1,
        TC=0.1,
        marked=True,
        TC_uncorrected=0.1,
    ),
    case(
        "P1-probe-with-waivers",
        "probing_offshore",
        elevation=-3000,
        penetration=12,
        tilt=45,
        recordings=6,
        location=("actual",),
        source=("insitu_probe",),
        method=("probePulse",),
        saturation=("saturatedInSitu",),
        pT=("actualInSitu",),
        count=4,
        tilt_corrected=True,
        bottom_water_corrected=True,
        T=1.2,
        TC=1.2,
        marked=False,
        T_uncorrected=1.0,
    ),
    case(
        "P2-probe-without-corrections",
        "probing_offshore",
        elevation=-3000,
        penetration=12,
        tilt=45,
        recordings=6,
        location=("actual",),
        source=("insitu_probe",),
        method=("probePulse",),
        saturation=("saturatedInSitu",),
        pT=("actualInSitu",),
        count=4,
        T=1.0,
        TC=1.2,
        marked=False,
    ),
    case(
        "P3-onshore-lab",
        "probing_onshore",
        elevation=120,
        penetration=2,
        tilt=None,
        recordings=2,
        location=("other",),
        source=("core_samples",),
        method=("lineSourceFull",),
        saturation=("saturatedCalculated",),
        pT=("recordedAmbient",),
        count=2,
        T=0.4,
        TC=0.5,
        marked=True,
    ),
    case(
        "P4-clustering-literature",
        "probing_clustering",
        elevation=-1600,
        penetration=0.8,
        tilt=12,
        recordings=1,
        location=("literature",),
        source=("assumed_from_literature",),
        method=("lithology",),
        saturation=("unspecified",),
        pT=("unspecified",),
        count=None,
        T=0.4,
        TC=0.5,
        marked=False,
    ),
    case(
        "P5-no-saturation",
        "probing_offshore",
        elevation=-2000,
        penetration=4,
        tilt=5,
        recordings=3,
        location=("actual",),
        source=("insitu_probe",),
        method=("unspecified",),
        saturation=(),
        pT=("replicatedP",),
        count=1,
        T=0.9,
        TC=0.5,
        marked=True,
    ),
    case(
        "B1-agreeing-in-situ",
        "drilling",
        recordings=40,
        top=("LOGeq",),
        bottom=("cLOG",),
        depths=(100, 900),
        location=("actual",),
        source=("core_samples",),
        count=30,
        saturation=("saturatedMeasured",),
        pT=("correctedPT",),
        in_situ="considered_pt",
        T=1.1,
        TC=1.0,
        marked=False,
    ),
    case(
        "B2-not-considered",
        "drilling",
        recordings=40,
        top=("LOGeq",),
        bottom=("cLOG",),
        depths=(100, 900),
        location=("actual",),
        source=("core_samples",),
        count=30,
        saturation=("saturatedMeasured",),
        pT=("correctedPT",),
        in_situ="not_considered",
        T=1.1,
        TC=0.8,
        marked=False,
        TC_uncorrected=1.0,
    ),
    case(
        "B3-no-in-situ-correction",
        "drilling",
        recordings=40,
        top=("LOGeq",),
        bottom=("cLOG",),
        depths=(100, 900),
        location=("actual",),
        source=("core_samples",),
        count=30,
        saturation=("saturatedMeasured",),
        pT=("correctedPT",),
        in_situ=None,
        T=1.1,
        TC=0.8,
        marked=True,
        TC_uncorrected=1.0,
    ),
    case(
        "B4-mining-ambient",
        "mining",
        recordings=40,
        top=("LOGeq",),
        bottom=("cLOG",),
        depths=(100, 900),
        location=("actual",),
        source=("core_samples",),
        count=30,
        saturation=("saturatedMeasured",),
        pT=("recordedAmbient",),
        in_situ="-",
        T=1.1,
        TC=0.8,
        marked=False,
    ),
    case(
        "B5-drilling-clustering",
        "drilling_clustering",
        recordings=3,
        top=("BHT", "cBHT"),
        bottom=("BHT",),
        depths=(0, 2000),
        location=("other",),
        source=("cutting_samples",),
        count=12,
        saturation=("recovered",),
        pT=("replicatedP",),
        in_situ="considered_p",
        T=0.7,
        TC=0.5,
        marked=False,
    ),
    case(
        "B6-tunnelling-literature",
        "tunneling",
        recordings=2,
        top=("SUR",),
        bottom=("cBHT",),
        depths=(0, 1500),
        location=("literature",),
        source=("assumed_from_literature",),
        count=None,
        saturation=("dryMeasured",),
        pT=("unspecified",),
        in_situ="not_considered",
        T=0.7,
        TC=0.2,
        marked=False,
    ),
    case(
        "B7-unresolvable-surface-case",
        "drilling",
        recordings=2,
        top=("SUR",),
        bottom=("LOGeq",),
        depths=(0, 1500),
        location=("actual",),
        source=("mineral_computation",),
        count=20,
        saturation=("saturatedCalculated",),
        pT=("actualInSitu",),
        in_situ="considered_pt",
        T=0.4,
        TC=0.7,
        marked=True,
    ),
    case(
        "B8-indirect-no-methods",
        "indirect",
        recordings=5,
        top=(),
        bottom=(),
        depths=(None, None),
        location=("actual",),
        source=("core_samples",),
        count=30,
        saturation=("saturatedMeasured",),
        pT=("correctedPT",),
        in_situ="considered_pt",
        T=0.5,
        TC=0.1,
        marked=True,
    ),
    case(
        "B9-everything-unspecified",
        "drilling",
        recordings=5,
        top=("unspecified",),
        bottom=("unspecified",),
        depths=(100, 200),
        location=("literature",),
        source=("unspecified",),
        count=1,
        saturation=("unspecified",),
        pT=("unspecified",),
        in_situ="-",
        T=0.5,
        TC=0.2,
        marked=False,
    ),
]


def build_case(inputs):
    """Build the interval, gradient and conductivity a conformance case describes."""
    top_depth, bottom_depth = inputs.get("depths", (None, None))
    interval = build_interval(
        inputs["explo"],
        elevation=inputs.get("elevation"),
        top=top_depth,
        bottom=bottom_depth,
        penetration=inputs.get("penetration"),
        tilt=inputs.get("tilt"),
    )
    gradient = build_gradient(
        interval,
        number=inputs["recordings"],
        top=inputs.get("top", ()),
        bottom=inputs.get("bottom", ()),
    )
    conductivity = build_conductivity(
        interval,
        number=inputs["count"],
        source=inputs["source"],
        location=inputs["location"],
        method=inputs.get("method", ()),
        saturation=inputs["saturation"],
        pT=inputs["pT"],
    )
    return interval.site, gradient, conductivity


class TestRoute:
    @pytest.mark.parametrize(
        "explo_method",
        ["probing_onshore", "probing_offshore", "probing_clustering"],
    )
    def test_probing_methods_route_to_the_probe_rules(self, explo_method):
        from heat_flow.quality import ProbeRules, route

        site = HeatFlowSiteFactory(explo_method=explo_method)

        assert route(site) is ProbeRules

    @pytest.mark.parametrize(
        "explo_method",
        ["drilling", "drilling_clustering", "mining", "tunneling", "indirect"],
    )
    def test_excavation_and_indirect_methods_route_to_the_borehole_rules(
        self, explo_method
    ):
        from heat_flow.quality import BoreholeRules, route

        site = HeatFlowSiteFactory(explo_method=explo_method)

        assert route(site) is BoreholeRules

    @pytest.mark.parametrize("explo_method", ["other", "unspecified", None])
    def test_other_unspecified_and_empty_methods_are_not_determined(
        self, explo_method
    ):
        from heat_flow.quality import route

        site = HeatFlowSiteFactory(explo_method=explo_method)

        assert route(site) is None

    def test_a_measurement_without_a_site_is_not_determined(self):
        from heat_flow.quality import route

        assert route(None) is None


class TestConformance:
    """The scheme's output against the toolbox's own, case by case (research R3)."""

    @pytest.mark.parametrize("inputs", CONFORMANCE_CASES)
    def test_corrected_scores_equal_the_toolbox_output(self, inputs):
        from heat_flow.quality import UNCORRECTED, route

        site, gradient, conductivity = build_case(inputs)
        rules = route(site)

        t = rules.gradient(
            gradient,
            tilt_corrected=inputs.get("tilt_corrected", False),
            bottom_water_corrected=inputs.get("bottom_water_corrected", False),
        )
        tc = rules.conductivity(
            conductivity, in_situ=inputs.get("in_situ", UNCORRECTED)
        )

        assert t.value == pytest.approx(inputs["T"])
        assert tc.value == pytest.approx(inputs["TC"])
        assert (t.missing or tc.missing) is inputs["marked"]

    @pytest.mark.parametrize("inputs", CONFORMANCE_CASES)
    def test_uncorrected_scores_differ_only_where_a_child_rule_changed_them(
        self, inputs
    ):
        from heat_flow.quality import route

        site, gradient, conductivity = build_case(inputs)
        rules = route(site)

        t = rules.gradient(gradient)
        tc = rules.conductivity(conductivity)

        assert t.value == pytest.approx(inputs.get("T_uncorrected", inputs["T"]))
        assert tc.value == pytest.approx(
            inputs.get("TC_uncorrected", inputs["TC"])
        )


class TestProbeGradient:
    def probe_gradient(self, *, penetration=5, tilt=0, elevation=-3000, number=6):
        interval = build_interval(
            "probing_offshore",
            elevation=elevation,
            penetration=penetration,
            tilt=tilt,
        )
        return build_gradient(interval, number=number)

    def score(self, gradient, **corrections):
        from heat_flow.quality import ProbeRules

        return ProbeRules.gradient(gradient, **corrections)

    @pytest.mark.parametrize(
        ("penetration", "penalty"),
        [(10.01, 0.1), (10, 0.0), (3.01, 0.0), (3, -0.1), (1.01, -0.1), (1, -0.2)],
    )
    def test_penetration_bins_are_tried_largest_first(self, penetration, penalty):
        # The other inputs add +0.1 (six recordings) and nothing else.
        score = self.score(self.probe_gradient(penetration=penetration))

        assert score.value == pytest.approx(1.1 + penalty)
        assert score.missing is False

    @pytest.mark.parametrize(
        ("number", "penalty"),
        [(6, 0.1), (5, 0.0), (3, 0.0), (2, -0.1), (1, -0.2)],
    )
    def test_recording_bins_distinguish_two_from_fewer_and_more(
        self, number, penalty
    ):
        # Penetration 5 adds nothing.
        score = self.score(self.probe_gradient(number=number))

        assert score.value == pytest.approx(1.0 + penalty)

    @pytest.mark.parametrize(
        ("elevation", "penalty"),
        [(-2500.01, 0.0), (-2500, -0.1), (-1500.01, -0.1), (-1500, -0.2)],
    )
    def test_water_depth_bins_read_the_depth_below_sea_level(
        self, elevation, penalty
    ):
        score = self.score(self.probe_gradient(elevation=elevation))

        assert score.value == pytest.approx(1.1 + penalty)
        assert score.missing is False

    @pytest.mark.parametrize("elevation", [0, 120, None])
    def test_an_elevation_at_or_above_sea_level_counts_as_empty(self, elevation):
        score = self.score(self.probe_gradient(elevation=elevation))

        assert score.value == pytest.approx(1.1 - 0.2)
        assert score.missing is True

    @pytest.mark.parametrize(
        ("tilt", "penalty"), [(30.01, -0.2), (30, -0.1), (10.01, -0.1), (10, 0.0)]
    )
    def test_tilt_bins(self, tilt, penalty):
        score = self.score(self.probe_gradient(tilt=tilt))

        assert score.value == pytest.approx(1.1 + penalty)

    def test_a_corrected_tilt_is_waived_even_when_the_tilt_is_empty(self):
        gradient = self.probe_gradient(tilt=None)

        score = self.score(gradient, tilt_corrected=True)

        assert score.value == pytest.approx(1.1)
        assert score.missing is False

    def test_a_corrected_bottom_water_is_waived_even_when_the_elevation_is_empty(
        self,
    ):
        gradient = self.probe_gradient(elevation=None)

        score = self.score(gradient, bottom_water_corrected=True)

        assert score.value == pytest.approx(1.1)
        assert score.missing is False

    def test_a_gradient_without_probe_metadata_has_empty_penetration_and_tilt(self):
        interval = build_interval("probing_offshore", elevation=-3000)
        gradient = build_gradient(interval, number=6)

        score = self.score(gradient)

        # 1.0, +0.1 for six recordings, -0.2 each for the two empty probe inputs.
        assert score.value == pytest.approx(0.7)
        assert score.missing is True

    def test_empty_recordings_take_the_largest_penalty_and_the_mark(self):
        score = self.score(self.probe_gradient(number=None))

        assert score.value == pytest.approx(0.8)
        assert score.missing is True


class TestProbeConductivity:
    def probe_conductivity(self, **fields):
        inputs = dict(
            number=4,
            source=("insitu_probe",),
            location=("actual",),
            method=("probePulse",),
            saturation=("saturatedInSitu",),
            pT=("actualInSitu",),
        )
        inputs.update(fields)
        return build_conductivity(build_interval("probing_offshore"), **inputs)

    def score(self, conductivity):
        from heat_flow.quality import ProbeRules

        return ProbeRules.conductivity(conductivity)

    def test_the_best_inputs_reach_the_top_of_the_scale(self):
        score = self.score(self.probe_conductivity())

        assert score.value == pytest.approx(1.2)
        assert score.missing is False

    @pytest.mark.parametrize(
        ("count", "penalty"), [(4, 0.0), (3, -0.1), (2, -0.1), (1, -0.2)]
    )
    def test_number_bins(self, count, penalty):
        score = self.score(self.probe_conductivity(number=count))

        assert score.value == pytest.approx(1.2 + penalty)

    def test_the_number_is_not_scored_for_a_literature_location(self):
        conductivity = self.probe_conductivity(location=("literature",), number=None)

        score = self.score(conductivity)

        # Location -0.2, the ship saturation case +0.1, pT +0.1. The empty number is not
        # scored at a literature location, so it is not marked either.
        assert score.value == pytest.approx(1.0)
        assert score.missing is False

    @pytest.mark.parametrize("empty", ["saturation", "method", "source", "location"])
    def test_any_empty_saturation_input_takes_the_largest_penalty_and_the_mark(
        self, empty
    ):
        conductivity = self.probe_conductivity(**{empty: ()})

        score = self.score(conductivity)

        assert score.missing is True

    def test_an_empty_saturation_scores_the_largest_saturation_penalty(self):
        score = self.score(self.probe_conductivity(saturation=()))

        # 1.0, location 0, saturation -0.2, number 0, pT +0.1.
        assert score.value == pytest.approx(0.9)

    def test_an_explicit_unspecified_saturation_is_a_value_and_is_not_marked(self):
        # Pulse probe with an unspecified saturation matches no saturation case, which
        # takes the largest penalty without the mark.
        score = self.score(self.probe_conductivity(saturation=("unspecified",)))

        assert score.value == pytest.approx(0.9)
        assert score.missing is False

    def test_the_poorest_of_several_locations_counts(self):
        score = self.score(self.probe_conductivity(location=("actual", "other")))

        assert score.value == pytest.approx(1.1)

    def test_an_actual_in_situ_pT_needs_the_pulse_probe_to_score_well(self):
        conductivity = self.probe_conductivity(method=("lineSourceFull",))

        score = self.score(conductivity)

        # 1.0, saturation -0.2 (saturated in situ with a lab method matches no case),
        # number 0, pT: actual in situ without the pulse probe matches nothing, -0.2.
        assert score.value == pytest.approx(0.6)

    def test_empty_pT_conditions_take_the_largest_penalty_and_the_mark(self):
        score = self.score(self.probe_conductivity(pT=()))

        assert score.value == pytest.approx(1.0 + 0.1 - 0.2)
        assert score.missing is True

    def test_the_probe_conductivity_reads_nothing_from_an_in_situ_correction(self):
        from heat_flow.quality import ProbeRules

        conductivity = self.probe_conductivity()

        assert ProbeRules.conductivity(conductivity, in_situ="not_considered") == (
            ProbeRules.conductivity(conductivity)
        )


class TestBoreholeGradient:
    def borehole_gradient(self, *, number=10, top=("LOGeq",), bottom=("LOGeq",)):
        interval = build_interval("drilling", top=0, bottom=1000)
        return build_gradient(interval, number=number, top=top, bottom=bottom)

    def score(self, gradient):
        from heat_flow.quality import BoreholeRules

        return BoreholeRules.gradient(gradient)

    def test_a_continuous_log_needs_more_than_three_recordings(self):
        # Three recordings is a set of single points, so LOGeq scores -0.1, not +0.1.
        assert self.score(self.borehole_gradient(number=4)).value == pytest.approx(1.1)
        assert self.score(self.borehole_gradient(number=3)).value == pytest.approx(0.9)

    def test_a_continuous_log_with_a_perturbed_method_is_penalised(self):
        gradient = self.borehole_gradient(top=("LOGpert",), bottom=("LOGeq",))

        assert self.score(gradient).value == pytest.approx(0.9)

    def test_a_non_log_method_makes_the_case_single_points(self):
        gradient = self.borehole_gradient(top=("LOGeq",), bottom=("BHT",))

        # Multiple single points: the poorest matching group is BHT at -0.3.
        assert self.score(gradient).value == pytest.approx(0.7)

    @pytest.mark.parametrize(
        ("bottom", "penalty"),
        [("cBHT", -0.3), ("BHT", -0.5), ("CPD", -0.6), ("other", -0.6)],
    )
    def test_the_surface_case_is_decided_by_the_bottom_method_alone(
        self, bottom, penalty
    ):
        gradient = self.borehole_gradient(number=2, top=("SUR",), bottom=(bottom,))

        assert self.score(gradient).value == pytest.approx(1.0 + penalty)
        assert self.score(gradient).missing is False

    @pytest.mark.parametrize(
        ("method", "penalty"),
        [("HT_FT", -0.1), ("HT_FTpert", -0.3)],
    )
    def test_the_misspelt_toolbox_tokens_read_as_the_vocabulary_methods(
        self, method, penalty
    ):
        # HT_FT is the vocabulary's HT-FTeq and HT_FTpert its HT-FTpert.
        gradient = self.borehole_gradient(number=2, top=(method,), bottom=(method,))

        assert self.score(gradient).value == pytest.approx(1.0 + penalty)

    def test_a_method_that_fits_no_case_takes_the_largest_penalty_and_the_mark(self):
        # DTSeq is only a continuous-log method, so with two recordings it fits nothing.
        gradient = self.borehole_gradient(number=2, top=("DTSeq",), bottom=("DTSeq",))

        score = self.score(gradient)

        assert score.value == pytest.approx(0.5)
        assert score.missing is True

    def test_empty_methods_take_the_largest_penalty_and_the_mark(self):
        score = self.score(self.borehole_gradient(top=(), bottom=()))

        assert score.value == pytest.approx(0.5)
        assert score.missing is True

    def test_an_explicit_unspecified_method_is_a_value_and_is_not_marked(self):
        score = self.score(
            self.borehole_gradient(top=("unspecified",), bottom=("unspecified",))
        )

        assert score.value == pytest.approx(0.5)
        assert score.missing is False

    def test_the_poorest_of_several_methods_counts(self):
        gradient = self.borehole_gradient(
            number=2, top=("cBHT", "CPD"), bottom=("cBHT",)
        )

        assert self.score(gradient).value == pytest.approx(0.5)


class TestBoreholeConductivity:
    def borehole_conductivity(self, *, depths=(0, 1000), **fields):
        inputs = dict(
            number=30,
            source=("core_samples",),
            location=("actual",),
            saturation=("saturatedMeasured",),
            pT=("actualInSitu",),
        )
        inputs.update(fields)
        interval = build_interval("drilling", top=depths[0], bottom=depths[1])
        return build_conductivity(interval, **inputs)

    def score(self, conductivity, **kwargs):
        from heat_flow.quality import BoreholeRules

        return BoreholeRules.conductivity(conductivity, **kwargs)

    def test_the_best_uncorrected_inputs_score_one(self):
        score = self.score(self.borehole_conductivity())

        assert score.value == pytest.approx(1.0)
        assert score.missing is False

    @pytest.mark.parametrize("depths", [(0, None), (None, 500)])
    def test_one_reported_depth_passes_the_gate(self, depths):
        score = self.score(self.borehole_conductivity(depths=depths))

        assert score.value == pytest.approx(1.0)

    def test_neither_depth_gives_the_fixed_minimum_and_the_mark(self):
        score = self.score(self.borehole_conductivity(depths=(None, None)))

        assert score.value == pytest.approx(0.1)
        assert score.missing is True

    def test_an_empty_location_takes_the_largest_penalty_and_the_mark(self):
        score = self.score(self.borehole_conductivity(location=()))

        assert score.value == pytest.approx(0.8)
        assert score.missing is True

    @pytest.mark.parametrize(
        ("source", "penalty"),
        [
            ("insitu_probe", 0.1),
            ("core_log", 0.1),
            ("core_samples", 0.0),
            ("cutting_samples", -0.1),
            ("outcrop_samples", -0.1),
            ("well_log", -0.1),
            ("mineral_computation", -0.2),
            ("assumed_from_literature", -0.2),
            ("other", -0.2),
            ("unspecified", -0.2),
        ],
    )
    def test_source_penalties(self, source, penalty):
        score = self.score(self.borehole_conductivity(source=(source,)))

        assert score.value == pytest.approx(1.0 + penalty)
        assert score.missing is False

    def test_an_empty_source_takes_the_largest_penalty_and_the_mark(self):
        score = self.score(self.borehole_conductivity(source=()))

        assert score.value == pytest.approx(0.8)
        assert score.missing is True

    @pytest.mark.parametrize(("count", "penalty"), [(16, 0.0), (15, -0.1)])
    def test_number_bins(self, count, penalty):
        score = self.score(self.borehole_conductivity(number=count))

        assert score.value == pytest.approx(1.0 + penalty)

    def test_an_empty_number_takes_the_largest_penalty_and_the_mark(self):
        score = self.score(self.borehole_conductivity(number=None))

        assert score.value == pytest.approx(0.9)
        assert score.missing is True

    @pytest.mark.parametrize(
        ("saturation", "penalty"),
        [
            ("saturatedInSitu", 0.0),
            ("saturatedMeasured", 0.0),
            ("saturatedCalculated", -0.1),
            ("recovered", -0.1),
            ("dryMeasured", -0.2),
            ("other", -0.2),
            ("unspecified", -0.2),
        ],
    )
    def test_saturation_penalties(self, saturation, penalty):
        score = self.score(self.borehole_conductivity(saturation=(saturation,)))

        assert score.value == pytest.approx(1.0 + penalty)
        assert score.missing is False

    @pytest.mark.parametrize(
        ("pT", "penalty"),
        [
            ("actualInSitu", 0.0),
            ("replicatedPT", 0.0),
            ("correctedPT", 0.0),
            ("replicatedP", -0.1),
            ("replicatedT", -0.1),
            ("correctedP", -0.1),
            ("correctedT", -0.1),
            ("recordedAmbient", -0.2),
            ("unrecordedAmbient", -0.2),
            ("unspecified", -0.2),
        ],
    )
    def test_uncorrected_pT_is_scored_on_its_own_terms(self, pT, penalty):
        score = self.score(self.borehole_conductivity(pT=(pT,)))

        assert score.value == pytest.approx(1.0 + penalty)
        assert score.missing is False

    def test_empty_pT_conditions_take_the_largest_penalty_and_the_mark(self):
        score = self.score(self.borehole_conductivity(pT=()))

        assert score.value == pytest.approx(0.8)
        assert score.missing is True

    def test_the_poorest_of_several_pT_conditions_counts(self):
        score = self.score(
            self.borehole_conductivity(pT=("actualInSitu", "recordedAmbient"))
        )

        assert score.value == pytest.approx(0.8)

    @pytest.mark.parametrize(
        ("pT", "in_situ", "expected", "marked"),
        [
            ("correctedPT", "considered_pt", 1.0, False),
            ("correctedPT", "not_considered", 0.8, False),
            ("correctedT", "considered_t", 0.9, False),
            ("correctedP", "considered_p", 0.9, False),
            ("recordedAmbient", "not_considered", 0.8, False),
            ("recordedAmbient", "-", 0.8, False),
            ("actualInSitu", None, 0.8, True),
        ],
    )
    def test_the_in_situ_keyword_applies_the_agreement_rule(
        self, pT, in_situ, expected, marked
    ):
        conductivity = self.borehole_conductivity(pT=(pT,))

        score = self.score(conductivity, in_situ=in_situ)

        assert score.value == pytest.approx(expected)
        assert score.missing is marked

    def test_empty_pT_with_an_in_situ_correction_is_still_marked(self):
        conductivity = self.borehole_conductivity(pT=())

        score = self.score(conductivity, in_situ="considered_pt")

        assert score.value == pytest.approx(0.8)
        assert score.missing is True


class TestSubScore:
    def test_a_sub_score_is_immutable(self):
        from dataclasses import FrozenInstanceError

        from heat_flow.quality import SubScore

        with pytest.raises(FrozenInstanceError):
            SubScore(value=1.0, missing=False).value = 0.5

    def test_scores_are_rounded_to_three_places(self):
        # Four penalties of -0.1 sum to 0.6000000000000001 in floating point.
        interval = build_interval(
            "probing_offshore", elevation=-1600, penetration=2, tilt=12
        )
        gradient = build_gradient(interval, number=2)

        from heat_flow.quality import ProbeRules

        assert ProbeRules.gradient(gradient).value == 0.6


class TestChoiceLists:
    def test_the_m_score_choices_gain_the_four_marked_classes(self):
        from heat_flow.quality import MScoreOptions

        assert {"M1x", "M2x", "M3x", "M4x", "Mx"} <= set(MScoreOptions.values)

    def test_the_scheme_revision_is_the_toolbox_version(self):
        from heat_flow.quality import SCHEME_REVISION

        assert SCHEME_REVISION == "hfqa_tool 0.2"


class TestCriterion:
    def test_an_empty_mapping_input_is_marked_on_either_route(self):
        # On the probe route the saturation rule also marks an empty location, so the
        # mapping's own mark is only visible when the evaluator is called directly.
        from heat_flow.quality import LOCATION_PENALTIES, Criterion

        penalty, missing = Criterion.mapping(
            frozenset(), LOCATION_PENALTIES, unmatched_missing=False
        )

        assert penalty == -0.2
        assert missing is True

    def test_an_unmatched_mapping_input_is_marked_only_where_the_route_says(self):
        from heat_flow.quality import Criterion

        table = {"actual": 0.0, "literature": -0.2}

        assert Criterion.mapping(
            frozenset({"unknown"}), table, unmatched_missing=False
        ) == (-0.2, False)
        assert Criterion.mapping(
            frozenset({"unknown"}), table, unmatched_missing=True
        ) == (-0.2, True)


class TestUScore:
    @pytest.mark.parametrize(
        ("value", "uncertainty", "expected"),
        [
            (100, 4.9, "U1"),
            (100, 5, "U2"),
            (100, 15, "U2"),
            (100, 15.1, "U3"),
            (100, 25, "U3"),
            (100, 25.1, "U4"),
            (100, 80, "U4"),
        ],
    )
    def test_bands_take_the_upper_bound_into_the_better_class(
        self, value, uncertainty, expected
    ):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.u_score(value, uncertainty) == expected

    @pytest.mark.parametrize(
        ("uncertainty", "expected"),
        [(4.9999996, "U2"), (15.0000004, "U2"), (25.0000004, "U3"), (25.000001, "U4")],
    )
    def test_the_coefficient_is_rounded_to_six_places_before_banding(
        self, uncertainty, expected
    ):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.u_score(100, uncertainty) == expected

    @pytest.mark.parametrize(
        ("value", "uncertainty"),
        [(None, 5), (0, 5), (100, None), (100, 0)],
    )
    def test_an_empty_or_zero_value_or_uncertainty_is_not_determined(
        self, value, uncertainty
    ):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.u_score(value, uncertainty) == "Ux"

    def test_a_negative_value_is_read_as_a_magnitude(self):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.u_score(-40, 12) == "U4"
        assert QualityScheme.u_score(40, -1.9) == "U1"


class TestMScore:
    @pytest.mark.parametrize(
        ("t", "tc", "expected"),
        [
            (1.0, 0.76, "M1"),
            (1.0, 0.75, "M1"),
            (1.0, 0.74, "M2"),
            (1.0, 0.5, "M2"),
            (1.0, 0.49, "M3"),
            (0.5, 0.5, "M3"),
            (0.5, 0.49, "M4"),
            (0.1, 0.1, "M4"),
        ],
    )
    def test_classes_take_a_boundary_product_into_the_better_class(
        self, t, tc, expected
    ):
        from heat_flow.quality import QualityScheme, SubScore

        assert QualityScheme.m_score(SubScore(t), SubScore(tc)) == expected

    def test_the_product_is_rounded_to_three_places_before_it_is_classed(self):
        from heat_flow.quality import QualityScheme, SubScore

        # 0.833 x 0.9 is 0.7497, which the toolbox rounds up to the M1 boundary.
        assert QualityScheme.m_score(SubScore(0.833), SubScore(0.9)) == "M1"

    @pytest.mark.parametrize("marked", ["t", "tc", "both"])
    def test_either_marked_sub_score_adds_the_x_suffix(self, marked):
        from heat_flow.quality import QualityScheme, SubScore

        t = SubScore(0.9, marked in {"t", "both"})
        tc = SubScore(0.9, marked in {"tc", "both"})

        assert QualityScheme.m_score(t, tc) == "M1x"

    def test_a_sub_score_that_cannot_be_calculated_gives_mx(self):
        from heat_flow.quality import QualityScheme, SubScore

        assert QualityScheme.m_score(SubScore(None), SubScore(0.9)) == "Mx"
        assert QualityScheme.m_score(SubScore(0.9), SubScore(None)) == "Mx"
        assert QualityScheme.m_score(SubScore(None, True), SubScore(None)) == "Mx"


class TestPerturbationFlags:
    ORDER = ["S", "E", "TOPO", "PAL", "SUR", "CONV", "HR"]

    def test_no_corrections_give_seven_dashes(self):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.perturbation_flags({}) == "-------"

    @pytest.mark.parametrize(
        ("status", "upper"),
        [
            ("present_corrected", True),
            ("present_not_corrected", False),
        ],
    )
    @pytest.mark.parametrize(
        ("correction", "letter", "position"),
        [
            ("S", "S", 0),
            ("E", "E", 1),
            ("TOPO", "T", 2),
            ("PAL", "P", 3),
            ("SUR", "V", 4),
            ("CONV", "C", 5),
            ("HR", "R", 6),
        ],
    )
    def test_each_correction_writes_its_own_letter_in_its_own_place(
        self, correction, letter, position, status, upper
    ):
        from heat_flow.quality import QualityScheme

        flags = QualityScheme.perturbation_flags({correction: status})

        expected = letter if upper else letter.lower()
        assert flags == "-" * position + expected + "-" * (6 - position)

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            ("present_not_significant", "X"),
            ("not_recognized", "x"),
            ("-", "-"),
            ("not_considered", "-"),
            ("considered_pt", "-"),
            ("tilt_corrected", "-"),
            ("", "-"),
        ],
    )
    def test_the_remaining_statuses(self, status, expected):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.perturbation_flags({"PAL": status}) == "---" + expected + "---"

    def test_the_in_situ_and_temperature_corrections_write_no_flag(self):
        from heat_flow.quality import QualityScheme

        flags = QualityScheme.perturbation_flags(
            {"IS": "present_corrected", "T": "present_corrected"}
        )

        assert flags == "-------"


class TestQualityCode:
    def test_the_code_joins_u_m_and_flags_with_dots(self):
        from heat_flow.quality import QualityScheme

        assert QualityScheme.code("U1", "M2", "SxxxCxR") == "U1.M2.SxxxCxR"

    def test_a_marked_m_score_makes_the_longest_code_fourteen_characters(self):
        from heat_flow.quality import QualityScheme

        code = QualityScheme.code("U2", "M3x", "-e-PX--")

        assert code == "U2.M3x.-e-PX--"
        assert len(code) == 14


# Per R3 case: the child's value and uncertainty, its corrections by type, and the
# toolbox's U, M and flags. T and TC come from the conformance case of the same name.
SCHEME_EXPECTATIONS = {
    "X1-continuous-eq": (None, None, {}, "Ux", "M1x", "-------"),
    "X2-continuous-pert": (None, None, {}, "Ux", "M2x", "-------"),
    "X3-multiple-single-points": (None, None, {}, "Ux", "M3x", "-------"),
    "X4-single-point-plus-surface": (None, None, {}, "Ux", "M4x", "-------"),
    "X5-interval-gate": (None, None, {}, "Ux", "M4x", "-------"),
    "P1-probe-with-waivers": (
        80,
        4,
        {
            "S": "present_corrected",
            "E": "present_not_corrected",
            "TOPO": "present_not_significant",
            "PAL": "not_recognized",
            "SUR": "present_corrected",
            "CONV": "-",
        },
        "U2",
        "M1",
        "SeXxV--",
    ),
    "P2-probe-without-corrections": (80, 4, {}, "U2", "M1", "-------"),
    "P3-onshore-lab": (60, 9, {}, "U2", "M4x", "-------"),
    "P4-clustering-literature": (-40, 12, {}, "U4", "M4", "-------"),
    "P5-no-saturation": (100, 30, {}, "U4", "M3x", "-------"),
    "B1-agreeing-in-situ": (65, 3, {}, "U1", "M1", "-------"),
    "B2-not-considered": (65, 3, {}, "U1", "M1", "-------"),
    "B3-no-in-situ-correction": (65, 3, {}, "U1", "M1x", "-------"),
    "B4-mining-ambient": (65, 3, {}, "U1", "M1", "-------"),
    "B5-drilling-clustering": (50, 10, {}, "U3", "M3", "-------"),
    "B6-tunnelling-literature": (90, 20, {}, "U3", "M4", "-------"),
    "B7-unresolvable-surface-case": (90, 0, {}, "Ux", "M3x", "-------"),
    "B8-indirect-no-methods": (70, None, {}, "Ux", "M4x", "-------"),
    "B9-everything-unspecified": (70, 7, {}, "U2", "M4", "-------"),
}


class TestSchemeConformance:
    """The U-score, M-score and flags against the toolbox's own (research R3)."""

    @pytest.mark.parametrize("inputs", CONFORMANCE_CASES)
    def test_u_m_and_flags_equal_the_toolbox_output(self, inputs, request):
        from heat_flow.quality import UNCORRECTED, QualityScheme, route

        name = request.node.callspec.id
        value, uncertainty, statuses, u, m, flags = SCHEME_EXPECTATIONS[name]
        site, gradient, conductivity = build_case(inputs)
        rules = route(site)
        t = rules.gradient(
            gradient,
            tilt_corrected=inputs.get("tilt_corrected", False),
            bottom_water_corrected=inputs.get("bottom_water_corrected", False),
        )
        tc = rules.conductivity(
            conductivity, in_situ=inputs.get("in_situ", UNCORRECTED)
        )

        assert QualityScheme.u_score(value, uncertainty) == u
        assert QualityScheme.m_score(t, tc) == m
        assert QualityScheme.perturbation_flags(statuses) == flags
