"""Heat flow quality scheme, following the Heat Flow Quality Analysis Toolbox V0.2.

The toolbox (hfqa_tool, Dergunova et al. 2026) is the version of the scheme that scored the
2024 GHFDB release. It refines the scheme of Fuchs et al. (2023), and where the two differ the
toolbox's code is the definition. ``docs/guides/quality-scores.md`` explains each place where
the portal had to choose.

A measurement is scored by the rules of the route its site's exploration method selects:
probe sensing or borehole and mine. Each route scores a thermal gradient (the T-score) and a
thermal conductivity (the TC-score), starting from 1.0 and adding a penalty per criterion.
"""

import operator
from dataclasses import dataclass

from django.db import models
from django.utils.translation import gettext_lazy as _

SCHEME_REVISION = "hfqa_tool 0.2"

# Stands for "score without reading anything from a child". It is not None, which means the
# child records no in-situ correction at all.
UNCORRECTED = object()

# Conductivity location, shared by both routes.
LOCATION_PENALTIES = {"actual": 0.0, "other": -0.1, "literature": -0.2}

LAB_METHODS = frozenset(
    {
        "pointSource",
        "lineSourceFull",
        "lineSourceHalf",
        "planeSourceFull",
        "planeSourceHalf",
        "laboratoryOther",
    }
)


class UScoreOptions(models.TextChoices):
    """Quality grades for a heat flow measurement's U-score (uncertainty)."""

    U1 = "U1", _("Excellent")
    U2 = "U2", _("Good")
    U3 = "U3", _("Acceptable")
    U4 = "U4", _("Poor")
    Ux = "Ux", _("Not determined / missing data")


class MScoreOptions(models.TextChoices):
    """Quality grades for a heat flow measurement's M-score (methodology).

    A trailing ``x`` marks a grade reached with missing information.
    """

    M1 = "M1", _("Excellent")
    M2 = "M2", _("Good")
    M3 = "M3", _("Acceptable")
    M4 = "M4", _("Poor")
    M1x = "M1x", _("Excellent, with missing information")
    M2x = "M2x", _("Good, with missing information")
    M3x = "M3x", _("Acceptable, with missing information")
    M4x = "M4x", _("Poor, with missing information")
    Mx = "Mx", _("Not determined / missing data")


@dataclass(frozen=True)
class SubScore:
    """A T-score or TC-score and whether it was reached with missing information.

    Attributes:
        value: The score, or ``None`` when it is not determined.
        missing: True when an input the scheme needed was empty.
    """

    value: float | None
    missing: bool = False

    @classmethod
    def from_penalties(cls, penalties: list[tuple[float, bool]]) -> "SubScore":
        """Add the penalties of every criterion to the starting score of 1.0.

        Args:
            penalties: One ``(penalty, missing)`` pair per criterion.

        Returns:
            The score rounded to three places, marked when any criterion was.
        """
        total = 1.0 + sum(penalty for penalty, _missing in penalties)
        return cls(round(total, 3), any(missing for _penalty, missing in penalties))


class Reading:
    """Reads what the scheme needs from a measurement, its interval and its site."""

    @staticmethod
    def concepts(manager) -> frozenset[str]:
        """Return the identifiers of every concept in a vocabulary field."""
        return frozenset(concept.name for concept in manager.all())

    @staticmethod
    def magnitude(quantity, unit: str) -> float | None:
        """Return a quantity as a number in *unit*, or ``None`` when it is empty.

        A record that has not been reloaded holds the plain number that was assigned, which
        is already in the field's base unit.
        """
        if quantity is None:
            return None
        if hasattr(quantity, "to"):
            return float(quantity.to(unit).magnitude)
        return float(quantity)

    @staticmethod
    def site(measurement):
        """Return the site of the measurement's interval, or ``None``."""
        return getattr(measurement.sample, "site", None)

    @staticmethod
    def probe_metadata(measurement):
        """Return the probe metadata of the measurement's interval, or ``None``."""
        return getattr(measurement.sample, "probe_metadata", None)


