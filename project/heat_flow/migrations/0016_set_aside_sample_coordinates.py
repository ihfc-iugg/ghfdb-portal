# FairDM's ``sample/0012_located_samples`` replaces a sample's link to a shared
# ``Point`` with a point of its own, and does so by dropping the old column and adding
# an empty one. Every site in this portal is placed by that link, so the coordinates are
# copied aside here, before the column goes, and written back by
# ``0017_restore_sample_coordinates``.
#
# Forward only in effect: going back drops the copy, which holds nothing the database
# does not still have while ``sample/0012`` is unapplied.

from django.db import migrations

COPY_TABLE = "heat_flow_sample_coordinates"


def set_aside(apps, schema_editor):
    """Copy the longitude and latitude of every sample that has a location."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            f"CREATE TABLE {COPY_TABLE} AS"
            " SELECT sample.id AS sample_id, point.x AS longitude, point.y AS latitude"
            " FROM sample_sample AS sample"
            " JOIN fairdm_location_point AS point ON point.id = sample.location_id"
        )
        cursor.execute(f"ALTER TABLE {COPY_TABLE} ADD PRIMARY KEY (sample_id)")


def drop_copy(apps, schema_editor):
    """Drop the copy, which the database no longer needs once the link is back."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {COPY_TABLE}")


class Migration(migrations.Migration):
    dependencies = [
        ("heat_flow", "0015_rename_intervalconductivity_location"),
        ("sample", "0011_index_modified"),
        ("fairdm_location", "0001_initial"),
    ]

    run_before = [
        ("sample", "0012_located_samples"),
    ]

    operations = [
        migrations.RunPython(set_aside, drop_copy),
    ]
