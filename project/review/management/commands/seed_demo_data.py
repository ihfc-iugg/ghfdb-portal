"""Add demo data to a development database (FS-008).

Each run adds datasets that carry a literature item, contributors, an assessment and a
generated heat flow graph beneath them. Most datasets are grouped into a few projects, and the
rest belong to none. Nothing that is not demo data is touched. Every demo dataset and project
holds ``options["demo_data"] = True``, so ``Dataset.all_objects`` and ``Project.objects``
filtered on it find them all.
"""

import itertools
import random
import uuid
from typing import Any, cast

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from fairdm.contrib.contributors.models import Contribution, Organization
from fairdm.contrib.contributors.services.crediting import Crediting
from fairdm.core.choices import ProjectStatus
from fairdm.core.dataset.models import Dataset, DatasetLiteratureRelation
from fairdm.core.project.models import Project, ProjectDescription
from fairdm.management.commands.create_dev_accounts import (
    DEV_ACCOUNT_PASSWORD,
    EXAMPLE_ACCOUNTS,
    PROFILE_ACCOUNTS,
)
from heat_flow.demo import DemoGraph
from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow
from heat_flow.signals import Recalculation
from literature.models import LiteratureItem

from review.models import Review
from review.permissions import DATA_ASSESSOR_GROUP, DATA_CURATOR_GROUP
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

#: The assessment roles' accounts, in the shape of ``EXAMPLE_ACCOUNTS``, beside the group each
#: one joins. The curator is the entry ``seed_profiles`` would add.
DATA_ASSESSOR_ACCOUNT = (
    "data-assessor.user@example.com",
    "Data Assessor",
    "User",
    False,
    False,
)
DATA_CURATOR_ACCOUNT = next(
    account for account in PROFILE_ACCOUNTS if account[0].startswith("data-curator.")
)
DEMO_ACCOUNTS = (
    *((account, None) for account in EXAMPLE_ACCOUNTS),
    (DATA_ASSESSOR_ACCOUNT, DATA_ASSESSOR_GROUP),
    (DATA_CURATOR_ACCOUNT, DATA_CURATOR_GROUP),
)

