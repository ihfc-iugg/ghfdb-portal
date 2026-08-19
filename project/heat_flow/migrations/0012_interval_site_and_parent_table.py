"""Rename the interval-to-site link and give ParentHeatFlow its default table.

``HeatFlowInterval.sample`` becomes ``site`` and is retyped from the polymorphic
``Sample`` root to ``HeatFlowSite``, which is what it has always held.
``ParentHeatFlow`` drops the ``ghfdb_parentheatflow`` table override left over
from an abandoned plan to move the model into the ``ghfdb`` application, so it
takes the default ``heat_flow_parentheatflow``.  Both index names are derived
from the table name and are renamed to match.
"""

import auto_prefetch
import django.db.models.deletion
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("heat_flow", "0011_ghfdb_id_rename_and_quality_nullable"),
    ]

    operations = [
        migrations.RenameField(
            model_name="heatflowinterval",
            old_name="sample",
            new_name="site",
        ),
        migrations.AlterField(
            model_name="heatflowinterval",
            name="site",
            field=auto_prefetch.ForeignKey(
                blank=True,
                help_text="The heat flow site this depth interval belongs to.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="intervals",
                to="heat_flow.heatflowsite",
                verbose_name="site",
            ),
        ),
        migrations.RenameIndex(
            model_name="parentheatflow",
            new_name="heat_flow_p_ghfdb_i_550af7_idx",
            old_name="ghfdb_paren_ghfdb_i_6b75a3_idx",
        ),
        migrations.RenameIndex(
            model_name="parentheatflow",
            new_name="heat_flow_p_corr_HP_1024a1_idx",
            old_name="ghfdb_paren_corr_HP_e744cb_idx",
        ),
        migrations.AlterModelTable(
            name="parentheatflow",
            table=None,
        ),
    ]
