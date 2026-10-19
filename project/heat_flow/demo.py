"""Generate a dataset's worth of valid, realistic heat flow records for development.

``DemoGraph`` builds sites, parents, children and everything beneath them with the values
and proportions of the published database. Scores are never generated: the caller wraps the
build in ``Recalculation.deferred()`` and the portal computes them (FS-008).
"""

import math
import random
from collections.abc import Callable
from decimal import Decimal
from typing import Any, NamedTuple

from django.core.exceptions import ValidationError

from .models import (
    HeatFlow,
    HeatFlowCorrection,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ProbeMetadata,
    ThermalGradient,
)

SITES_PER_DATASET = 20
CHILDREN_CYCLE = (1, 2, 3, 4)
MAX_PLACEMENT_ATTEMPTS = 10


class Region(NamedTuple):
    """A box of the globe where heat flow is measured.

    Attributes:
        name: A readable label.
        min_lat: Southern edge in decimal degrees.
        max_lat: Northern edge in decimal degrees.
        min_lon: Western edge in decimal degrees.
        max_lon: Eastern edge in decimal degrees.
        marine: Whether the box is at sea.
        environment: A value of the site's geographic environment vocabulary.
        explo_method: A value of the site's exploration method vocabulary, which selects
            the probe or the borehole quality rules.
    """

    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    marine: bool
    environment: str
    explo_method: str


def _land(name: str, lat: tuple[float, float], lon: tuple[float, float]) -> Region:
    return Region(name, *lat, *lon, False, "onshore_continental", "drilling")


def _sea(name: str, lat: tuple[float, float], lon: tuple[float, float]) -> Region:
    return Region(name, *lat, *lon, True, "offshore_marine", "probing_offshore")


REGIONS = (
    _land("Western North America", (34.0, 48.0), (-122.0, -108.0)),
    _land("Eastern North America", (35.0, 46.0), (-90.0, -75.0)),
    _land("Canadian Shield", (48.0, 58.0), (-100.0, -80.0)),
    _land("Central Europe", (46.0, 54.0), (5.0, 20.0)),
    _land("Scandinavia", (58.0, 66.0), (8.0, 28.0)),
    _land("Iberia", (37.0, 43.0), (-8.0, 0.0)),
    _land("Tibetan Plateau", (28.0, 36.0), (80.0, 98.0)),
    _land("North China", (34.0, 42.0), (108.0, 120.0)),
    _land("India", (12.0, 26.0), (74.0, 86.0)),
    _land("East African Rift", (-10.0, 8.0), (30.0, 40.0)),
    _land("Southern Africa", (-33.0, -20.0), (18.0, 30.0)),
    _land("Eastern Australia", (-37.0, -22.0), (140.0, 152.0)),
    _sea("North Sea", (54.0, 60.0), (0.0, 6.0)),
    _sea("Gulf of Mexico", (24.0, 28.0), (-94.0, -86.0)),
    _sea("Cascadia margin", (42.0, 48.0), (-127.0, -124.0)),
    _sea("Japan Trench", (36.0, 40.0), (143.0, 146.0)),
    _sea("Mid-Atlantic Ridge flank", (20.0, 30.0), (-48.0, -40.0)),
    _sea("East Pacific Rise flank", (-10.0, 0.0), (-110.0, -100.0)),
    _sea("Mediterranean basin", (34.0, 38.0), (14.0, 24.0)),
    _sea("South China Sea", (10.0, 18.0), (112.0, 118.0)),
)

#: Corrections a child may carry, in a fixed order so a seeded build repeats.
CORRECTION_TYPES = tuple(HeatFlowCorrection.CorrectionTypeChoices.values)