DEMO_EMAIL_DOMAIN = "demo.example"
GIVEN_NAMES = ("Aiko", "Bruno", "Chidi", "Dara", "Elif", "Farid", "Greta", "Hugo")
FAMILY_NAMES = ("Okafor", "Lindqvist", "Moreau", "Tanaka", "Silva", "Novak", "Haddad")
#: Datasets per project. The last dataset of every group belongs to no project.
DATASETS_PER_PROJECT = 4
ORGANIZATIONS = (
    "Demo Institute of Geothermics",
    "Demo Marine Geophysics Laboratory",
    "Demo Geological Survey",
)
PROJECT_THEMES = (
    "Regional heat flow compilation",
    "Marine heat flow survey",
    "Borehole temperature programme",
    "Geothermal resource assessment",
)
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
        parser.add_argument(
            "--page-states",
            action="store_true",
            help=(
                "Vary the first complete dataset so every state a heat flow record's page"
                " answers for can be opened."
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
        call_command("create_dev_accounts")
        assessor, curator = self._ensure_accounts()
        totals = {"datasets": 0, "projects": 0, "sites": 0, "children": 0}
        project = None
        unpublished = None
        varied = False

        for position in range(size):
            group_position = position % DATASETS_PER_PROJECT
            with transaction.atomic(), Recalculation.deferred():
                if group_position == 0:
                    project = self._create_project(rng, creator=assessor)
                    totals["projects"] += 1
                dataset = self._create_dataset(
                    position,
                    rng,
                    next_ghfdb_id,
                    assessor=assessor,
                    curator=curator,
                    project=(
                        project if group_position < DATASETS_PER_PROJECT - 1 else None
                    ),
                )
            if unpublished is None:
                unpublished = dataset
            if options["page_states"] and dataset.published and not varied:
                DemoGraph(dataset, rng).vary_page_states(unpublished)
                varied = True
            sites = HeatFlowSite.objects.filter(dataset=dataset).count()
            children = HeatFlow.objects.filter(dataset=dataset).count()
            totals["datasets"] += 1
            totals["sites"] += sites
            totals["children"] += children
            if options["verbosity"] >= 2:
                self.stdout.write(f"{dataset.name}: {sites} sites, {children} children")

        self.stdout.write(
            f"Created {totals['datasets']} datasets in {totals['projects']} projects,"
            f" {totals['sites']} sites"
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
        """Return one above the highest published identifier on any parent or child.

        Returns:
            The next free published identifier.
        """
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

        Args:
            position: The dataset's zero-based place in the run.

        Returns:
            The state the dataset's assessment is created in.
        """
        if position < len(STATE_PLAN):
            return STATE_PLAN[position]
        if position % 5:
            return States.COMPLETE
        return STATE_PLAN[position % len(STATE_PLAN)]

    @staticmethod
    def _ensure_accounts() -> tuple[Any, Any]:
        """Create the sign-in accounts the demo data uses, reusing any that exist.

        An account that already exists keeps everything but its groups. The groups are never
        created here: the migrations and the portal roles do that.

        Returns:
            The demo Data Assessor and the demo Data Curator.
        """
        Person = get_user_model()
        EmailAddress = apps.get_model("account", "EmailAddress")
        accounts: dict[str, Any] = {}
        for (email, first, last, is_staff, is_superuser), group in DEMO_ACCOUNTS:
            person: Any = Person.objects.filter(email__iexact=email).first()
            if person is None:
                person = Person(
                    email=email,
                    first_name=first,
                    last_name=last,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=True,
                    is_claimed=True,
                )
                person.set_password(DEV_ACCOUNT_PASSWORD)
                person.save()
            EmailAddress.objects.update_or_create(
                user=person, email=email, defaults={"verified": True, "primary": True}
            )
            if group:
                person.groups.add(Group.objects.get(name=group))
            accounts[email] = person
        return accounts[DATA_ASSESSOR_ACCOUNT[0]], accounts[DATA_CURATOR_ACCOUNT[0]]

    @staticmethod
    def _demo_person(given: str, family: str) -> Any:
        """Return the demo person with this name, creating them when absent.

        Args:
            given: The person's first name.
            family: The person's last name.

        Returns:
            The existing or new person, who cannot sign in.
        """
        Person = get_user_model()
        email = f"{given}.{family}@{DEMO_EMAIL_DOMAIN}".lower()
        person = Person.objects.filter(email__iexact=email).first()
        if person is None:
            person = Person(
                email=email,
                first_name=given,
                last_name=family,
                is_active=True,
                is_claimed=False,
            )
            person.set_unusable_password()
            person.save()
        return person

    @staticmethod
    def _create_project(rng: random.Random, *, creator: Any) -> Project:
        """Create one public demo project, owned by a demo organization.

        Args:
            rng: The source of every random choice.
            creator: The person credited as the project's creator.

        Returns:
            The project.
        """
        owner_name = rng.choice(ORGANIZATIONS)
        owner = Organization.objects.filter(name=owner_name).first()
        if owner is None:
            owner = Organization.objects.create(name=owner_name)
        project = Project.objects.create(
            name=f"{rng.choice(PROJECT_THEMES)} {uuid.uuid4().hex[:6]}",
            owner=owner,
            visibility=Project.VISIBILITY.PUBLIC,
            status=rng.choice(ProjectStatus.values),
            options={"demo_data": True},
        )
        ProjectDescription.objects.create(
            related=project,
            type="Abstract",
            value=(
                "Demo data: a generated project grouping heat flow datasets for"
                " development. None of it describes real measurements."
            ),
        )
        Crediting(project).make_creator(creator, roles=["ProjectLeader"])
        return project

    def _create_dataset(
        self,
        position: int,
        rng: random.Random,
        next_ghfdb_id: Any,
        *,
        assessor: Any,
        curator: Any,
        project: Project | None = None,
    ) -> Dataset:
        """Create one demo dataset with its literature, contributors, assessment and graph.

        Args:
            position: The dataset's place in the run.
            rng: The source of every random choice.
            next_ghfdb_id: Returns the next published identifier.
            assessor: The Data Assessor who uploaded the assessment and is credited on the dataset.
            curator: The Data Curator who decides assessments.
            project: The project the dataset belongs to, or ``None``.

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
            project=project,
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

        Crediting(dataset).make_creator(assessor, roles=["DataManager"])
        dataset.add_contributor(assessor, with_roles=["DataCollector"])

        today = timezone.now().date().isoformat()
        decided = state in (States.CHANGES_REQUESTED, States.COMPLETE)
        review = Review.objects.create(
            dataset=dataset,
            literature=literature,
            uploaded_by=assessor,
            state=state,
            decided_by=curator if decided else None,
            decided_at=timezone.now() if decided else None,
            decision_comment=(
                "Please check the conductivity sources."
                if state == States.CHANGES_REQUESTED
                else ""
            ),
            start_date=today,
            end_date=today,
        )
        review.reviewers.add(assessor)

        DemoGraph(dataset, rng, next_ghfdb_id if complete else None).build()
        return dataset
