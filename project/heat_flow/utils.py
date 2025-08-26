# import pandas as pd
# from django.contrib.staticfiles import finders
from django.db import models
from django.utils.translation import gettext as _
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


class UScoreOptions(models.TextChoices):
    U1 = "U1", _("Excellent")
    U2 = "U2", _("Good")
    U3 = "U3", _("Acceptable")
    U4 = "U4", _("Poor")
    Ux = "Ux", _("Not determined / missing data")


class MScoreOptions(models.TextChoices):
    M1 = "M1", _("Excellent")
    M2 = "M2", _("Good")
    M3 = "M3", _("Acceptable")
    M4 = "M4", _("Poor")
    Mx = "Mx", _("Not determined / missing data")


def calculate_U_score(hf):
    """
    Calculate the U-score for a heat flow measurement based on its uncertainty.
    The U-score is defined as follows:
    - U1: Excellent (uncertainty < 5%)
    - U2: Good (5% <= uncertainty 5-15%)
    - U3: Ok (10% <= uncertainty 15-25%)
    - U4: Poor (uncertainty >= 25%)
    - Ux: Not determined / missing data
    """

    # We need both a heat flow value and uncertainty to calculate a U-score.
    if not hf.value or not hf.uncertainty:
        return UScoreOptions.Ux

    COV_perc = hf.uncertainty / hf.value * 100  # Convert uncertainty to percentage
    if COV_perc < 5:
        return UScoreOptions.U1
    elif COV_perc < 15:
        return UScoreOptions.U2
    elif COV_perc < 25:
        return UScoreOptions.U3
    else:
        return UScoreOptions.U4


def calculate_M_score_probe(hf):
    """
    Calculate the M-score for a heat flow measurement based on the probe type.
    The M-score is defined as follows:
    - M1: Excellent (probe type = "Thermal Needle Probe")
    - M2: Good (probe type = "Thermal Wire Probe")
    - M3: Ok (probe type = "Thermal Conductivity Probe")
    - M4: Poor (probe type = "Other")
    - Mx: Not determined / missing data
    """

    if not hf.probe_type:
        return "Mx"

    probe_type = hf.probe_type.lower()
    if "needle" in probe_type:
        return "M1"
    elif "wire" in probe_type:
        return "M2"
    elif "conductivity" in probe_type:
        return "M3"
    else:
        return "M4"


def calculate_M_score_borehole(hf):
    """
    Calculate the M-score for a heat flow measurement based on the borehole type.
    The M-score is defined as follows:
    - M1: Excellent (borehole type = "Deep Borehole")
    - M2: Good (borehole type = "Shallow Borehole")
    - M3: Ok (borehole type = "Exploratory Borehole")
    - M4: Poor (borehole type = "Other")
    - Mx: Not determined / missing data
    """

    if not hf.borehole_type:
        return "Mx"

    borehole_type = hf.borehole_type.lower()
    if "deep" in borehole_type:
        return "M1"
    elif "shallow" in borehole_type:
        return "M2"
    elif "exploratory" in borehole_type:
        return "M3"
    else:
        return "M4"


def calculate_M_score(hf):
    if hf.is_probe_measurement:
        quality_score = calculate_M_score_probe(hf)
    elif hf.is_borehole_measurement:
        quality_score = calculate_M_score_borehole(hf)
    else:
        return MScoreOptions.Mx

    if quality_score > 0.75:
        return MScoreOptions.M1
    elif quality_score > 0.5:
        return MScoreOptions.M2
    elif quality_score > 0.25:
        return MScoreOptions.M3
    elif quality_score > 0:
        return MScoreOptions.M4
    else:
        return MScoreOptions.Mx


def calc_T_score_borehole(TG):
    pass


def calc_T_score_probe(TG):
    score = 1.0
    hf = TG.heat_flow_child
    if hf.probe_penetration:
        score += 0.1
    pass


