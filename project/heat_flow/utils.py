# import pandas as pd
# from django.contrib.staticfiles import finders
from django_pandas.managers import DataFrameManager

GHFDB_field_map = [
    ("parent_id", "parent__id"),
    ("q", "parent__value"),
    ("q_uncertainty", "parent__uncertainty"),
    ("name", "parent__sample__name"),
    ("lat_NS", "parent__sample__location__y"),
    ("lon_EW", "parent__sample__location__x"),
    ("elevation", "parent__sample__location__elevation"),
    ("environment", "parent__sample__environment"),
    # ("p_comment", "parent__sample__comment"),
    ("corr_HP_flag", "parent__sample__corr_HP_flag"),
    ("total_depth_MD", "parent__sample__length"),
    ("total_depth_TVD", "parent__sample__vertical_depth"),
    ("explo_method", "parent__sample__explo_method"),
    ("explo_purpose", "parent__sample__explo_purpose"),
    ("qc", "value"),
    ("qc_uncertainty", "uncertainty"),
    ("q_method", "method"),
    ("q_top", "top"),
    ("q_bottom", "bottom"),
    ("probe_penetration", "probe_penetration"),
    ("publication_reference", "sample__dataset__reference"),
    ("data_reference", "sample__dataset__reference"),
    ("relevant_child", "relevant_child"),
    ("c_comment", "c_comment"),
    ("corr_IS_flag", "corr_IS_flag"),
    ("corr_T_flag", "corr_T_flag"),
    ("corr_S_flag", "corr_S_flag"),
    ("corr_E_flag", "corr_E_flag"),
    ("corr_TOPO_flag", "corr_TOPO_flag"),
    ("corr_PAL_flag", "corr_PAL_flag"),
    ("corr_SUR_flag", "corr_SUR_flag"),
    ("corr_CONV_flag", "corr_CONV_flag"),
    ("corr_HR_flag", "corr_HR_flag"),
    ("expedition", "expedition"),
    ("probe_type", "probe_type"),
    ("probe_length", "probe_length"),
    ("probe_tilt", "probe_tilt"),
    ("water_temperature", "water_temperature"),
    ("geo_lithology", "sample__lithology"),
    ("geo_stratigraphy", "sample__age"),
    ("T_grad_mean", "temperature_gradient__mean"),
    ("T_grad_uncertainty", "temperature_gradient__uncertainty"),
    ("T_grad_mean_cor", "temperature_gradient__corrected_mean"),
    ("T_grad_uncertainty_cor", "temperature_gradient__corrected_uncertainty"),
    ("T_method_top", "temperature_gradient__method_top"),
    ("T_method_bottom", "temperature_gradient__method_bottom"),
    ("T_shutin_top", "temperature_gradient__shutin_top"),
    ("T_shutin_bottom", "temperature_gradient__shutin_bottom"),
    ("T_corr_top", "temperature_gradient__correction_top"),
    ("T_corr_bottom", "temperature_gradient__correction_bottom"),
    ("T_number", "temperature_gradient__number"),
    # ("q_date", "parent__sample__date"),
    ("tc_mean", "thermal_conductivity__mean"),
    ("tc_uncertainty", "thermal_conductivity__uncertainty"),
    ("tc_source", "thermal_conductivity__source"),
    ("tc_location", "thermal_conductivity__location"),
    ("tc_method", "thermal_conductivity__method"),
    ("tc_saturation", "thermal_conductivity__saturation"),
    ("tc_pT_conditions", "thermal_conductivity__pT_conditions"),
    ("tc_pT_function", "thermal_conductivity__pT_function"),
    ("tc_number", "thermal_conductivity__number"),
    ("tc_strategy", "thermal_conductivity__strategy"),
    # ("Ref_IGSN", "sample__dataset__reference"),
]

GHFDB_db_fields = [field[1] for field in GHFDB_field_map]
GHFDB_csv_fields = [field[0] for field in GHFDB_field_map]


class GHFDB(DataFrameManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "parent",
                "parent__sample",
                "sample",
            )
            .filter(parent__is_ghfdb=True)
        )

    def to_dataframe(self, fieldnames=(), verbose=False, index=None, coerce_float=False, datetime_index=False):
        return super().to_dataframe(fieldnames, verbose, index, coerce_float, datetime_index)


# # Find the file
# file_path = finders.find("ghfdb/IHFC_2024_GHFDB.xlsx")

# GHFDB_2024 = pd.read_excel(file_path)

# print(GHFDB_2024.head())
