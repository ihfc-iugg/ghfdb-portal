"""Tests for the review app's data migration creating its two groups (T005).

The suite runs with ``--nomigrations`` (tests/README.md), so the migration's
``RunPython`` function is imported and called directly against the real
model classes, the same pattern
``tests/test_ghfdb/migrations/0003_ghfdbchild_ghfdbparent.py`` established.
"""

import importlib

import pytest
from django.apps import apps as real_apps
from django.contrib.auth.models import Group

MIGRATION_MODULE = "project.review.migrations.0002_data_assessor_and_data_curator_groups"


@pytest.mark.django_db
@pytest.mark.review
class TestCreateReviewGroups:
    def test_creates_the_data_assessor_and_data_curator_groups(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_groups(real_apps, None)

        assert Group.objects.filter(name="Data Assessor").exists()
        assert Group.objects.filter(name="Data Curator").exists()

    def test_grants_no_model_permissions(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_groups(real_apps, None)

        for name in ("Data Assessor", "Data Curator"):
            group = Group.objects.get(name=name)
            assert not group.permissions.exists()

    def test_running_it_twice_creates_each_group_only_once(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_groups(real_apps, None)
        module.create_groups(real_apps, None)

        assert Group.objects.filter(name="Data Assessor").count() == 1
        assert Group.objects.filter(name="Data Curator").count() == 1

    def test_reverse_removes_both_groups(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_groups(real_apps, None)
        module.delete_groups(real_apps, None)

        assert not Group.objects.filter(
            name__in=["Data Assessor", "Data Curator"]
        ).exists()


WORKFLOW_FIELDS_MODULE = "project.review.migrations.0003_review_workflow_fields"


class TestStatusToStateMapping:
    """T006: the old three-value ``status`` maps onto the new four-value
    ``state``. The suite runs with ``--nomigrations`` (tests/README.md), so
    the test database is built straight from the current model and has no
    ``status`` column left to migrate data out of — the mapping table this
    migration's ``RunPython`` reads from is what a test can pin directly."""

    def test_every_old_status_value_maps_to_its_new_state(self):
        from review.states import States

        module = importlib.import_module(WORKFLOW_FIELDS_MODULE)

        assert module.STATUS_TO_STATE == {
            0: States.DESCRIBED,  # OPEN -> DESCRIBED
            1: States.AWAITING_DECISION,  # PENDING -> AWAITING_DECISION
            2: States.COMPLETE,  # COMPLETE -> COMPLETE
        }