def calculate_T_score(TG):
    if TG.heat_flow_child.is_probe:
        return calc_T_score_probe(TG)
    else:
        return calc_T_score_borehole(TG)


class ProbeMScoreCalculator:
    """Responsible for calculating the M-score for a probe measurement.

    Issues:

    - `water_depth_penalty` depends on a non-existent field `corr_BWT_flag` in the heat_flow model (the hfqa_tool refers to
    `corr_SUR_flag` so we use that as well)
    - `tilt_correction` specifies to check the "corr_IS_flag" for "Tilt Corrected", but "corr_IS_flag" does not
    allow such a value.
    """

    def __init__(self, heat_flow):
        self.heat_flow = heat_flow

    def calc_M_score(self):
        """
        Calculate the T-score for a probe measurement.
        """
        T_score = self.calc_T_score()
        TC_score = self.calc_TC_score()
        return T_score * TC_score

    def calc_TC_score(self):
        """
        Calculate the thermal conductivity score for a probe measurement.
        """
        score = 1.0
        score += self.localization_penalty()
        score += self.source_and_saturation_penalty()
        score += self.TC_number_penalty()
        score += self.pT_conditions_penalty()
        return score

    def localization_penalty(self):
        """
        Calculate the penalty for the localization of the thermal conductivity measurement.
        """
        TC = self.heat_flow.thermal_conductivity
        if TC.location == "actual":
            return 0
        elif TC.location == "other":
            return -0.1
        else:
            # location == "literature" or value is None
            return -0.2

    def source_and_saturation_penalty(self):
        """
        Calculate the penalty for the source and saturation of the thermal conductivity measurement.
        """
        TC = self.heat_flow.thermal_conductivity
        if TC.source == "lab" and TC.saturation == "unsaturated":
            return 0
        elif TC.source == "field" and TC.saturation == "saturated":
            return -0.1
        elif TC.source == "literature" or TC.saturation is None:
            return -0.2
        else:
            return -0.1

    def calc_T_score(self):
        """Calculate the T-score for a borehole measurement."""
        score = 1.0
        score += self.penetration_penalty()
        score += self.T_number_penalty()
        score += self.water_depth_penalty()
        score += self.probe_tilt_penalty()
        return score

    def T_number_penalty(self):
        """
        Calculate the penalty for the number of temperature measurements.
        """
        gradient = self.heat_flow.temperature_gradient
        if gradient.number > 5:
            return 0.1
        elif gradient.number > 3:
            return 0
        elif gradient.number > 1:
            return -0.1
        else:
            return -0.2

    def water_depth_penalty(self):
        water_depth = -self.heat_flow.parent.sample.elevation
        corrected_for_BWT = self.heat_flow.corr_SUR_flag == "present_corrected"
        if water_depth is None and not corrected_for_BWT:
            return -0.2

        elif water_depth > 2500 or corrected_for_BWT:
            return 0
        elif water_depth >= 1500:
            return -0.1
        # elif water_depth < 1500:
        #     return -0.2
        return -0.2

    def probe_tilt_penalty(self):
        """
        Calculate the penalty for the probe tilt.
        """
        corrected = self.heat_flow.corr_T_flag == "tiltCorrected"
        tilt = self.heat_flow.probe_tilt

        # If no tilt is provided, and it has not been specified as corrected, it gets the largest penalty.
        if tilt is None and not corrected:
            return -0.2

        if tilt <= 10 or corrected:
            return 0
        elif tilt < 30:
            return -0.1
        else:
            return -0.2

    def penetration_penalty(self):
        """
        Calculate the penalty for the probe penetration depth.
        """
        penetration = self.heat_flow.probe_penetration
        if penetration > 10:
            return 0.1
        elif penetration > 3:
            return 0
        elif penetration > 1:
            return -0.1
        else:
            return -0.2


# # Find the file
# file_path = finders.find("ghfdb/IHFC_2024_GHFDB.xlsx")

# GHFDB_2024 = pd.read_excel(file_path)

# print(GHFDB_2024.head())