class Criterion:
    """Evaluators shared by both routes.

    Each returns ``(penalty, missing)``. An empty input takes the criterion's largest penalty
    with the mark, and an explicit ``unspecified`` concept is a value, never empty (FR-009).
    A multi-valued field contributes every concept and the poorest matching penalty wins.
    """

    OPERATORS = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
    }

    @classmethod
    def bins(cls, value: float | None, bins) -> tuple[float, bool]:
        """Score a number against ``(operator, threshold, penalty)`` bins.

        Bins are tried in the order given, which is the largest threshold first. A number
        that fits no bin takes the largest penalty without the mark.
        """
        worst = min(penalty for _op, _threshold, penalty in bins)
        if value is None:
            return worst, True
        for op, threshold, penalty in bins:
            if cls.OPERATORS[op](value, threshold):
                return penalty, False
        return worst, False

    @staticmethod
    def mapping(
        concepts: frozenset[str], table: dict[str, float], *, unmatched_missing: bool
    ) -> tuple[float, bool]:
        """Score a vocabulary field by the poorest of its concepts found in *table*.

        Args:
            concepts: The concept identifiers held by the field.
            table: Penalty per concept identifier.
            unmatched_missing: Whether a field that matches nothing carries the mark. An empty
                field always does.
        """
        matched = [table[name] for name in concepts if name in table]
        if matched:
            return min(matched), False
        return min(table.values()), unmatched_missing or not concepts

    @staticmethod
    def cases(
        cases, fields: dict[str, frozenset[str]], *, fallback: float | None = None
    ) -> tuple[float, bool]:
        """Score fields against ``(penalty, conditions)`` cases.

        Every field a case names is checked for emptiness first, and any empty one takes the
        largest penalty with the mark. Otherwise every case whose conditions all hold counts
        (a condition holds when the field holds any of its concepts) and the poorest wins.
        With no match, *fallback* applies if given, else the largest penalty, unmarked.
        """
        penalties = [penalty for penalty, _when in cases]
        if fallback is not None:
            penalties.append(fallback)
        worst = min(penalties)
        named = {field for _penalty, when in cases for field in when}
        if any(not fields[field] for field in named):
            return worst, True
        matched = [
            penalty
            for penalty, when in cases
            if all(fields[field] & names for field, names in when.items())
        ]
        if matched:
            return min(matched), False
        return (worst if fallback is None else fallback), False

    @staticmethod
    def depth_reported(interval) -> bool:
        """Return whether the interval reports a top or a bottom depth."""
        return interval.top is not None or interval.bottom is not None


class ProbeRules:
    """Scores for a site explored by probe sensing (toolbox ``marine_logic``)."""

    PENETRATION = (
        (">", 10.0, 0.1),
        (">", 3.0, 0.0),
        (">", 1.0, -0.1),
        ("<=", 1.0, -0.2),
    )
    RECORDINGS = ((">", 5, 0.1), (">=", 3, 0.0), ("==", 2, -0.1), ("<", 2, -0.2))
    WATER_DEPTH = ((">", 2500.0, 0.0), (">", 1500.0, -0.1), ("<=", 1500.0, -0.2))
    TILT = ((">", 30.0, -0.2), (">", 10.0, -0.1), (">=", 0.0, 0.0))
    COUNT = ((">", 3, 0.0), (">=", 2, -0.1), ("<", 2, -0.2))

    # One entry per toolbox case: its penalty and, per field, the concepts that satisfy it.
    # A field a case names is required by every case of the block, so an empty one marks.
    SATURATION = (
        (
            0.1,
            {
                "saturation": {"saturatedInSitu"},
                "method": {"probePulse"},
                "source": {"insitu_probe"},
            },
        ),
        (
            0.0,
            {
                "saturation": {"recovered", "saturatedMeasured"},
                "method": {"probePulse"},
                "source": {"insitu_probe"},
            },
        ),
        (
            0.0,
            {
                "saturation": {"recovered", "saturatedMeasured"},
                "method": LAB_METHODS,
            },
        ),
        (-0.1, {"saturation": {"saturatedCalculated"}, "method": LAB_METHODS}),
        (
            -0.2,
            {
                "saturation": {"dryMeasured", "unspecified", "other"},
                "method": LAB_METHODS,
            },
        ),
        (
            -0.1,
            {
                "method": {"lithology", "wellLogDeterministic", "wellLogEmpirical"},
                "location": {"literature"},
            },
        ),
        (
            -0.2,
            {
                "method": {
                    "waterContent",
                    "mineralComposition",
                    "chlorineContent",
                    "unspecified",
                }
            },
        ),
    )
    PT_CONDITIONS = (
        (0.1, {"pT": {"actualInSitu"}, "method": {"probePulse"}}),
        (0.0, {"pT": {"replicatedPT", "correctedPT"}}),
        (-0.1, {"pT": {"replicatedP", "correctedP", "replicatedT", "correctedT"}}),
        (-0.2, {"pT": {"recordedAmbient", "unrecordedAmbient", "unspecified"}}),
    )

    @classmethod
    def gradient(
        cls, gradient, *, tilt_corrected=False, bottom_water_corrected=False
    ) -> SubScore:
        """Score a thermal gradient measured by probe sensing (the T-score).

        Args:
            gradient: The ``ThermalGradient``.
            tilt_corrected: Waives the tilt criterion, for a child whose temperature
                correction is recorded as tilt corrected.
            bottom_water_corrected: Waives the water depth criterion, for a child whose
                surface and bottom-water correction is present and corrected.

        Returns:
            The gradient's T-score.
        """
        probe = Reading.probe_metadata(gradient)
        elevation = Reading.magnitude(
            getattr(Reading.site(gradient), "elevation", None), "m"
        )
        penetration = Reading.magnitude(getattr(probe, "penetration", None), "m")
        tilt = Reading.magnitude(getattr(probe, "tilt", None), "degree")

        # Sea level or above cannot be a water depth, so it counts as not recorded.
        depth = -elevation if elevation is not None and elevation < 0 else None
        penalties = [
            Criterion.bins(penetration, cls.PENETRATION),
            Criterion.bins(gradient.number, cls.RECORDINGS),
        ]
        if not bottom_water_corrected:
            penalties.append(Criterion.bins(depth, cls.WATER_DEPTH))
        if not tilt_corrected:
            penalties.append(Criterion.bins(tilt, cls.TILT))
        return SubScore.from_penalties(penalties)

    @classmethod
    def conductivity(cls, conductivity, *, in_situ=UNCORRECTED) -> SubScore:
        """Score a thermal conductivity determined by probe sensing (the TC-score).

        Args:
            conductivity: The ``IntervalConductivity``.
            in_situ: Ignored. The probe route reads nothing from the child.

        Returns:
            The conductivity's TC-score.
        """
        fields = {
            "source": Reading.concepts(conductivity.source),
            "location": Reading.concepts(conductivity.location),
            "method": Reading.concepts(conductivity.method),
            "saturation": Reading.concepts(conductivity.saturation),
            "pT": Reading.concepts(conductivity.pT_conditions),
        }
        penalties = [
            Criterion.mapping(
                fields["location"], LOCATION_PENALTIES, unmatched_missing=False
            ),
            Criterion.cases(cls.SATURATION, fields),
        ]
        if "literature" not in fields["location"]:
            penalties.append(Criterion.bins(conductivity.number, cls.COUNT))
        penalties.append(Criterion.cases(cls.PT_CONDITIONS, fields))
        return SubScore.from_penalties(penalties)


