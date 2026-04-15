"""
GHFDB parent-level import resource (HeatFlowSite + ParentHeatFlow).

Implements GHFDBParentImportResource which reads the GHFDB XLSX spreadsheet
and creates/updates parent-level records:
  - HeatFlowSite (name, location, elevation, environment, etc.)
  - Point (geographic coordinates from lat_NS / long_EW)
  - ParentHeatFlow (value, uncertainty, comment, corr_HP_flag)

Upsert key: ParentHeatFlow.local_id <- spreadsheet column ID_parent

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from decimal import Decimal, InvalidOperation
from typing import cast

from heat_flow.models import HeatFlowSite, ParentHeatFlow
from import_export import fields
from import_export.resources import ModelResource

from ._widgets import ParentWidget, QuantityWidget, YesNoWidget


class GHFDBParentImportResource(ModelResource):
    """
    Import resource for GHFDB parent-level data.

    Parses the 18 PARENT_COLUMNS from the GHFDB spreadsheet and upserts
    ``ParentHeatFlow`` + ``HeatFlowSite`` records keyed on ``ID_parent``.
    """

    # Fields with direct model attribute mappings (field key == PARENT_COLUMNS entry)
    ID_parent = fields.Field(attribute="local_id", column_name="ID_parent")
    q = fields.Field(
        attribute="value",
        column_name="q",
        widget=QuantityWidget("mW/m^2"),
    )
    q_uncertainty = fields.Field(
        attribute="uncertainty",
        column_name="q_uncertainty",
        widget=QuantityWidget("mW/m^2"),
    )
    p_comment = fields.Field(
        attribute="comment",
        column_name="p_comment",
        default="",
    )
    corr_HP_flag = fields.Field(
        attribute="corr_HP_flag",
        column_name="corr_HP_flag",
        widget=YesNoWidget(),
        default="",
    )

    # Pass-through fields (no attribute) — values extracted from row by ParentWidget in
    # before_save_instance(); declared here so all PARENT_COLUMNS appear in resource.fields.
    name = fields.Field(column_name="name")
    lat_NS = fields.Field(column_name="lat_NS")
    long_EW = fields.Field(column_name="long_EW")
    elevation = fields.Field(column_name="elevation")
    environment = fields.Field(column_name="environment")
    total_depth_MD = fields.Field(column_name="total_depth_MD")
    total_depth_TVD = fields.Field(column_name="total_depth_TVD")
    explo_method = fields.Field(column_name="explo_method")
    explo_purpose = fields.Field(column_name="explo_purpose")
    Country = fields.Field(column_name="Country")
    Region = fields.Field(column_name="Region")
    Continent = fields.Field(column_name="Continent")
    Domain = fields.Field(column_name="Domain")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parent_widget = ParentWidget()
        self._fairdm_dataset = None

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def before_import(self, dataset, **kwargs):
        """Store the FairDM dataset and deduplicate rows by effective parent key."""
        from fairdm.core.models import Dataset as FairDataset

        self._fairdm_dataset = kwargs.get("fairdm_dataset") or FairDataset.objects.first()

        # Inject ID_parent column when the upload template omits it entirely.
        # _check_import_id_fields() runs after before_import(), so adding the column
        # here ensures header validation passes; before_import_row() fills each cell.
        if "ID_parent" not in (dataset.headers or []):
            dataset.append_col(["" for _ in range(len(dataset))], header="ID_parent")

        # Keep only the first occurrence of each effective parent key.
        # For template rows without ID_parent, use a deterministic location key.
        seen: set = set()
        rows_to_delete = []
        for i, row in enumerate(dataset.dict):
            effective_id = self._effective_parent_id(row)
            if effective_id in seen:
                rows_to_delete.append(i)
                continue
            seen.add(effective_id)

        for i in reversed(rows_to_delete):
            del dataset[i]

    def before_import_row(self, row, **kwargs):
        """Inject effective parent ID so import_id_fields can upsert template rows."""
        row["ID_parent"] = self._effective_parent_id(row)

    def before_save_instance(self, instance, row, **kwargs):
        """Save the HeatFlowSite (+ Point) and link it to the ParentHeatFlow."""
        if not instance.dataset_id:
            instance.dataset = self._fairdm_dataset

        id_parent = row.get("ID_parent") or ""
        site = self._get_or_create_site(id_parent, row)
        instance.sample = site

    def after_save_instance(self, instance, row, **kwargs):
        """Apply M2M relations (explo_purpose) to the site."""
        if instance.sample_id:
            self._parent_widget.set_m2m_relations(instance.sample)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_create_site(self, id_parent: str, row: dict) -> HeatFlowSite:
        """Return the HeatFlowSite for this parent row, creating it if needed."""
        from fairdm.contrib.location.models import Point

        # Parse the new site data from the row
        new_site = self._parent_widget.clean(row.get("name"), row=row)

        # Use Sample.local_id (inherited) to upsert the site
        if id_parent:
            try:
                site = HeatFlowSite.objects.get(local_id=id_parent)
            except HeatFlowSite.DoesNotExist:
                site = new_site or HeatFlowSite()
                site.local_id = id_parent
        else:
            site = new_site or HeatFlowSite()

        # Apply field updates from the row data
        if new_site is not None:
            for field_name in [
                "name",
                "environment",
                "explo_method",
                "elevation",
                "length",
                "vertical_depth",
                "country",
                "region",
                "continent",
                "domain",
            ]:
                setattr(site, field_name, getattr(new_site, field_name))

            # Get or create the Point for the coordinates
            if new_site.location is not None:
                point, _ = Point.objects.get_or_create(
                    x=new_site.location.x,
                    y=new_site.location.y,
                )
                site.location = point

        if not site.dataset_id:
            site.dataset = self._fairdm_dataset

        site.save()
        return cast(HeatFlowSite, site)

    def _effective_parent_id(self, row: dict) -> str:
        """Return ID_parent, or a deterministic synthetic key for no-ID rows."""
        explicit_id = str(row.get("ID_parent") or "").strip()
        if explicit_id:
            return explicit_id

        lat = self._normalize_decimal(row.get("lat_NS"))
        lon = self._normalize_decimal(row.get("long_EW"))
        return f"AUTO_PARENT:{lat}:{lon}"

    def _normalize_decimal(self, value) -> str:
        """Normalize decimal-like values so equivalent numerics map to one key."""
        raw = str(value or "").strip()
        if not raw:
            return ""
        try:
            dec = Decimal(raw)
        except (InvalidOperation, ValueError):
            return raw.lower()
        normalized = dec.normalize()
        return format(normalized, "f")

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    class Meta:
        model = ParentHeatFlow
        import_id_fields = ("ID_parent",)
        use_transactions = True
        rollback_on_validation_errors = True
        fields = (
            "ID_parent",
            "q",
            "q_uncertainty",
            "p_comment",
            "corr_HP_flag",
            "name",
            "lat_NS",
            "long_EW",
            "elevation",
            "environment",
            "total_depth_MD",
            "total_depth_TVD",
            "explo_method",
            "explo_purpose",
            "Country",
            "Region",
            "Continent",
            "Domain",
        )
