# Writes back the coordinates ``0016_set_aside_sample_coordinates`` copied before
# FairDM's ``sample/0012_located_samples`` emptied the ``location`` column, as a WGS 84
# point on each sample, then drops the copy.
#
# Forward only. There is no way back: the reverse of ``sample/0012`` restores an empty
# link, so undoing this step would lose every coordinate, and Django refuses to reverse
# it.

from django.db import migrations

COPY_TABLE = "heat_flow_sample_coordinates"


def restore(apps, schema_editor):
    """Place every sample at its copied coordinates, and check that none was missed."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"SELECT count(*) FROM {COPY_TABLE}")
        (copied,) = cursor.fetchone()
        cursor.execute(
            "UPDATE sample_sample AS sample"
            " SET location = ST_SetSRID("
            "ST_MakePoint(copy.longitude::float8, copy.latitude::float8), 4326)"
            f" FROM {COPY_TABLE} AS copy"
            " WHERE sample.id = copy.sample_id"
        )
        restored = cursor.rowcount
        if restored != copied:
            raise RuntimeError(
                f"{copied} sample coordinates were set aside and {restored} were "
                f"written back. The copy is kept in {COPY_TABLE}."
            )
        cursor.execute(f"DROP TABLE {COPY_TABLE}")


class Migration(migrations.Migration):
    dependencies = [
        ("heat_flow", "0016_set_aside_sample_coordinates"),
        ("sample", "0012_located_samples"),
    ]

    operations = [
        migrations.RunPython(restore),
    ]