class BoreholeRules:
    """Scores for a site explored by drilling, mining, tunnelling or indirect methods."""

    GATE_SCORE = 0.1

    # Temperature method groups. HT_FT and HT_FTpert are the vocabulary's HT-FTeq and
    # HT-FTpert, which the toolbox's lists misspell.
    CONTINUOUS = (
        (0.1, frozenset({"LOGeq", "cLOG", "DTSeq", "cDTS"})),
        (-0.1, frozenset({"LOGpert"})),
    )
    SINGLE_POINTS = (
        (
            -0.1,
            frozenset(
                {
                    "LOGeq",
                    "cLOG",
                    "cBHT",
                    "HT_FT",
                    "cHT_FT",
                    "RTDeq",
                    "cRTD",
                    "ODTT_PC",
                    "ODTT_TP",
                    "EGRT",
                    "GRT",
                    "cDTS",
                }
            ),
        ),
        (
            -0.3,
            frozenset({"LOGpert", "DTSpert", "BHT", "HT_FTpert", "RTDpert", "BLK"}),
        ),
        (-0.5, frozenset({"CPD", "XEN", "GTM", "BSR", "unspecified", "other"})),
    )
    SURFACE_PLUS_ONE_POINT = (
        (
            -0.3,
            frozenset(
                {
                    "cBHT",
                    "RTDeq",
                    "cRTD",
                    "ODTT_PC",
                    "ODTT_TP",
                    "cHT_FT",
                    "EGRT",
                    "GRT",
                }
            ),
        ),
        (-0.5, frozenset({"BHT", "HT_FTpert", "RTDpert"})),
        (-0.6, frozenset({"CPD", "XEN", "GTM", "BSR", "unspecified", "other"})),
    )

    COUNT = ((">", 15, 0.0), ("<=", 15, -0.1))
    SOURCE = (
        (0.1, {"source": {"insitu_probe", "core_log"}}),
        (0.0, {"source": {"core_samples"}}),
        (-0.1, {"source": {"cutting_samples", "outcrop_samples", "well_log"}}),
        (
            -0.2,
            {
                "source": {
                    "mineral_computation",
                    "assumed_from_literature",
                    "unspecified",
                    "other",
                }
            },
        ),
    )
    SATURATION = (
        (0.0, {"saturation": {"saturatedMeasured", "saturatedInSitu"}}),
        (-0.1, {"saturation": {"saturatedCalculated", "recovered"}}),
        (-0.2, {"saturation": {"dryMeasured", "unspecified", "other"}}),
    )
    # The paper's Table 3, reading the pT conditions on their own terms.
    PT_UNCORRECTED = (
        (0.0, {"pT": {"actualInSitu", "replicatedPT", "correctedPT"}}),
        (
            -0.1,
            {"pT": {"replicatedP", "replicatedT", "correctedP", "correctedT"}},
        ),
        (-0.2, {"pT": {"recordedAmbient", "unrecordedAmbient", "unspecified"}}),
    )
    # The toolbox's case list: the pT conditions must agree with the in-situ correction.
    PT_CORRECTED = (
        (
            0.0,
            {
                "pT": {"actualInSitu", "replicatedPT", "correctedPT"},
                "in_situ": {"considered_pt"},
            },
        ),
        (
            -0.1,
            {
                "pT": {"replicatedP", "correctedP", "replicatedT", "correctedT"},
                "in_situ": {"considered_p", "considered_t"},
            },
        ),
        (
            -0.2,
            {
                "pT": {"recordedAmbient", "unrecordedAmbient", "unspecified"},
                "in_situ": {"not_considered", "-"},
            },
        ),
    )
    PT_FALLBACK = -0.2

    @classmethod
    def gradient(cls, gradient, **_corrections) -> SubScore:
        """Score a thermal gradient from a borehole or mine (the T-score).

        Args:
            gradient: The ``ThermalGradient``.
            **_corrections: Ignored. The borehole route reads no correction for the gradient.

        Returns:
            The gradient's T-score.
        """
        top = Reading.concepts(gradient.method_top)
        bottom = Reading.concepts(gradient.method_bottom)
        if "SUR" in top:
            return SubScore.from_penalties(
                [cls.method_penalty(cls.SURFACE_PLUS_ONE_POINT, bottom)]
            )
        continuous = {name for _penalty, names in cls.CONTINUOUS for name in names}
        if (
            gradient.number is not None
            and gradient.number > 3
            and (top | bottom)
            and (top | bottom) <= continuous
        ):
            return SubScore.from_penalties(
                [cls.method_penalty(cls.CONTINUOUS, top | bottom)]
            )
        return SubScore.from_penalties(
            [cls.method_penalty(cls.SINGLE_POINTS, top | bottom)]
        )

    @staticmethod
    def method_penalty(groups, methods: frozenset[str]) -> tuple[float, bool]:
        """Return the poorest matching group's penalty for *methods*.

        A set of methods that fits no group takes the case's largest penalty with the mark.
        """
        matched = [penalty for penalty, names in groups if methods & names]
        if matched:
            return min(matched), False
        return min(penalty for penalty, _names in groups), True

    @classmethod
    def conductivity(cls, conductivity, *, in_situ=UNCORRECTED) -> SubScore:
        """Score a thermal conductivity from a borehole or mine (the TC-score).

        Args:
            conductivity: The ``IntervalConductivity``.
            in_situ: By default the pT conditions are scored on their own terms. Pass the
                status of the child's in-situ correction, or ``None`` when it records none,
                to apply the toolbox's agreement rule.

        Returns:
            The conductivity's TC-score.
        """
        if not Criterion.depth_reported(conductivity.sample):
            return SubScore(cls.GATE_SCORE, True)
        fields = {
            "source": Reading.concepts(conductivity.source),
            "location": Reading.concepts(conductivity.location),
            "saturation": Reading.concepts(conductivity.saturation),
            "pT": Reading.concepts(conductivity.pT_conditions),
        }
        penalties = [
            Criterion.mapping(
                fields["location"], LOCATION_PENALTIES, unmatched_missing=True
            ),
            Criterion.cases(cls.SOURCE, fields),
        ]
        if "literature" not in fields["location"]:
            penalties.append(Criterion.bins(conductivity.number, cls.COUNT))
        penalties.append(Criterion.cases(cls.SATURATION, fields))
        if in_situ is UNCORRECTED:
            penalties.append(Criterion.cases(cls.PT_UNCORRECTED, fields))
        else:
            fields["in_situ"] = frozenset() if in_situ is None else frozenset({in_situ})
            penalties.append(
                Criterion.cases(cls.PT_CORRECTED, fields, fallback=cls.PT_FALLBACK)
            )
        return SubScore.from_penalties(penalties)


# Exploration method concept to the route it selects.
ROUTES: dict[str, type[ProbeRules] | type[BoreholeRules]] = {
    "probing_onshore": ProbeRules,
    "probing_offshore": ProbeRules,
    "probing_clustering": ProbeRules,
    "drilling": BoreholeRules,
    "drilling_clustering": BoreholeRules,
    "mining": BoreholeRules,
    "tunneling": BoreholeRules,
    "indirect": BoreholeRules,
}


def route(site) -> type[ProbeRules] | type[BoreholeRules] | None:
    """Return the rules a site's exploration method selects.

    Args:
        site: The ``HeatFlowSite`` a measurement belongs to, or ``None``.

    Returns:
        ``ProbeRules`` or ``BoreholeRules``, or ``None`` when the method is other,
        unspecified or empty, which leaves the measurement's score not determined.
    """
    method = getattr(site, "explo_method", None)
    return None if method is None else ROUTES.get(method)
