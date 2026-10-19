"""Add demo data to a development database (FS-008).

Each run adds datasets that carry a literature item, contributors, an assessment and a
generated heat flow graph beneath them. Nothing that is not demo data is touched. Every demo
dataset holds ``options["demo_data"] = True``, so ``Dataset.all_objects`` filtered on it finds
them all.
"""

import itertools
import random
import uuid
from typing import Any, cast

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from fairdm.contrib.contributors.models import Contribution
from fairdm.core.dataset.models import Dataset, DatasetLiteratureRelation
from heat_flow.demo import DemoGraph
from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow
from heat_flow.signals import Recalculation
from literature.models import LiteratureItem

from review.models import Review
from review.states import States

DEFAULT_SIZE = 20
MIN_SIZE = 4
MAX_SIZE = 200

#: The assessment states in the order the first datasets of a run take them.
STATE_PLAN = (
    States.DESCRIBED,
    States.AWAITING_DECISION,
    States.CHANGES_REQUESTED,
    States.COMPLETE,
)

DEMO_EMAIL_DOMAIN = "demo.example"
GIVEN_NAMES = ("Aiko", "Bruno", "Chidi", "Dara", "Elif", "Farid", "Greta", "Hugo")
FAMILY_NAMES = ("Okafor", "Lindqvist", "Moreau", "Tanaka", "Silva", "Novak", "Haddad")
SURVEY_SUBJECTS = (
    "Continental margin",
    "Rift basin",
    "Shield terrain",
    "Foreland basin",
    "Oceanic crust",
    "Geothermal field",
)


