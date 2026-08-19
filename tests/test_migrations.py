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

from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings

PROJECT_APPS = ["heat_flow", "ghfdb", "review"]


@pytest.mark.django_db
# The suite runs with --nomigrations, which points every app at a stub module.
# Restore the real ones so the comparison has something to compare against.
@override_settings(MIGRATION_MODULES={})
def test_no_unrecorded_model_changes():
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
            f"`python manage.py makemigrations {' '.join(PROJECT_APPS)}`.\n{out.getvalue()}"
        )
