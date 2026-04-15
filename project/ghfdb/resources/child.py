"""
GHFDB child-level import resource (HeatFlow + related measurements).

Implements GHFDBChildImportResource which reads the GHFDB XLSX spreadsheet
and creates/updates child-level records:
  - HeatFlowInterval (depth interval)
  - HeatFlow (child measurement)
  - ThermalGradient (optional, sentinel: T_grad_mean)
  - IntervalConductivity (optional, sentinel: tc_mean)
  - ProbeMetadata (optional, created in after_save_instance)
  - HeatFlowCorrection x 9 (created in after_save_instance via CORRECTION_COL_MAP)

Upsert key: HeatFlow.local_id <- spreadsheet column ID

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from decimal import Decimal, InvalidOperation

from heat_flow.models import HeatFlow, ParentHeatFlow
from import_export import fields
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from ._base import CORRECTION_COL_MAP
from ._widgets import (
    ConductivityWidget,
    GradientWidget,
    IntervalWidget,
    MultiConceptWidget,
    QuantityWidget,
    YesNoWidget,
)


class GHFDBChildImportResource(ModelResource):
    """
    Import resource for GHFDB child-level data.

    Processes all child columns from the GHFDB spreadsheet and upserts
    ``HeatFlow`` records keyed on ``ID``.  Related objects (HeatFlowInterval,
    ThermalGradient, IntervalConductivity, HeatFlowCorrection, ProbeMetadata)
    are created or updated in ``before_save_instance`` / ``after_save_instance``.
    """

    local_id = fields.Field(attribute="local_id", column_name="ID")
    qc = fields.Field(
        attribute="value",
        column_name="qc",
        widget=QuantityWidget("mW/m^2"),
    )
    qc_uncertainty = fields.Field(
        attribute="uncertainty",
        column_name="qc_uncertainty",
        widget=QuantityWidget("mW/m^2"),
    )
    parent = fields.Field(
        attribute="parent",
        column_name="ID_parent",
        widget=ForeignKeyWidget(ParentHeatFlow, field="local_id"),
    )
    relevant_child = fields.Field(
        attribute="is_relevant",
        column_name="relevant_child",
        widget=YesNoWidget(),
        default="",
    )
    c_comment = fields.Field(attribute="c_comment", column_name="c_comment", default="")
    expedition = fields.Field(attribute="expedition", column_name="expedition", default="")
    water_temperature = fields.Field(
        attribute="water_temperature",
        column_name="water_temperature",
        widget=QuantityWidget("°C"),
    )
    q_date = fields.Field(attribute="date_acquired", column_name="q_date", default="")

    # Pass-through fields (no attribute) — values extracted from row by hooks/widgets.
    # Declared here so all GHFDB child columns appear in resource.fields for schema coverage.
    # import_field() short-circuits when attribute is None, so these are always no-ops.
    lat_ns = fields.Field(column_name="lat_NS")
    long_ew = fields.Field(column_name="long_EW")
    corr_hp_flag = fields.Field(column_name="corr_HP_flag")
    total_depth_md = fields.Field(column_name="total_depth_MD")
    total_depth_tvd = fields.Field(column_name="total_depth_TVD")
    q_method = fields.Field(column_name="q_method")
    q_top = fields.Field(column_name="q_top")
    q_bottom = fields.Field(column_name="q_bottom")
    probe_penetration = fields.Field(column_name="probe_penetration")
    probe_length = fields.Field(column_name="probe_length")
    probe_tilt = fields.Field(column_name="probe_tilt")
    probe_type = fields.Field(column_name="probe_type")
    publication_reference = fields.Field(column_name="publication_reference")
    data_reference = fields.Field(column_name="data_reference")
    corr_is_flag = fields.Field(column_name="corr_IS_flag")
    corr_t_flag = fields.Field(column_name="corr_T_flag")
    corr_s_flag = fields.Field(column_name="corr_S_flag")
    corr_e_flag = fields.Field(column_name="corr_E_flag")
    corr_topo_flag = fields.Field(column_name="corr_TOPO_flag")
    corr_pal_flag = fields.Field(column_name="corr_PAL_flag")
    corr_sur_flag = fields.Field(column_name="corr_SUR_flag")
    corr_conv_flag = fields.Field(column_name="corr_CONV_flag")
    corr_hr_flag = fields.Field(column_name="corr_HR_flag")
    geo_lithology = fields.Field(column_name="geo_lithology")
    geo_stratigraphy = fields.Field(column_name="geo_stratigraphy")
    t_grad_mean = fields.Field(column_name="T_grad_mean")
    t_grad_uncertainty = fields.Field(column_name="T_grad_uncertainty")
    t_grad_mean_cor = fields.Field(column_name="T_grad_mean_cor")
    t_grad_uncertainty_cor = fields.Field(column_name="T_grad_uncertainty_cor")
    t_method_top = fields.Field(column_name="T_method_top")
    t_method_bottom = fields.Field(column_name="T_method_bottom")
    t_shutin_top = fields.Field(column_name="T_shutin_top")
    t_shutin_bottom = fields.Field(column_name="T_shutin_bottom")
    t_corr_top = fields.Field(column_name="T_corr_top")
    t_corr_bottom = fields.Field(column_name="T_corr_bottom")
    t_number = fields.Field(column_name="T_number")
    tc_mean = fields.Field(column_name="tc_mean")
    tc_uncertainty = fields.Field(column_name="tc_uncertainty")
    tc_source = fields.Field(column_name="tc_source")
    tc_location = fields.Field(column_name="tc_location")
    tc_method = fields.Field(column_name="tc_method")
    tc_saturation = fields.Field(column_name="tc_saturation")
    tc_pT_conditions = fields.Field(column_name="tc_pT_conditions")
    tc_pT_function = fields.Field(column_name="tc_pT_function")
    tc_number = fields.Field(column_name="tc_number")
    tc_strategy = fields.Field(column_name="tc_strategy")
    igsn = fields.Field(column_name="igsn")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._interval_widget = IntervalWidget()
        self._gradient_widget = GradientWidget()
        self._conductivity_widget = ConductivityWidget()
        self._fairdm_dataset = None

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def before_import(self, dataset, **kwargs):
        """Store the FairDM dataset reference for use during row processing."""
        from fairdm.core.models import Dataset as FairDataset

        self._fairdm_dataset = kwargs.get("fairdm_dataset") or FairDataset.objects.first()

        # Inject optional ID / ID_parent columns when the upload template omits them.
        # _check_import_id_fields() runs after before_import(), so injecting here
        # ensures header validation passes; before_import_row() fills each cell.
        for col_name in ("ID", "ID_parent"):
            if col_name not in (dataset.headers or []):
                dataset.append_col(["" for _ in range(len(dataset))], header=col_name)

    def before_import_row(self, row, **kwargs):
        """Inject effective IDs so no-ID template rows follow deterministic upsert."""
        row["ID_parent"] = self._effective_parent_id(row)
        row["ID"] = self._effective_child_id(row)

    def before_save_instance(self, instance, row, **kwargs):
        """
        Save the HeatFlowInterval and optional sub-measurements, then link them
        to the HeatFlow instance.
        """
        if not instance.dataset_id:
            instance.dataset = self._fairdm_dataset

        # Determine the parent HeatFlowSite for the interval
        parent_hf = instance.parent
        heat_flow_site = parent_hf.sample if parent_hf else None

        # --- HeatFlowInterval ---
        interval = self._build_interval(row, heat_flow_site)
        instance.sample = interval

        # --- ThermalGradient (sentinel: T_grad_mean) ---
        gradient = self._build_gradient(row, interval)
        instance.thermal_gradient = gradient

        # --- IntervalConductivity (sentinel: tc_mean) ---
        conductivity = self._build_conductivity(row, interval)
        instance.thermal_conductivity = conductivity

    def after_save_instance(self, instance, row, **kwargs):
        """Create HeatFlowCorrection + ProbeMetadata; set interval M2M fields."""
        self._create_corrections(instance, row)
        self._create_probe_metadata(instance, row)

        # Apply M2M relations to sub-measurements
        interval = instance.sample
        if interval and interval.pk:
            self._interval_widget.set_m2m_relations(interval)
            if instance.thermal_gradient and instance.thermal_gradient.pk:
                self._gradient_widget.set_m2m_relations(instance.thermal_gradient)
            if instance.thermal_conductivity and instance.thermal_conductivity.pk:
                self._conductivity_widget.set_m2m_relations(instance.thermal_conductivity)

        # HeatFlow M2M: q_method
        from heat_flow import vocabularies

        q_method_raw = row.get("q_method", "")
        if q_method_raw:
            widget = MultiConceptWidget(vocabularies.HeatFlowMethod)
            qs = widget.clean(q_method_raw, row=row)
            if qs is not None:
                instance.method.set(qs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_interval(self, row, heat_flow_site):
        """Create and save the HeatFlowInterval for this child row."""
        from heat_flow.models import HeatFlowInterval

        # Re-use stored widget to ensure _last_row is available for set_m2m_relations
        interval_unsaved = self._interval_widget.clean(None, row=row)
        if interval_unsaved is None:
            interval_unsaved = HeatFlowInterval()

        interval_unsaved.dataset = self._fairdm_dataset
        interval_unsaved.sample = heat_flow_site
        interval_unsaved.save()
        return interval_unsaved

    def _build_gradient(self, row, interval):
        """Create and save a ThermalGradient if T_grad_mean is non-empty."""
        gradient = self._gradient_widget.clean(row.get("T_grad_mean"), row=row)
        if gradient is None:
            return None
        gradient.dataset = self._fairdm_dataset
        gradient.sample = interval
        gradient.save()
        return gradient

    def _build_conductivity(self, row, interval):
        """Create and save an IntervalConductivity if tc_mean is non-empty."""
        conductivity = self._conductivity_widget.clean(row.get("tc_mean"), row=row)
        if conductivity is None:
            return None
        conductivity.dataset = self._fairdm_dataset
        conductivity.sample = interval
        conductivity.save()
        return conductivity

    def _create_corrections(self, instance, row):
        """Create/update all 9 HeatFlowCorrection records for this HeatFlow."""
        from heat_flow.models import HeatFlowCorrection

        for col_name, correction_type in CORRECTION_COL_MAP.items():
            raw = row.get(col_name, "")
            status = self._parse_correction_status(raw)
            HeatFlowCorrection.objects.update_or_create(
                heat_flow=instance,
                correction_type=correction_type,
                defaults={"status": status},
            )

    def _parse_correction_status(self, raw: str) -> str:
        """Map a raw correction flag value to a HeatFlowCorrection.StatusChoices key."""
        from heat_flow.models import HeatFlowCorrection

        StatusChoices = HeatFlowCorrection.StatusChoices
        unspecified = str(StatusChoices.UNSPECIFIED)
        present_corrected = str(StatusChoices.PRESENT_CORRECTED)

        if not raw:
            return unspecified
        # Accept direct status values
        valid_values = {str(v) for v, _ in StatusChoices.choices}
        if raw in valid_values:
            return raw
        # Map Yes/No shorthands
        if raw.lower() in ("yes", "1", "true"):
            return present_corrected
        return unspecified

    def _create_probe_metadata(self, instance, row):
        """Create or update ProbeMetadata when probe columns are non-empty."""
        probe_penetration = row.get("probe_penetration", "")
        probe_length = row.get("probe_length", "")
        probe_tilt = row.get("probe_tilt", "")
        if not any([probe_penetration, probe_length, probe_tilt]):
            return

        from heat_flow.models import ProbeMetadata
        from quantityfield.units import ureg

        def _qty(val, unit):
            if val:
                try:
                    return ureg.Quantity(float(val), unit)
                except (ValueError, TypeError):
                    pass
            return None

        ProbeMetadata.objects.update_or_create(
            interval=instance.sample,
            defaults={
                "penetration": _qty(probe_penetration, "m"),
                "length": _qty(probe_length, "m"),
                "tilt": _qty(probe_tilt, "°"),
            },
        )

    def _effective_parent_id(self, row: dict) -> str:
        """Return ID_parent, or a deterministic location key for no-ID template rows."""
        explicit_id = str(row.get("ID_parent") or "").strip()
        if explicit_id:
            return explicit_id

        lat = self._normalize_decimal(row.get("lat_NS"))
        lon = self._normalize_decimal(row.get("long_EW"))
        return f"AUTO_PARENT:{lat}:{lon}"

    def _effective_child_id(self, row: dict) -> str:
        """Return ID, or a deterministic natural-key ID for no-ID template rows."""
        explicit_id = str(row.get("ID") or "").strip()
        if explicit_id:
            return explicit_id

        lat = self._normalize_decimal(row.get("lat_NS"))
        lon = self._normalize_decimal(row.get("long_EW"))
        q_top = self._normalize_decimal(row.get("q_top"))
        q_bottom = self._normalize_decimal(row.get("q_bottom"))
        publication_reference = str(row.get("publication_reference") or "").strip().lower()
        return f"AUTO_CHILD:{lat}:{lon}:{q_top}:{q_bottom}:{publication_reference}"

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
        model = HeatFlow
        import_id_fields = ("local_id",)
        use_transactions = True
        rollback_on_validation_errors = True
        fields = (
            "local_id",
            "qc",
            "qc_uncertainty",
            "parent",
            "relevant_child",
            "c_comment",
            "expedition",
            "water_temperature",
            "q_date",
            "lat_ns",
            "long_ew",
            "corr_hp_flag",
            "total_depth_md",
            "total_depth_tvd",
            "q_method",
            "q_top",
            "q_bottom",
            "probe_penetration",
            "probe_length",
            "probe_tilt",
            "probe_type",
            "publication_reference",
            "data_reference",
            "corr_is_flag",
            "corr_t_flag",
            "corr_s_flag",
            "corr_e_flag",
            "corr_topo_flag",
            "corr_pal_flag",
            "corr_sur_flag",
            "corr_conv_flag",
            "corr_hr_flag",
            "geo_lithology",
            "geo_stratigraphy",
            "t_grad_mean",
            "t_grad_uncertainty",
            "t_grad_mean_cor",
            "t_grad_uncertainty_cor",
            "t_method_top",
            "t_method_bottom",
            "t_shutin_top",
            "t_shutin_bottom",
            "t_corr_top",
            "t_corr_bottom",
            "t_number",
            "tc_mean",
            "tc_uncertainty",
            "tc_source",
            "tc_location",
            "tc_method",
            "tc_saturation",
            "tc_pT_conditions",
            "tc_pT_function",
            "tc_number",
            "tc_strategy",
            "igsn",
        )
