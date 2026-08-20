"""The portal's own applications must have no unrecorded model changes.

``GHFDBParent`` was written, registered in the admin and left without a
migration, so ``makemigrations`` reported pending changes for months and the
model's admin permissions were never created.  Nothing failed, because nothing
looked.

The check is scoped to ``heat_flow``, ``ghfdb`` and ``review``.  Installed
packages are excluded deliberately: at least one third-party application ships
model state its own migrations do not cover, and we cannot add a migration to
someone else's package.
"""

import os
from io import StringIO

import pytest
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
        """Every model change in the portal's applications has a migration."""
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


class TestMigrationsApplyToAnEmptyDatabase:
    """The migrations must actually run, not merely exist.

    The suite runs with ``--nomigrations``, which points every app at a stub module, so
    no test in this repository has ever applied a migration.  ``makemigrations --check``
    above proves the migrations describe the models; it cannot prove they execute.  A
    migration that is unrecorded and one that is recorded and broken look identical from
    inside a test database built straight from model state.

    So this migrates into an empty file, in a subprocess, and asserts on the tables that
    come out rather than on a return code.  The subprocess is not incidental: the
    development settings hard-wire the SQLite path, so the only way to redirect it is a
    second connection the settings define when the environment names a file for it.
    """

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
    @pytest.mark.skip(
        reason=(
            "Blocked upstream: the migration graph cannot be applied to an empty "
            "database. contributors.0008_migrate_to_location_model, in the fairdm "
            "package, reads contributors_organization.lat in a RunPython step and drops "
            "the column in the step after it, so it passes against a database that "
            "already carries the older schema and fails against one that never did. "
            "Raised as FAIR-DM/fairdm#252. Nothing in this repository can fix it, and "
            "nothing here works around it. Un-skip when that issue closes."
        )
    )
    def test_migrations_build_every_heat_flow_table(self, tmp_path):
        """Applying the whole migration graph to an empty database builds all eight tables."""
        import sqlite3
        import subprocess
        import sys
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[1]
        database = tmp_path / "migrated.sqlite3"

        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "migrate",
                "--database",
                "migration_check",
                "--noinput",
                "-v",
                "0",
            ],
            cwd=repo_root,
            env={**os.environ, "MIGRATION_CHECK_DATABASE": str(database)},
            capture_output=True,
            text=True,
        )

        assert database.exists(), (
            "migrate produced no database at the path it was given."
            f"\n{result.stdout}\n{result.stderr}"
        )

        with sqlite3.connect(database) as connection:
            built = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }

        missing = [table for table in self.HEAT_FLOW_TABLES if table not in built]
        assert not missing, (
            f"Migrations left these tables unbuilt: {missing}."
            f"\n{result.stdout}\n{result.stderr}"
        )
