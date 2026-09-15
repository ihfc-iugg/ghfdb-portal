"""Create the Data Assessor and Data Curator groups (T005, data-model.md
"Groups").

A data migration rather than a fixture, so both groups exist in every
environment without a load step and without pinning ``auth.permission`` rows
by primary key — the defect ``ghfdb_review_group.json`` carried, which broke
whenever a migration reordered permissions and named its group in a case no
code in the repository looked for.

Grants no Django model permissions: access is decided by the two predicates
in ``review.permissions``, not by anything on these groups.
"""

from django.db import migrations

GROUP_NAMES = ["Data Assessor", "Data Curator"]


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in GROUP_NAMES:
        Group.objects.get_or_create(name=name)


def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_NAMES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("review", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]
