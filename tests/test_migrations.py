# The portal's own applications must have no unrecorded model changes.

import importlib
import os
import subprocess
import sys
from io import StringIO

import psycopg2
import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings

PROJECT_APPS = ["heat_flow", "ghfdb", "review"]


class TestMigrationState:
    @pytest.mark.django_db
    # The suite runs with --nomigrations, which points every app at a stub
    # module. Restore the real ones so the comparison has something to
    # compare against.
    @override_settings(MIGRATION_MODULES={})
    def test_no_unrecorded_model_changes(self):
        out = StringIO()
        try:
            call_command(
                "makemigrations",
                *PROJECT_APPS,
                check=True,
                dry_run=True,
                verbosity=1,
                stdout=out,
            )
        except SystemExit:
            pytest.fail(
                "Model changes have no migration. Run "
                f"`python manage.py makemigrations {' '.join(PROJECT_APPS)}`."
                f"\n{out.getvalue()}"
            )


class TestGHFDBProxyMigrations:
    # FS-002 FR-001: the migrations recording the GHFDB proxies touch no table. A proxy
    # model adds no table, so an ``AddField``, ``AlterField`` or ``RemoveField``
    # operation in either migration would be the defect.

    def test_the_initial_migration_is_a_bare_proxy_create_model(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module("project.ghfdb.migrations.0002_initial")
        operations = module.Migration.operations

        assert len(operations) == 1
        operation = operations[0]
        assert isinstance(operation, migrations.CreateModel)
        assert operation.name == "GHFDB"
        assert operation.fields == []
        assert operation.options.get("proxy") is True

    def test_the_child_and_parent_migration_touches_no_column(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module(
            "project.ghfdb.migrations.0003_child_and_parent_proxies"
        )
        operations = module.Migration.operations

        forbidden = (migrations.AddField, migrations.AlterField, migrations.RemoveField)
        assert not any(isinstance(operation, forbidden) for operation in operations)

    def test_the_child_and_parent_are_bare_proxies(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module(
            "project.ghfdb.migrations.0003_child_and_parent_proxies"
        )
        created = {
            operation.name: operation
            for operation in module.Migration.operations
            if isinstance(operation, migrations.CreateModel)
        }

        assert set(created) == {"GHFDBChild", "GHFDBParent"}
        for operation in created.values():
            assert operation.fields == []
            assert operation.options.get("proxy") is True


class TestMigrationsApplyToAnEmptyDatabase:
    # The migrations must actually run, not merely exist. The suite runs with
    # ``--nomigrations``, so this is the one test that applies them, to a database
    # created empty on the suite's own PostGIS server.

    HEAT_FLOW_TABLES = [
        "heat_flow_heatflowsite",
        "heat_flow_heatflowinterval",
        "heat_flow_parentheatflow",
        "heat_flow_heatflow",
        "heat_flow_thermalgradient",
        "heat_flow_intervalconductivity",
        "heat_flow_probemetadata",
        "heat_flow_heatflowcorrection",
    ]

    @pytest.mark.slow
    def test_migrations_build_every_heat_flow_table(self, empty_database):
        # The database is named through POSTGRES_*, which stack.development.env never
        # overwrites, and DATABASE_URL is dropped because it would take precedence.
        environment = {
            key: value for key, value in os.environ.items() if key != "DATABASE_URL"
        }
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput", "-v", "0"],
            cwd=settings.BASE_DIR,
            env={
                **environment,
                "DJANGO_ENV": "development",
                "POSTGRES_HOST": empty_database["HOST"],
                "POSTGRES_PORT": str(empty_database["PORT"]),
                "POSTGRES_USER": empty_database["USER"],
                "POSTGRES_PASSWORD": empty_database["PASSWORD"],
                "POSTGRES_DB": empty_database["NAME"],
            },
            capture_output=True,
            text=True,
            timeout=900,
        )

        assert result.returncode == 0, (
            "`manage.py migrate` failed against an empty database."
            f"\n{result.stdout}\n{result.stderr}"
        )

        migrated = psycopg2.connect(
            dbname=empty_database["NAME"],
            user=empty_database["USER"],
            password=empty_database["PASSWORD"],
            host=empty_database["HOST"],
            port=empty_database["PORT"],
        )
        with migrated, migrated.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables"
                " WHERE table_schema = 'public'"
            )
            built = {row[0] for row in cursor.fetchall()}
        migrated.close()

        missing = [table for table in self.HEAT_FLOW_TABLES if table not in built]
        assert not missing, (
            f"Migrations left these tables unbuilt: {missing}."
            f"\n{result.stdout}\n{result.stderr}"
        )


class TestIhfcIdentifierMigration:
    # The published vocabularies renamed their concepts, so every stored address and every
    # stored correction status has to follow. The test database holds the published
    # concepts, so each test first turns the few concepts it uses back into the ones the
    # release before held, then stores data under those names.

    MODULE = "project.heat_flow.migrations.0009_rename_ihfc_concept_identifiers"

    ONSHORE_MARINE = ("geographic-environments", "onshore_marine", "onshore-lake-river")
    LOG_EQUILIBRIUM = ("temperature-method", "LOGeq", "log-equilibrium")
    HT_FT = ("temperature-method", "HT_FT", "HT-FT-equilibrium")

    @staticmethod
    def address(slug, identifier):
        from heat_flow.vocabularies import IHFC

        return f"{IHFC}/{slug}/{identifier}"

    def release_before(self, *renamed):
        """Turn the published concepts named back into the ones the release before held."""
        from controlled_vocabularies.models import Record

        for slug, old, new in renamed:
            Record.objects.filter(uri=self.address(slug, new)).update(
                uri=self.address(slug, old), slug=old
            )

    def migrate(self, direction="forwards"):
        from django.apps import apps

        getattr(importlib.import_module(self.MODULE), direction)(apps, None)

    @pytest.mark.django_db
    def test_a_stored_single_valued_address_is_rewritten(self):
        from heat_flow.models import HeatFlowSite
        from tests.factories import HeatFlowSiteFactory

        self.release_before(self.ONSHORE_MARINE)
        site = HeatFlowSiteFactory(
            environment_id=self.address("geographic-environments", "onshore_marine"),
            explo_purpose=[],
        )

        self.migrate()

        stored = HeatFlowSite.objects.get(pk=site.pk).environment_id
        assert stored == self.address("geographic-environments", "onshore-lake-river")

    @pytest.mark.django_db
    def test_stored_many_valued_addresses_are_rewritten(self):
        from controlled_vocabularies.models import Record
        from tests.factories import ThermalGradientFactory

        self.release_before(self.LOG_EQUILIBRIUM, self.HT_FT)
        old = Record.objects.filter(
            uri__in=[
                self.address(*self.LOG_EQUILIBRIUM[:2]),
                self.address(*self.HT_FT[:2]),
            ]
        )
        gradient = ThermalGradientFactory(
            method_top=old, method_bottom=[], correction_top=[], correction_bottom=[]
        )

        self.migrate()

        assert set(gradient.method_top.values_list("uri", flat=True)) == {
            self.address("temperature-method", "log-equilibrium"),
            self.address("temperature-method", "HT-FT-equilibrium"),
        }

    @pytest.mark.django_db
    def test_a_stored_correction_status_is_rewritten(self):
        from heat_flow.models import HeatFlowCorrection
        from tests.factories import HeatFlowCorrectionFactory

        correction = HeatFlowCorrectionFactory(correction_type="S")
        # An update skips the check on save, which only knows the published statuses.
        HeatFlowCorrection.objects.filter(pk=correction.pk).update(
            status="present_not_corrected"
        )

        self.migrate()

        correction.refresh_from_db()
        assert correction.status == "present-uncorrected"

    @pytest.mark.django_db
    def test_an_address_that_was_not_renamed_is_left_as_it_is(self):
        from heat_flow.models import HeatFlowSite
        from heat_flow.vocabularies import EXPLORATION_METHOD, term
        from tests.factories import HeatFlowSiteFactory

        drilling = term(EXPLORATION_METHOD, "drilling")
        site = HeatFlowSiteFactory(explo_method_id=drilling, explo_purpose=[])
        site_type = site.type_id

        self.migrate()

        stored = HeatFlowSite.objects.get(pk=site.pk)
        assert (stored.explo_method_id, stored.type_id) == (drilling, site_type)

    @pytest.mark.django_db
    def test_the_old_concept_becomes_the_new_one_when_the_new_release_is_not_loaded(
        self,
    ):
        # The portal migrates before it loads the vocabularies, so the new concept does
        # not exist yet when a row is pointed at it.
        from controlled_vocabularies.models import Record
        from tests.factories import HeatFlowSiteFactory

        self.release_before(self.ONSHORE_MARINE)
        HeatFlowSiteFactory(
            environment_id=self.address("geographic-environments", "onshore_marine"),
            explo_purpose=[],
        )

        self.migrate()

        held = Record.objects.values_list("uri", flat=True)
        assert self.address("geographic-environments", "onshore-lake-river") in held
        assert self.address("geographic-environments", "onshore_marine") not in held

    @pytest.mark.django_db
    def test_the_old_concept_is_dropped_when_the_new_release_is_already_loaded(self):
        from controlled_vocabularies.models import Record

        new = Record.objects.get(
            uri=self.address("geographic-environments", "onshore-lake-river")
        )
        self.release_before(self.ONSHORE_MARINE)
        new.pk = None
        new.save()

        self.migrate()

        old_address = self.address("geographic-environments", "onshore_marine")
        assert not Record.objects.filter(uri=old_address).exists()
        assert Record.objects.filter(uri=new.uri).count() == 1

    @pytest.mark.django_db
    def test_reversing_restores_the_addresses_the_release_before_held(self):
        from heat_flow.models import HeatFlowSite
        from tests.factories import HeatFlowSiteFactory

        self.release_before(self.ONSHORE_MARINE)
        old_address = self.address("geographic-environments", "onshore_marine")
        site = HeatFlowSiteFactory(environment_id=old_address, explo_purpose=[])
        self.migrate()

        self.migrate("backwards")

        assert HeatFlowSite.objects.get(pk=site.pk).environment_id == old_address
