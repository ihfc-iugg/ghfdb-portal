"""
GHFDB export resource — produces a GHFDB-format XLSX from HeatFlow data.

Implements GHFDBExportResource which serialises the normalised relational
model back to the flat GHFDB spreadsheet format with:
  - All 62 columns in the canonical GHFDB_COLUMN_ORDER
  - Semicolon-joined labels for M2M fields
  - Plain SI numeric magnitudes for Pint quantity fields

Data source: GHFDB.objects.for_export() (annotated + prefetched queryset)

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from import_export import fields
from import_export.resources import ModelResource

from ._base import GHFDB_COLUMN_ORDER

# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _mag(value) -> float | str:
    """Return the float magnitude of a Pint Quantity, or '' for None/missing."""
    if value is None:
        return ""
    if hasattr(value, "magnitude"):
        mag = value.magnitude
        try:
            return float(mag)
        except (TypeError, ValueError):
            return str(mag)
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def _labels(qs) -> str:
    """Return semicolon-joined Concept labels from a related manager QuerySet."""
    if qs is None:
        return ""
    try:
        return "; ".join(getattr(c, "label", str(c)) for c in qs)
    except Exception:  # pragma: no cover — defensive guard for unexpected queryset types
        return ""


# ---------------------------------------------------------------------------
# GHFDBExportResource
# ---------------------------------------------------------------------------


class GHFDBExportResource(ModelResource):
    """
    Export resource for GHFDB flat-format XLSX.

    Produces a tablib Dataset containing one row per HeatFlow record with all
    62 GHFDB columns in ``GHFDB_COLUMN_ORDER`` sequence.  Pint quantity fields
    are rendered as plain SI numeric magnitudes; M2M vocabulary fields are
    rendered as semicolon-joined Concept labels.

    Usage::

        resource = GHFDBExportResource()
        dataset = resource.export()          # all records
        dataset = resource.export(qs)        # filtered subset

        Tested row limit: up to 50 000 rows without memory issues when combined
        with ``GHFDB.objects.for_export()``.

        Large-export guidance:
        - Keep queryset usage streaming-friendly (use ``.iterator()`` in custom
            export pipelines that bypass django-import-export internals).
        - For exports beyond the tested synchronous limit move to a background
            task (deferred to a future spec).

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global
          Heat Flow Database. Earth System Science Data.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    # -----------------------------------------------------------------------
    # Parent-level scalar fields
    # -----------------------------------------------------------------------
    q = fields.Field(attribute="p_q")
    q_uncertainty = fields.Field(attribute="p_q_uncertainty")

    # Site-level scalar fields
    name = fields.Field(attribute="site_name")
    lat_ns = fields.Field(attribute="lat_ns")
    long_ew = fields.Field(attribute="long_ew")
    elevation = fields.Field(attribute="site_elevation")
    environment = fields.Field(attribute="site_environment")
    p_comment = fields.Field(attribute="p_comment")
    corr_hp_flag = fields.Field(attribute="p_corr_hp_flag")
    total_depth_md = fields.Field(attribute="total_depth_md")
    total_depth_tvd = fields.Field(attribute="total_depth_tvd")
    explo_method = fields.Field(attribute="site_explo_method")

    # Site-level M2M
    explo_purpose = fields.Field(attribute=None)

    # -----------------------------------------------------------------------
    # Child-level scalar fields
    # -----------------------------------------------------------------------
    qc = fields.Field(attribute="value")
    qc_uncertainty = fields.Field(attribute="uncertainty")

    # Child-level M2M
    q_method = fields.Field(attribute=None)

    # Depth interval scalars
    q_top = fields.Field(attribute="interval_top")
    q_bottom = fields.Field(attribute="interval_bottom")

    # Probe metadata scalars
    probe_penetration = fields.Field(attribute="probe_penetration")

    # Unimplemented reference columns (placeholder — returns "")
    publication_reference = fields.Field(attribute=None)
    data_reference = fields.Field(attribute=None)

    # Child flags / metadata
    relevant_child = fields.Field(attribute="is_relevant")
    c_comment = fields.Field(attribute="c_comment")

    # Correction flag annotations
    corr_is_flag = fields.Field(attribute="corr_IS_flag")
    corr_t_flag = fields.Field(attribute="corr_T_flag")
    corr_s_flag = fields.Field(attribute="corr_S_flag")
    corr_e_flag = fields.Field(attribute="corr_E_flag")
    corr_topo_flag = fields.Field(attribute="corr_TOPO_flag")
    corr_pal_flag = fields.Field(attribute="corr_PAL_flag")
    corr_sur_flag = fields.Field(attribute="corr_SUR_flag")
    corr_conv_flag = fields.Field(attribute="corr_CONV_flag")
    corr_hr_flag = fields.Field(attribute="corr_HR_flag")

    expedition = fields.Field(attribute="expedition")

    # Marine probe M2M + scalars
    probe_type = fields.Field(attribute=None)
    probe_length = fields.Field(attribute="probe_length")
    probe_tilt = fields.Field(attribute="probe_tilt")
    water_temperature = fields.Field(attribute="water_temperature")

    # Geological context M2M (not yet mapped to model fields — returns "")
    geo_lithology = fields.Field(attribute=None)
    geo_stratigraphy = fields.Field(attribute=None)

    # -----------------------------------------------------------------------
    # Thermal gradient scalars and M2M
    # -----------------------------------------------------------------------
    t_grad_mean = fields.Field(attribute="tgrad_value")
    t_grad_uncertainty = fields.Field(attribute="tgrad_uncertainty")
    t_grad_mean_cor = fields.Field(attribute="tgrad_corrected")
    t_grad_uncertainty_cor = fields.Field(attribute="tgrad_corrected_unc")
    t_method_top = fields.Field(attribute=None)
    t_method_bottom = fields.Field(attribute=None)
    t_shutin_top = fields.Field(attribute="tgrad_shutin_top")
    t_shutin_bottom = fields.Field(attribute="tgrad_shutin_bottom")
    t_corr_top = fields.Field(attribute=None)
    t_corr_bottom = fields.Field(attribute=None)
    t_number = fields.Field(attribute="tgrad_number")

    q_date = fields.Field(attribute="date_acquired")

    # -----------------------------------------------------------------------
    # Thermal conductivity scalars and M2M
    # -----------------------------------------------------------------------
    tc_mean = fields.Field(attribute="tc_value")
    tc_uncertainty = fields.Field(attribute="tc_uncertainty")  # annotation name matches
    tc_source = fields.Field(attribute=None)
    tc_location = fields.Field(attribute=None)
    tc_method = fields.Field(attribute=None)
    tc_saturation = fields.Field(attribute=None)
    tc_pT_conditions = fields.Field(attribute=None)
    tc_pT_function = fields.Field(attribute=None)
    tc_number = fields.Field(attribute="tc_number")
    tc_strategy = fields.Field(attribute=None)

    # IGSN — not yet mapped to a model field (returns "")
    igsn = fields.Field(attribute=None)

    # -----------------------------------------------------------------------
    # T043: Pint quantity dehydrate methods
    # -----------------------------------------------------------------------

    def dehydrate_q(self, obj) -> float | str:
        return _mag(getattr(obj, "p_q", None))

    def dehydrate_q_uncertainty(self, obj) -> float | str:
        return _mag(getattr(obj, "p_q_uncertainty", None))

    def dehydrate_elevation(self, obj) -> float | str:
        return _mag(getattr(obj, "site_elevation", None))

    def dehydrate_total_depth_md(self, obj) -> float | str:
        return _mag(getattr(obj, "total_depth_md", None))

    def dehydrate_total_depth_tvd(self, obj) -> float | str:
        return _mag(getattr(obj, "total_depth_tvd", None))

    def dehydrate_qc(self, obj) -> float | str:
        return _mag(getattr(obj, "value", None))

    def dehydrate_qc_uncertainty(self, obj) -> float | str:
        return _mag(getattr(obj, "uncertainty", None))

    def dehydrate_q_top(self, obj) -> float | str:
        return _mag(getattr(obj, "interval_top", None))

    def dehydrate_q_bottom(self, obj) -> float | str:
        return _mag(getattr(obj, "interval_bottom", None))

    def dehydrate_probe_penetration(self, obj) -> float | str:
        return _mag(getattr(obj, "probe_penetration", None))

    def dehydrate_probe_length(self, obj) -> float | str:
        return _mag(getattr(obj, "probe_length", None))

    def dehydrate_probe_tilt(self, obj) -> float | str:
        return _mag(getattr(obj, "probe_tilt", None))

    def dehydrate_water_temperature(self, obj) -> float | str:
        return _mag(getattr(obj, "water_temperature", None))

    def dehydrate_t_grad_mean(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_value", None))

    def dehydrate_t_grad_uncertainty(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_uncertainty", None))

    def dehydrate_t_grad_mean_cor(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_corrected", None))

    def dehydrate_t_grad_uncertainty_cor(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_corrected_unc", None))

    def dehydrate_t_shutin_top(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_shutin_top", None))

    def dehydrate_t_shutin_bottom(self, obj) -> float | str:
        return _mag(getattr(obj, "tgrad_shutin_bottom", None))

    def dehydrate_tc_mean(self, obj) -> float | str:
        return _mag(getattr(obj, "tc_value", None))

    def dehydrate_tc_uncertainty(self, obj) -> float | str:
        return _mag(getattr(obj, "tc_uncertainty", None))

    # -----------------------------------------------------------------------
    # T044: M2M dehydrate methods
    # -----------------------------------------------------------------------

    def dehydrate_explo_purpose(self, obj) -> str:
        try:
            qs = obj.sample.heatflowinterval.sample.heatflowsite.explo_purpose.all()
            return _labels(qs)
        except AttributeError:
            return ""

    def dehydrate_q_method(self, obj) -> str:
        try:
            return _labels(obj.method.all())
        except AttributeError:
            return ""

    def dehydrate_probe_type(self, obj) -> str:
        try:
            return _labels(obj.sample.heatflowinterval.probe_metadata.probe_type.all())
        except AttributeError:
            return ""

    def dehydrate_t_method_top(self, obj) -> str:
        try:
            if obj.thermal_gradient is None:
                return ""
            return _labels(obj.thermal_gradient.method_top.all())
        except AttributeError:
            return ""

    def dehydrate_t_method_bottom(self, obj) -> str:
        try:
            if obj.thermal_gradient is None:
                return ""
            return _labels(obj.thermal_gradient.method_bottom.all())
        except AttributeError:
            return ""

    def dehydrate_t_corr_top(self, obj) -> str:
        try:
            if obj.thermal_gradient is None:
                return ""
            return _labels(obj.thermal_gradient.correction_top.all())
        except AttributeError:
            return ""

    def dehydrate_t_corr_bottom(self, obj) -> str:
        try:
            if obj.thermal_gradient is None:
                return ""
            return _labels(obj.thermal_gradient.correction_bottom.all())
        except AttributeError:
            return ""

    def dehydrate_tc_source(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.source.all())
        except AttributeError:
            return ""

    def dehydrate_tc_location(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.location.all())
        except AttributeError:
            return ""

    def dehydrate_tc_method(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.method.all())
        except AttributeError:
            return ""

    def dehydrate_tc_saturation(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.saturation.all())
        except AttributeError:
            return ""

    def dehydrate_tc_pT_conditions(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.pT_conditions.all())
        except AttributeError:
            return ""

    def dehydrate_tc_pT_function(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.pT_function.all())
        except AttributeError:
            return ""

    def dehydrate_tc_strategy(self, obj) -> str:
        try:
            if obj.thermal_conductivity is None:
                return ""
            return _labels(obj.thermal_conductivity.strategy.all())
        except AttributeError:
            return ""

    # Unimplemented / placeholder columns
    def dehydrate_publication_reference(self, obj) -> str:
        return ""

    def dehydrate_data_reference(self, obj) -> str:
        return ""

    def dehydrate_geo_lithology(self, obj) -> str:
        return ""

    def dehydrate_geo_stratigraphy(self, obj) -> str:
        return ""

    def dehydrate_igsn(self, obj) -> str:
        return ""

    # -----------------------------------------------------------------------
    # Queryset
    # -----------------------------------------------------------------------

    def get_queryset(self):
        from ..models import GHFDB

        return GHFDB.objects.for_export()

    # -----------------------------------------------------------------------
    # Meta
    # -----------------------------------------------------------------------

    class Meta:
        from ..models import GHFDB as _GHFDB

        model = _GHFDB
        # Restrict auto-discovery to exactly the 62 GHFDB columns; all columns are
        # declared explicitly above so auto-discovery produces no additional fields.
        fields = GHFDB_COLUMN_ORDER
        export_order = GHFDB_COLUMN_ORDER