class Command(BaseCommand):
    """Add demo datasets, with their assessments and heat flow records, to a development database."""

    help = (
        "Add demo datasets, each with literature, contributors, an assessment and generated "
        "heat flow records, to a development database. Refuses to run in production."
    )

    def add_arguments(self, parser):
        """Add the number of datasets to create."""
        parser.add_argument(
            "--size",
            type=int,
            default=DEFAULT_SIZE,
            help=(
                f"The number of datasets to create, from {MIN_SIZE} to {MAX_SIZE}"
                f" (default {DEFAULT_SIZE}). Four is the least that holds every assessment state."
            ),
        )

    def handle(self, *args, **options):
        """Refuse production or a size out of range, load the vocabularies and licences, then create the datasets."""
        self._refuse_production()
        size = options["size"]
        if not MIN_SIZE <= size <= MAX_SIZE:
            raise CommandError(
                f"--size must be from {MIN_SIZE} to {MAX_SIZE} datasets, not {size}."
            )
        call_command("preload")
        call_command("seed_licenses")

        rng = random.Random()  # noqa: S311 - demo values, not secrets
        next_ghfdb_id = itertools.count(self._next_ghfdb_id()).__next__
        uploader = self._demo_person("Demo", "User", claimed=True)
        totals = {"datasets": 0, "sites": 0, "children": 0}

        for position in range(size):
            with transaction.atomic(), Recalculation.deferred():
                dataset = self._create_dataset(
                    position, rng, next_ghfdb_id, uploader=uploader
                )
            sites = HeatFlowSite.objects.filter(dataset=dataset).count()
            children = HeatFlow.objects.filter(dataset=dataset).count()
            totals["datasets"] += 1
            totals["sites"] += sites
            totals["children"] += children
            if options["verbosity"] >= 2:
                self.stdout.write(f"{dataset.name}: {sites} sites, {children} children")

        self.stdout.write(
            f"Created {totals['datasets']} datasets, {totals['sites']} sites"
            f" and {totals['children']} children."
        )

    def _refuse_production(self) -> None:
        """Raise when the resolved environment is not a development one."""
        from fairdm.apps import NON_PRODUCTION_ENVIRONMENTS, FairDMConfig

        config = cast(FairDMConfig, apps.get_app_config("fairdm"))
        environment = config.resolved_environment()
        if environment not in NON_PRODUCTION_ENVIRONMENTS:
            raise CommandError(
                f"Refusing to add demo data: the resolved environment {environment!r} is not"
                " a development one."
            )

    @staticmethod
    def _next_ghfdb_id() -> int:
        """Return one above the highest published identifier on any parent or child."""
        highest = [
            model.objects.aggregate(highest=Max("ghfdb_id"))["highest"] or 0
            for model in (ParentHeatFlow, HeatFlow)
        ]
        return max(highest) + 1

    @staticmethod
    def _state_for(position: int) -> States:
        """Return the assessment state of the dataset at *position* in a run.

        The first four datasets take each state once. Later ones are complete four times in
        five and take the other states in turn otherwise.
        """
        if position < len(STATE_PLAN):
            return STATE_PLAN[position]
        if position % 5:
            return States.COMPLETE
        return STATE_PLAN[position % len(STATE_PLAN)]

    @staticmethod
    def _demo_person(given: str, family: str, *, claimed: bool = False) -> Any:
        """Return the demo person with this name, creating them when absent."""
        Person = get_user_model()
        email = f"{given}.{family}@{DEMO_EMAIL_DOMAIN}".lower()
        person = Person.objects.filter(email__iexact=email).first()
        if person is None:
            person = Person(
                email=email,
                first_name=given,
                last_name=family,
                is_active=True,
                is_claimed=claimed,
            )
            person.set_unusable_password()
            person.save()
        return person

    def _create_dataset(
        self,
        position: int,
        rng: random.Random,
        next_ghfdb_id: Any,
        *,
        uploader: Any,
    ) -> Dataset:
        """Create one demo dataset with its literature, contributors, assessment and graph.

        Args:
            position: The dataset's place in the run.
            rng: The source of every random choice.
            next_ghfdb_id: Returns the next published identifier.
            uploader: The person who uploaded and decided the assessment.

        Returns:
            The dataset.
        """
        state = self._state_for(position)
        complete = state == States.COMPLETE
        token = uuid.uuid4().hex[:12]

        literature = LiteratureItem.objects.create(
            citation_key=f"demo-{token}",
            item={
                "type": "article-journal",
                "title": f"{rng.choice(SURVEY_SUBJECTS)} heat flow, demo {token}",
                "author": [
                    {
                        "given": rng.choice(GIVEN_NAMES),
                        "family": rng.choice(FAMILY_NAMES),
                    }
                ],
                "issued": {"date-parts": [[rng.randint(1985, 2024)]]},
                "DOI": f"10.5072/demo.{token}",
            },
        )
        dataset = Dataset.objects.create(
            name=f"{rng.choice(SURVEY_SUBJECTS)} heat flow {token[:6]}",
            reference=literature,
            options={"demo_data": True},
            visibility=(
                Dataset.VISIBILITY_CHOICES.PUBLIC
                if complete
                else Dataset.VISIBILITY_CHOICES.PRIVATE
            ),
            published=complete,
        )
        DatasetLiteratureRelation.objects.create(
            dataset=dataset, literature_item=literature, relationship_type="IsCitedBy"
        )

        roles = ("Creator", "ContactPerson", "DataCollector")
        for role in roles[: rng.randint(1, 3)]:
            person = self._demo_person(
                rng.choice(GIVEN_NAMES), rng.choice(FAMILY_NAMES)
            )
            Contribution.add_to(person, dataset, [role])

        today = timezone.now().date().isoformat()
        decided = state in (States.CHANGES_REQUESTED, States.COMPLETE)
        review = Review.objects.create(
            dataset=dataset,
            literature=literature,
            uploaded_by=uploader,
            state=state,
            decided_by=uploader if decided else None,
            decided_at=timezone.now() if decided else None,
            decision_comment=(
                "Please check the conductivity sources."
                if state == States.CHANGES_REQUESTED
                else ""
            ),
            start_date=today,
            end_date=today,
        )
        review.reviewers.add(uploader)

        DemoGraph(dataset, rng, next_ghfdb_id if complete else None).build()
        return dataset
