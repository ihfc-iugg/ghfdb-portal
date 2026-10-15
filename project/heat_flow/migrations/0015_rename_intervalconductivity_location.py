# The conductivity's location is renamed before FairDM declares a ``location`` field on
# Measurement. Renaming a many-to-many field renames its through table, so every row is kept.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("heat_flow", "0014_quality_scores"),
    ]

    operations = [
        migrations.RenameField(
            model_name="intervalconductivity",
            old_name="location",
            new_name="conductivity_location",
        ),
    ]
