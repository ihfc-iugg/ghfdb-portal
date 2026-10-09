"""Score every gradient, conductivity, child and parent (FS-007).

Scores are stored, and a write that bypasses the ORM (a queryset ``update`` or a
``bulk_create``) leaves them out of date, as do records written before scoring existed. The
portal's container runs this command on start, after the migrations.
"""

from django.core.management.base import BaseCommand

from heat_flow.models import (
    HeatFlow,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from heat_flow.quality import SCHEME_REVISION


class Command(BaseCommand):
    """Recalculate stored quality scores, in the order each level reads the one below."""

    help = (
        "Recalculate the stored quality scores of gradients, conductivities, children and"
        " parents that the current scheme revision has not scored. Use --all to recalculate"
        " every record."
    )

    # Records read and refreshed together. The release holds about 90,000 determinations.
    CHUNK_SIZE = 500

    def add_arguments(self, parser):
        """Add the option that widens the run to every record."""
        parser.add_argument(
            "--all",
            action="store_true",
            help=(
                "Recalculate every record, not only those the current revision has not"
                " scored. This is the repair for writes that bypass the ORM."
            ),
        )

    def handle(self, *args, **options):
        """Refresh each level in turn and report how many records it covered."""
        counts = {
            name: self.refresh(queryset, method, options["all"])
            for name, queryset, method in self.levels()
        }
        self.stdout.write(
            ", ".join(f"{count} {name}" for name, count in counts.items())
            + " refreshed"
        )

    @staticmethod
    def levels():
        """Return each level as its name, its queryset and the method that refreshes it.

        Gradients and conductivities come first, then the children that read them, then the
        parents that read the children. The concept fields and the corrections are fetched
        with each chunk, so a refresh does not query them one record at a time.
        """
        child_concepts = [
            f"{relation}__{field}"
            for relation, model in (
                ("thermal_gradient", ThermalGradient),
                ("thermal_conductivity", IntervalConductivity),
            )
            for field in model.SCORED_CONCEPT_FIELDS
        ]
        return (
            (
                "gradients",
                ThermalGradient.objects.prefetch_related(
                    *ThermalGradient.SCORED_CONCEPT_FIELDS
                ),
                "refresh_score",
            ),
            (
                "conductivities",
                IntervalConductivity.objects.prefetch_related(
                    *IntervalConductivity.SCORED_CONCEPT_FIELDS
                ),
                "refresh_score",
            ),
            (
                "children",
                HeatFlow.objects.select_related(
                    "thermal_gradient", "thermal_conductivity"
                ).prefetch_related("corrections", *child_concepts),
                "refresh_quality",
            ),
            (
                "parents",
                ParentHeatFlow.objects.prefetch_related("children"),
                "refresh_quality",
            ),
        )

    def refresh(self, queryset, method: str, every_record: bool) -> int:
        """Refresh the records of one level in chunks and return how many there were.

        Args:
            queryset: The level's records, with what a refresh reads prefetched.
            method: The name of the model method that recalculates and stores a record.
            every_record: Refresh every record, not only those another revision scored.
        """
        if not every_record:
            queryset = queryset.exclude(quality_scheme=SCHEME_REVISION)
        pks = list(queryset.order_by("pk").values_list("pk", flat=True))
        for start in range(0, len(pks), self.CHUNK_SIZE):
            chunk = pks[start : start + self.CHUNK_SIZE]
            for record in queryset.filter(pk__in=chunk):
                getattr(record, method)()
        return len(pks)
