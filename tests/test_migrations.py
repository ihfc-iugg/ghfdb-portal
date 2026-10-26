# The portal's own applications must have no unrecorded model changes.

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
