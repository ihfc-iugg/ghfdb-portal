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
from fairdm_geo.vocabularies import ODM2_SITE_TYPE

from . import vocabularies
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
from .overview import HeatFlowPage

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
    """Describe an onshore region measured by drilling.

    Args:
        name: A readable label.
        lat: The southern and northern edges in decimal degrees.
        lon: The western and eastern edges in decimal degrees.

    Returns:
        The region, with the onshore environment and the drilling exploration method.
    """
    return Region(name, *lat, *lon, False, "onshore_continental", "drilling")


def _sea(name: str, lat: tuple[float, float], lon: tuple[float, float]) -> Region:
    """Describe an offshore region measured by marine probing.

    Args:
        name: A readable label.
        lat: The southern and northern edges in decimal degrees.
        lon: The western and eastern edges in decimal degrees.

    Returns:
        The region, with the offshore environment and the marine probing exploration method.
    """
    return Region(name, *lat, *lon, True, "offshore_marine", "probing_offshore")


REGIONS = (
    _land("Western North America", (34.0, 48.0), (-120.0, -108.0)),
    _land("Eastern North America", (35.0, 46.0), (-90.0, -75.0)),
    _land("Canadian Shield", (48.0, 54.0), (-100.0, -84.0)),
    _land("Central Europe", (46.0, 54.0), (5.0, 20.0)),
    _land("Scandinavia", (59.0, 66.0), (12.0, 16.0)),
    _land("Finland", (61.0, 68.0), (24.0, 28.0)),
    _land("Iberia", (37.0, 43.0), (-8.0, 0.0)),
    _land("Tibetan Plateau", (28.0, 36.0), (80.0, 98.0)),
    _land("North China", (34.0, 42.0), (108.0, 120.0)),
    _land("India", (18.0, 26.0), (74.0, 84.0)),
    _land("East African Rift", (-10.0, 8.0), (30.0, 40.0)),
    _land("Southern Africa", (-33.0, -20.0), (18.0, 30.0)),
    _land("Eastern Australia", (-37.0, -22.0), (140.0, 152.0)),
    _sea("North Sea", (55.0, 58.0), (1.0, 4.0)),
    _sea("Gulf of Mexico", (24.0, 28.0), (-94.0, -86.0)),
    _sea("Cascadia margin", (42.0, 48.0), (-127.0, -124.0)),
    _sea("Japan Trench", (36.0, 40.0), (143.0, 146.0)),
    _sea("Mid-Atlantic Ridge flank", (20.0, 30.0), (-48.0, -40.0)),
    _sea("East Pacific Rise flank", (-10.0, 0.0), (-110.0, -100.0)),
    _sea("Mediterranean basin", (33.5, 36.0), (15.0, 22.0)),
    _sea("South China Sea", (10.0, 18.0), (112.0, 118.0)),
)

#: Corrections a child may carry, in a fixed order so a seeded build repeats.
CORRECTION_TYPES = tuple(HeatFlowCorrection.CorrectionTypeChoices.values)


