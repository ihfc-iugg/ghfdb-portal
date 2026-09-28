# Tests for the review app's data migration creating its own group .

import importlib

import pytest
from django.apps import apps as real_apps
from django.contrib.auth.models import Group

MIGRATION_MODULE = "project.review.migrations.0002_data_assessor_group"


@pytest.mark.django_db
@pytest.mark.review
class TestCreateDataAssessorGroup:
    def test_creates_the_data_assessor_group(self):
        module = importlib.import_module(MIGRATION_MODULE)
        Group.objects.filter(name="Data Assessor").delete()

        module.create_group(real_apps, None)

        assert Group.objects.filter(name="Data Assessor").exists()

    def test_grants_no_model_permissions(self):
        module = importlib.import_module(MIGRATION_MODULE)
        Group.objects.filter(name="Data Assessor").delete()

        module.create_group(real_apps, None)

        assert not Group.objects.get(name="Data Assessor").permissions.exists()

    def test_running_it_twice_creates_the_group_only_once(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_group(real_apps, None)
        module.create_group(real_apps, None)

        assert Group.objects.filter(name="Data Assessor").count() == 1

    def test_reverse_removes_it(self):
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_group(real_apps, None)
        module.delete_group(real_apps, None)

        assert not Group.objects.filter(name="Data Assessor").exists()

    def test_it_does_not_touch_the_frameworks_own_curator_role(self):
        # The framework installs Data Curator with real permissions and refuses to
        # delete it. A second group of that name would either collide or quietly produce
        # a role holding none of them.
        module = importlib.import_module(MIGRATION_MODULE)

        module.create_group(real_apps, None)
        module.delete_group(real_apps, None)

        assert Group.objects.filter(name="Data Curator").exists()


WORKFLOW_FIELDS_MODULE = "project.review.migrations.0003_review_workflow_fields"


class TestStatusToStateMapping:
    # The old three-value ``status`` maps onto the new four-value ``state``.

    def test_every_old_status_value_maps_to_its_new_state(self):
        from review.states import States

        module = importlib.import_module(WORKFLOW_FIELDS_MODULE)

        assert module.STATUS_TO_STATE == {
            0: States.DESCRIBED,  # OPEN -> DESCRIBED
            1: States.AWAITING_DECISION,  # PENDING -> AWAITING_DECISION
            2: States.COMPLETE,  # COMPLETE -> COMPLETE
        }
