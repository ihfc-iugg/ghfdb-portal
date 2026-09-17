"""Create the Data Assessor group (T005, data-model.md "Groups").

A data migration rather than a fixture, so the group exists in every
environment without a load step and without pinning ``auth.permission`` rows by
primary key — the defect ``ghfdb_review_group.json`` carried, which broke
whenever a migration reordered permissions and named its group in a case no
code in the repository looked for.

**Data Curator is not created here.** The framework ships it as one of its own
portal roles, with the permissions that role carries, and refuses to delete it.
Creating a second group of that name would either collide or quietly produce a
role with none of the framework's permissions, depending on which ran first.
Data Assessor has no framework counterpart and is ours.

Grants no Django model permissions: who may reach this application's pages is
decided by the predicates in ``review.permissions``.
"""

from django.db import migrations

GROUP_NAME = "Data Assessor"


def create_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=GROUP_NAME)


def delete_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("review", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_group, delete_group),
    ]
