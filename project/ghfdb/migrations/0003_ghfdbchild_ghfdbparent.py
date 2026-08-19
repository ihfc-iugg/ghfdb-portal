"""Rename the ``GHFDB`` proxy to ``GHFDBChild`` and record ``GHFDBParent``.

Both models are proxies, so neither operation touches a table.  ``GHFDBParent``
has existed in the code and in the admin since it was written but was never
recorded in a migration, which left ``makemigrations`` permanently dirty and
meant its admin permissions were never created.

Renaming a model does not rename the permissions built on it, so the codenames
are carried over explicitly.  Without that, any group holding ``view_ghfdb``
would keep a row the admin no longer looks for.
"""

import django.db.models.manager
from django.db import migrations

RENAMED_PERMISSIONS = {
    f"{action}_ghfdb": f"{action}_ghfdbchild"
    for action in ("add", "change", "delete", "view")
}


def rename_permissions(apps, schema_editor):
    _move_permissions(apps, RENAMED_PERMISSIONS)


def restore_permissions(apps, schema_editor):
    _move_permissions(apps, {new: old for old, new in RENAMED_PERMISSIONS.items()})


def _move_permissions(apps, mapping):
    """Repoint permission codenames on the proxy's content type."""
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    content_type = ContentType.objects.filter(
        app_label="ghfdb", model__in=("ghfdb", "ghfdbchild")
    ).first()
    if content_type is None:
        return

    permissions = Permission.objects.filter(content_type=content_type)
    for old_codename, new_codename in mapping.items():
        if permissions.filter(codename=new_codename).exists():
            continue
        permissions.filter(codename=old_codename).update(codename=new_codename)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("ghfdb", "0002_ghfdb"),
        ("heat_flow", "0012_interval_site_and_parent_table"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GHFDB",
            new_name="GHFDBChild",
        ),
        migrations.RunPython(rename_permissions, restore_permissions),
        migrations.CreateModel(
            name="GHFDBParent",
            fields=[],
            options={
                "verbose_name": "GHFDB Parent",
                "verbose_name_plural": "GHFDB Parents",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("heat_flow.parentheatflow",),
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
    ]
