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


class TestGHFDBChildProxyMigrations:
    # FS-002 FR-001: the migrations recording ``GHFDBChild`` touch no table. A proxy
    # model adds no table, so an ``AddField``, ``AlterField`` or ``RemoveField``
    # operation in either migration would be the defect.

    def test_the_initial_migration_is_a_bare_proxy_create_model(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module("project.ghfdb.migrations.0002_ghfdb")
        operations = module.Migration.operations

        assert len(operations) == 1
        operation = operations[0]
        assert isinstance(operation, migrations.CreateModel)
        assert operation.name == "GHFDB"
        assert operation.fields == []
        assert operation.options.get("proxy") is True

    def test_the_rename_migration_touches_no_table(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module(
            "project.ghfdb.migrations.0003_ghfdbchild_ghfdbparent"
        )
        operations = module.Migration.operations

        forbidden = (migrations.AddField, migrations.AlterField, migrations.RemoveField)
        assert not any(isinstance(operation, forbidden) for operation in operations)

        rename_operations = [
            operation
            for operation in operations
            if isinstance(operation, migrations.RenameModel)
        ]
        assert len(rename_operations) == 1
        assert rename_operations[0].old_name == "GHFDB"
        assert rename_operations[0].new_name == "GHFDBChild"


class TestGHFDBParentProxyMigrations:
    # FS-002 FR-001: the migration recording ``GHFDBParent`` is a bare proxy
    # ``CreateModel`` and no other operation. A proxy adds no table, so an ``AddField``
    # or ``AlterField`` naming ``GHFDBParent`` would be the defect.

    def test_the_create_model_is_a_bare_proxy(self):
        import importlib

        from django.db import migrations

        module = importlib.import_module(
            "project.ghfdb.migrations.0003_ghfdbchild_ghfdbparent"
        )
        operations = module.Migration.operations

        create_model_operations = [
            operation
            for operation in operations
            if isinstance(operation, migrations.CreateModel)
            and operation.name == "GHFDBParent"
        ]
        assert len(create_model_operations) == 1
        operation = create_model_operations[0]
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


def run_in_database(database, script):
    """Run a script with ``manage.py shell`` against a database.

    Args:
        database: The connection settings of the database to run against.
        script: The Python source to run.

    Returns:
        The last line the script printed.
    """
    environment = {
        key: value for key, value in os.environ.items() if key != "DATABASE_URL"
    }
    result = subprocess.run(
        [sys.executable, "manage.py", "shell"],
        input=script,
        cwd=settings.BASE_DIR,
        env={
            **environment,
            "DJANGO_ENV": "development",
            "POSTGRES_HOST": database["HOST"],
            "POSTGRES_PORT": str(database["PORT"]),
            "POSTGRES_USER": database["USER"],
            "POSTGRES_PASSWORD": database["PASSWORD"],
            "POSTGRES_DB": database["NAME"],
        },
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    return result.stdout.strip().splitlines()[-1]


# Builds the database as it stood before FairDM's located samples: samples linked to
# shared Points, two of them at one Point and one with none. Prints each sample's
# coordinates.
BEFORE_LOCATED_SAMPLES = """
import json
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

targets = [
    ("heat_flow", "0015_rename_intervalconductivity_location"),
    ("sample", "0011_index_modified"),
    ("fairdm_location", "0001_initial"),
]
for app, name in targets:
    call_command("migrate", app, name, verbosity=0)
apps = MigrationExecutor(connection).loader.project_state(targets).apps
Point = apps.get_model("fairdm_location", "Point")
Sample = apps.get_model("sample", "Sample")
HeatFlowSite = apps.get_model("heat_flow", "HeatFlowSite")
dataset = apps.get_model("dataset", "Dataset").objects.create(name="Before")

shared = Point.objects.create(x="-122.41942", y="37.77493")
HeatFlowSite.objects.create(name="Shared one", dataset=dataset, location=shared)
HeatFlowSite.objects.create(name="Shared two", dataset=dataset, location=shared)
HeatFlowSite.objects.create(
    name="South west",
    dataset=dataset,
    location=Point.objects.create(x="-179.99999", y="-89.99999"),
)
Sample.objects.create(
    name="Plain sample",
    dataset=dataset,
    location=Point.objects.create(x="8.40417", y="49.00937"),
)
Sample.objects.create(name="Nowhere", dataset=dataset)

print(json.dumps({
    sample.name: [str(sample.location.x), str(sample.location.y)]
    if sample.location else None
    for sample in Sample.objects.select_related("location")
}))
"""

# Applies every migration. Prints each sample's coordinates as five-decimal text with
# the point's SRID, and whether the copy set aside before the upgrade is still there.
AFTER_LOCATED_SAMPLES = """
import json
from django.core.management import call_command
from django.db import connection

call_command("migrate", verbosity=0)
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT name, round(ST_X(location)::numeric, 5)::text,"
        " round(ST_Y(location)::numeric, 5)::text, ST_SRID(location)"
        " FROM sample_sample"
    )
    rows = cursor.fetchall()
    cursor.execute("SELECT to_regclass('heat_flow_sample_coordinates')")
    (copy,) = cursor.fetchone()
print(json.dumps({
    "samples": {
        name: [x, y, srid] if x is not None else None for name, x, y, srid in rows
    },
    "copy": copy,
}))
"""


class TestLocatedSamplesKeepTheirCoordinates:
    # FairDM's ``sample/0012_located_samples`` drops the link to ``Point`` and adds an
    # empty point column. The portal's migrations around it carry every coordinate over.

    @pytest.mark.slow
    def test_every_sample_keeps_its_coordinates(self, empty_database):
        import json

        before = json.loads(run_in_database(empty_database, BEFORE_LOCATED_SAMPLES))
        after = json.loads(run_in_database(empty_database, AFTER_LOCATED_SAMPLES))

        assert after["samples"] == {
            name: [*coordinates, 4326] if coordinates else None
            for name, coordinates in before.items()
        }
        assert sum(value is not None for value in after["samples"].values()) == 4
        assert after["copy"] is None