class DemoGraph:
    """Builds the heat flow records of one dataset.

    Sites, intervals, parents, children, gradients and conductivities are multi-table models
    that Django cannot bulk-insert, so they are saved one at a time. Corrections, probe
    metadata and the concept rows are collected and written in bulk when ``build`` ends.

    Args:
        dataset: The dataset every record is created in.
        rng: The source of every random draw.
        next_ghfdb_id: Returns the next published identifier, or ``None`` for an
            unpublished dataset, whose records carry no identifier.
    """

    def __init__(
        self,
        dataset: Any,
        rng: random.Random,
        next_ghfdb_id: Callable[[], int] | None = None,
    ) -> None:
        self.dataset = dataset
        self.rng = rng
        self.next_ghfdb_id = next_ghfdb_id
        self._label_count = 0
        self._corrections: list[HeatFlowCorrection] = []
        self._probes: list[ProbeMetadata] = []
        self._concept_rows: list[tuple[Any, str, str]] = []
        self._concepts: dict[str, list[str]] = {}

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

    def vary_page_states(self, unpublished: Any) -> None:
        """Vary the dataset's first six sites so every state a record page shows exists.

        The sites keep their order, so the six states fall on sites with one, two,
        three, four, one and two children:

        1. A parent with no children, and a child with no gradient, conductivity,
           corrections or parent.
        2. A site with no parent.
        3. A parent with children and none marked relevant.
        4. A site with more intervals than its page lists, one interval and one child of
           another interval in the unpublished dataset.
        5. Scores stored under another scheme revision, and a site with no location.
        6. A child not yet scored, a gradient and a parent in the unpublished dataset.

        A record moved to the unpublished dataset loses its published identifier, as
        every record of an unpublished dataset does. Running it again varies the same
        sites further and never fails.

        Args:
            unpublished: A dataset the visitor may not open, which receives the records
                that must be hidden beside published ones.

        Raises:
            ValueError: The dataset has fewer than six sites.
        """
        sites = list(
            HeatFlowSite.objects.filter(dataset=self.dataset).order_by("pk")[:6]
        )
        if len(sites) < 6:
            raise ValueError("vary_page_states needs a dataset of at least six sites.")
        alone, unparented, unrelated, lengthy, stale, unscored = sites

        def children_of(site: HeatFlowSite):
            return HeatFlow.objects.filter(sample__in=site.intervals.all()).order_by(
                "pk"
            )

        bare = children_of(alone)
        HeatFlowCorrection.objects.filter(heat_flow__in=bare).delete()
        bare.update(parent=None, thermal_gradient=None, thermal_conductivity=None)
        for child in bare:
            child.refresh_quality()
        for parent in ParentHeatFlow.objects.filter(sample=alone):
            parent.refresh_quality()

        ParentHeatFlow.objects.filter(sample=unparented).delete()

        children_of(unrelated).update(is_relevant=False)
        for parent in ParentHeatFlow.objects.filter(sample=unrelated):
            parent.refresh_quality()

        for position in range(HeatFlowPage.intervals_shown):
            HeatFlowInterval.objects.create(
                dataset=self.dataset,
                name=self._label(),
                site=lengthy,
                top=3000 + position * 50,
                bottom=3040 + position * 50,
            )
        first, second = HeatFlowInterval.objects.filter(
            pk__in=children_of(lengthy).values("sample")
        ).order_by("pk")[:2]
        HeatFlowInterval.objects.filter(pk=first.pk).update(dataset=unpublished)
        HeatFlow.objects.filter(sample=first).update(dataset=unpublished, ghfdb_id=None)
        HeatFlow.objects.filter(sample=second).update(
            dataset=unpublished, ghfdb_id=None
        )

        scheme = "hfqa_tool 0.1"
        HeatFlowSite.objects.filter(pk=stale.pk).update(location=None)
        children = children_of(stale)
        ThermalGradient.objects.filter(
            pk__in=children.values("thermal_gradient")
        ).update(quality_scheme=scheme)
        children.update(quality_scheme=scheme)
        ParentHeatFlow.objects.filter(sample=stale).update(quality_scheme=scheme)

        first, second = children_of(unscored)[:2]
        HeatFlow.objects.filter(pk=first.pk).update(
            U_score="Ux",
            M_score="Mx",
            T_score=None,
            TC_score=None,
            quality=None,
            quality_scheme="",
        )
        ThermalGradient.objects.filter(pk=second.thermal_gradient_id).update(
            dataset=unpublished
        )
        ParentHeatFlow.objects.filter(sample=unscored).update(
            dataset=unpublished, ghfdb_id=None
        )

    def _label(self) -> str:
        """Return the next record name, unique within this build.

        Returns:
            A name and local identifier of the form ``DEMO-<dataset pk>-<n>``.
        """
        self._label_count += 1
        return f"DEMO-{self.dataset.pk}-{self._label_count}"

    def _published_id(self) -> int | None:
        """Return the next published identifier for a record.

        Returns:
            The identifier, or ``None`` when the dataset is unpublished.
        """
        return None if self.next_ghfdb_id is None else self.next_ghfdb_id()

    def _uncertainty(self, value: float) -> float:
        """Draw an uncertainty of 5 to 25 percent of *value*.

        Args:
            value: The measurement the uncertainty belongs to.

        Returns:
            A positive uncertainty, rounded to two places.
        """
        return round(abs(value) * self.rng.uniform(0.05, 0.25), 2)

    def _place_site(self) -> tuple[HeatFlowSite, Region]:
        """Create a site at a point no other site holds.

        Returns:
            The site and the region it was drawn in.

        Raises:
            ValidationError: Every one of ``MAX_PLACEMENT_ATTEMPTS`` points was taken.
        """
        for attempt in range(MAX_PLACEMENT_ATTEMPTS):
            region = self.rng.choice(REGIONS)
            latitude = round(self.rng.uniform(region.min_lat, region.max_lat), 5)
            longitude = round(self.rng.uniform(region.min_lon, region.max_lon), 5)
            label = self._label()
            try:
                site = HeatFlowSite.objects.create(
                    dataset=self.dataset,
                    name=label,
                    local_id=label,
                    location=HeatFlowSite.point_at(latitude, longitude),
                    type_id=f"{ODM2_SITE_TYPE.uri}/ocean"
                    if region.marine
                    else f"{ODM2_SITE_TYPE.uri}/land",
                    elevation=self._elevation(region),
                    environment_id=vocabularies.term(
                        vocabularies.GEOGRAPHIC_ENVIRONMENT, region.environment
                    ),
                    explo_method_id=vocabularies.term(
                        vocabularies.EXPLORATION_METHOD, region.explo_method
                    ),
                )
            except ValidationError:
                if attempt == MAX_PLACEMENT_ATTEMPTS - 1:
                    raise
                continue
            self._add_concepts(site, "explo_purpose")
            return site, region
        raise AssertionError("unreachable")  # pragma: no cover

    def _elevation(self, region: Region) -> float:
        """Draw an elevation that suits the region's medium.

        Args:
            region: The region the site lies in.

        Returns:
            A depth below sea level for a marine region, a height above it otherwise.
        """
        low, high = (-6000, -200) if region.marine else (0, 3000)
        return round(self.rng.uniform(low, high), 1)

    def _plan_child(self, region: Region) -> dict[str, float]:
        """Draw one child's values so that its heat flow is its gradient times its conductivity.

        Args:
            region: The region the child's site lies in.

        Returns:
            The child's ``conductivity``, ``gradient`` and ``value``.
        """
        rng = self.rng
        conductivity = round(
            min(max(rng.lognormvariate(math.log(2.5), 0.3), 0.8), 6), 2
        )
        target = min(
            max(rng.lognormvariate(math.log(95 if region.marine else 65), 0.4), 15), 400
        )
        gradient = round(min(max(target / conductivity, 5), 300), 2)
        return {
            "conductivity": conductivity,
            "gradient": gradient,
            "value": round(gradient * conductivity, 2),
        }

    def _build_site(self, child_count: int) -> None:
        """Create a site, its parent and the children beneath the parent.

        Args:
            child_count: The number of children. From three up, the last is not relevant
                to the parent.
        """
        site, region = self._place_site()
        plans = [self._plan_child(region) for _ in range(child_count)]
        relevant = [True] * child_count
        if child_count >= 3:
            relevant[-1] = False
        used = [
            plan["value"] for plan, flag in zip(plans, relevant, strict=True) if flag
        ]
        parent_value = round(sum(used) / len(used), 2)

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
        """Create one child with its interval, gradient and conductivity.

        Corrections, probe metadata and concepts are queued for ``build`` to write.

        Args:
            site: The site the child is measured at.
            region: The region the site lies in.
            parent: The parent the child belongs to.
            plan: The values drawn by ``_plan_child``.
            is_relevant: Whether the child counts towards the parent's value.
        """
        rng = self.rng
        dataset = self.dataset
        if region.marine:
            top, bottom = 0.0, round(rng.uniform(2, 10), 1)
        else:
            top = round(rng.uniform(0, 1500), 1)
            bottom = round(top + rng.uniform(50, 1500), 1)

        interval = HeatFlowInterval.objects.create(
            dataset=dataset, name=self._label(), site=site, top=top, bottom=bottom
        )
        gradient_value = plan["gradient"]
        corrected = round(gradient_value * rng.uniform(0.95, 1.1), 2)
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
        """Queue valid corrections for *child*, always a temperature one on a probe.

        Args:
            child: The heat flow the corrections apply to.
            probed: Whether the child was measured by a marine probe.
        """
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
        """Queue probe metadata for a marine interval.

        Args:
            interval: The interval the probe measured.
        """
        penetration = round(self.rng.uniform(1, 10), 2)
        probe = ProbeMetadata(
            interval=interval,
            penetration=Decimal(str(penetration)),
            length=Decimal(str(round(self.rng.uniform(penetration, 10), 2))),
            tilt=Decimal(str(round(self.rng.uniform(0, 20), 2))),
        )
        self._probes.append(probe)

    def _add_concepts(self, instance: Any, field_name: str) -> None:
        """Queue one concept of the field's own vocabulary for *instance*.

        Args:
            instance: The record that carries the field.
            field_name: The vocabulary field to give a concept.
        """
        field = instance._meta.get_field(field_name)
        vocabulary = field.vocabulary[0]
        if vocabulary.uri not in self._concepts:
            self._concepts[vocabulary.uri] = list(
                vocabularies.concepts(vocabulary)
                .order_by("uri")
                .values_list("uri", flat=True)
            )
        self._concept_rows.append(
            (instance, field_name, self.rng.choice(self._concepts[vocabulary.uri]))
        )

    def _write_bulk(self) -> None:
        """Write the queued corrections, probe metadata and concept rows."""
        HeatFlowCorrection.objects.bulk_create(self._corrections)
        for probe in ProbeMetadata.objects.bulk_create(self._probes):
            self._add_concepts(probe, "probe_type")
        rows: dict[Any, list[Any]] = {}
        for instance, field_name, concept in self._concept_rows:
            relation = getattr(type(instance), field_name)
            rows.setdefault(relation.through, []).append(
                relation.through(
                    **{
                        f"{relation.field.m2m_field_name()}_id": instance.pk,
                        f"{relation.field.m2m_reverse_field_name()}_id": concept,
                    }
                )
            )
        for through, objs in rows.items():
            through.objects.bulk_create(objs)
        self._corrections, self._probes, self._concept_rows = [], [], []
