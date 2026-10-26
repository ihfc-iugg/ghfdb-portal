# The conductivity's location is renamed before FairDM's measurement 0015 declares a
# ``location`` field on Measurement, which would otherwise clash with it. Renaming a
# many-to-many field renames its through table, so every row is kept.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("heat_flow", "0003_heatflow_m_score_heatflow_u_score_and_more"),
    ]

    run_before = [
        ("measurement", "0015_located_measurements"),
    ]

    operations = [
        migrations.RenameField(
            model_name="intervalconductivity",
            old_name="location",
            new_name="conductivity_location",
        ),
    ]