class DemoGraph:
    """Builds the heat flow records of one dataset.

    Sites, intervals, parents, children, gradients and conductivities are multi-table models
    that Django cannot bulk-insert, so they are saved one at a time. Corrections, probe
    metadata and the concept rows are collected and written in bulk when ``build`` ends.
    """

    def __init__(
        self,
        dataset: Any,
        rng: random.Random,
        next_ghfdb_id: Callable[[], int] | None = None,
    ) -> None:
        """Prepare a build into *dataset*.

        Args:
            dataset: The dataset every record is created in.
            rng: The source of every random draw.
            next_ghfdb_id: Returns the next published identifier, or ``None`` for an
                unpublished dataset, whose records carry no identifier.
        """
        self.dataset = dataset
        self.rng = rng
        self.next_ghfdb_id = next_ghfdb_id
        self._label_count = 0
        self._corrections: list[HeatFlowCorrection] = []
        self._probes: list[ProbeMetadata] = []
        self._concept_rows: list[tuple[Any, str, int]] = []
        self._concepts: dict[Any, list[int]] = {}

    def build(self, sites: int = SITES_PER_DATASET) -> None:
        """Create *sites* sites with their parents, children and everything beneath them.

        Args:
            sites: The number of sites. Children per site follow ``CHILDREN_CYCLE``.

        Raises:
            ValidationError: No free point was found for a site.
        """
        for position in range(sites):
            self._build_site(CHILDREN_CYCLE[position % len(CHILDREN_CYCLE)])
        self._write_bulk()

    def _label(self) -> str:
        self._label_count += 1
        return f"DEMO-{self.dataset.pk}-{self._label_count}"

    def _published_id(self) -> int | None:
        return None if self.next_ghfdb_id is None else self.next_ghfdb_id()

    def _round(self, value: float, places: int = 2) -> float:
        return round(value, places)

    def _uncertainty(self, value: float) -> float:
        return self._round(abs(value) * self.rng.uniform(0.05, 0.25))

    def _place_site(self) -> tuple[HeatFlowSite, Region]:
        """Create a site at a point no other site holds.

        Returns:
            The site and the region it was drawn in.

        Raises:
            ValidationError: Every one of ``MAX_PLACEMENT_ATTEMPTS`` points was taken.
        """
        for attempt in range(MAX_PLACEMENT_ATTEMPTS):
            region = self.rng.choice(REGIONS)
            latitude = self._round(self.rng.uniform(region.min_lat, region.max_lat), 5)
            longitude = self._round(self.rng.uniform(region.min_lon, region.max_lon), 5)
            label = self._label()
            try:
                site = HeatFlowSite.objects.create(
                    dataset=self.dataset,
                    name=label,
                    local_id=label,
                    location=HeatFlowSite.point_at(latitude, longitude),
                    type="ocean" if region.marine else "land",
                    elevation=self._elevation(region),
                    environment=region.environment,
                    explo_method=region.explo_method,
                )
            except ValidationError:
                if attempt == MAX_PLACEMENT_ATTEMPTS - 1:
                    raise
                continue
            self._add_concepts(site, "explo_purpose")
            return site, region
        raise AssertionError("unreachable")  # pragma: no cover

    def _elevation(self, region: Region) -> float:
        low, high = (-6000, -200) if region.marine else (0, 3000)
        return self._round(self.rng.uniform(low, high), 1)

    def _plan_child(self, region: Region) -> dict[str, float]:
        """Draw one child's values so that its heat flow is its gradient times its conductivity."""
        rng = self.rng
        conductivity = self._round(
            min(max(rng.lognormvariate(math.log(2.5), 0.3), 0.8), 6)
        )
        target = min(
            max(rng.lognormvariate(math.log(95 if region.marine else 65), 0.4), 15), 400
        )
        gradient = self._round(min(max(target / conductivity, 5), 300))
        return {
            "conductivity": conductivity,
            "gradient": gradient,
            "value": self._round(gradient * conductivity),
        }

    def _build_site(self, child_count: int) -> None:
        site, region = self._place_site()
        plans = [self._plan_child(region) for _ in range(child_count)]
        relevant = [True] * child_count
        if child_count >= 3:
            relevant[-1] = False
        used = [
            plan["value"] for plan, flag in zip(plans, relevant, strict=True) if flag
        ]
        parent_value = self._round(sum(used) / len(used))

        parent = ParentHeatFlow.objects.create(
            dataset=self.dataset,
            name=self._label(),
            sample=site,
            value=parent_value,
            uncertainty=self._uncertainty(parent_value),
            ghfdb_id=self._published_id(),
        )
        for plan, flag in zip(plans, relevant, strict=True):
            self._build_child(site, region, parent, plan, flag)

    def _build_child(
        self,
        site: HeatFlowSite,
        region: Region,
        parent: ParentHeatFlow,
        plan: dict[str, float],
        is_relevant: bool,
    ) -> None:
        rng = self.rng
        dataset = self.dataset
        if region.marine:
            top, bottom = 0.0, self._round(rng.uniform(2, 10), 1)
        else:
            top = self._round(rng.uniform(0, 1500), 1)
            bottom = self._round(top + rng.uniform(50, 1500), 1)

        interval = HeatFlowInterval.objects.create(
            dataset=dataset, name=self._label(), site=site, top=top, bottom=bottom
        )
        gradient_value = plan["gradient"]
        corrected = self._round(gradient_value * rng.uniform(0.95, 1.1))
        gradient = ThermalGradient.objects.create(
            dataset=dataset,
            name=self._label(),
            sample=interval,
            value=gradient_value,
            uncertainty=self._uncertainty(gradient_value),
            corrected_value=corrected,
            corrected_uncertainty=self._uncertainty(corrected),
            number=rng.randint(2, 60),
            **({} if region.marine else {"shutin_bottom": rng.randint(6, 200)}),
        )
        for field in (
            "method_top",
            "method_bottom",
            "correction_top",
            "correction_bottom",
        ):
            self._add_concepts(gradient, field)

        conductivity = IntervalConductivity.objects.create(
            dataset=dataset,
            name=self._label(),
            sample=interval,
            value=plan["conductivity"],
            uncertainty=self._uncertainty(plan["conductivity"]),
            number=rng.randint(1, 50),
        )
        for field in (
            "source",
            "conductivity_location",
            "method",
            "saturation",
            "pT_conditions",
            "pT_function",
            "strategy",
        ):
            self._add_concepts(conductivity, field)

        child = HeatFlow.objects.create(
            dataset=dataset,
            name=self._label(),
            sample=interval,
            value=plan["value"],
            uncertainty=self._uncertainty(plan["value"]),
            thermal_gradient=gradient,
            thermal_conductivity=conductivity,
            parent=parent,
            is_relevant=is_relevant,
            ghfdb_id=self._published_id(),
            **({"expedition": "RV Demo Explorer"} if region.marine else {}),
        )
        self._add_concepts(child, "method")
        self._collect_corrections(child, region.marine)
        if region.marine:
            self._collect_probe(interval)

    def _collect_corrections(self, child: HeatFlow, probed: bool) -> None:
        """Queue valid corrections for *child*, always a temperature one on a probe."""
        types = set(self.rng.sample(CORRECTION_TYPES, self.rng.randint(0, 3)))
        if probed:
            types.add("T")
        for correction_type in CORRECTION_TYPES:
            if correction_type not in types:
                continue
            valid = HeatFlowCorrection.VALID_STATUS_FOR_TYPE.get(
                correction_type, HeatFlowCorrection.ENVIRONMENTAL_VALID
            )
            self._corrections.append(
                HeatFlowCorrection(
                    heat_flow=child,
                    correction_type=correction_type,
                    status=self.rng.choice(sorted(valid)),
                )
            )

    def _collect_probe(self, interval: HeatFlowInterval) -> None:
        penetration = self._round(self.rng.uniform(1, 10))
        probe = ProbeMetadata(
            interval=interval,
            penetration=Decimal(str(penetration)),
            length=Decimal(str(self._round(self.rng.uniform(penetration, 10)))),
            tilt=Decimal(str(self._round(self.rng.uniform(0, 20)))),
        )
        self._probes.append(probe)

    def _add_concepts(self, instance: Any, field_name: str) -> None:
        """Queue one concept of the field's own vocabulary for *instance*."""
        field = instance._meta.get_field(field_name)
        vocabulary = field.vocabulary
        if vocabulary not in self._concepts:
            from research_vocabs.models import Concept

            self._concepts[vocabulary] = list(
                Concept.get_for_vocabulary(vocabulary)
                .order_by("pk")
                .values_list("pk", flat=True)
            )
        self._concept_rows.append(
            (instance, field_name, self.rng.choice(self._concepts[vocabulary]))
        )

    def _write_bulk(self) -> None:
        """Write the queued corrections, probe metadata and concept rows."""
        HeatFlowCorrection.objects.bulk_create(self._corrections)
        for probe in ProbeMetadata.objects.bulk_create(self._probes):
            self._add_concepts(probe, "probe_type")
        rows: dict[Any, list[Any]] = {}
        for instance, field_name, concept_id in self._concept_rows:
            relation = getattr(type(instance), field_name)
            rows.setdefault(relation.through, []).append(
                relation.through(
                    **{
                        f"{relation.field.m2m_field_name()}_id": instance.pk,
                        "concept_id": concept_id,
                    }
                )
            )
        for through, objs in rows.items():
            through.objects.bulk_create(objs)
        self._corrections, self._probes, self._concept_rows = [], [], []
