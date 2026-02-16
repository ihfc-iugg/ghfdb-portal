"""
Heat Flow Quality Assessment Module

This file implements the quality assessment scheme for heat flow measurements
as described in Fuchs et al. (2023) following the decision tree structure:

START: Heat Flow Quality Assessment
│
├─ **STEP 1: Determine Measurement Type**
│  ├─ Probe Sensing (Marine/Shallow) → Go to PROBE PATH
│  └─ Borehole/Mine → Go to BOREHOLE PATH
│
├─ **PROBE PATH**
│  ├─ **1A: Calculate U-Score (Uncertainty)**
│  ├─ **1B: Calculate M-Score (Methodological)**
│  └─ **1C: Evaluate P-Flags (Perturbations)**
│
├─ **BOREHOLE PATH**
│  ├─ **2A: Calculate U-Score** (Same as probe)
│  ├─ **2B: Calculate M-Score (Methodological)**
│  └─ **2C: Evaluate P-Flags** (Same as probe)
│
├─ **STEP 2: Combine Scores**
│  └─ Child Level Quality = U-Score + M-Score + P-Flags
│
└─ **STEP 3: Parent Level Quality**
   ├─ Single child → Inherit child quality
   ├─ Multiple children (all used) → Worst quality among all
   └─ Multiple children (some used) → Worst quality among relevant children only

Reference: https://www.sciencedirect.com/science/article/pii/S0040195123002743
"""

import logging

from django.db import models
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


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


def calculate_U_score(heat_flow):
    """
    Calculate the U-score for a heat flow measurement based on its uncertainty.

    Args:
        heat_flow: HeatFlow model instance

    Returns:
        UScoreOptions: U1 (Excellent) to U4 (Poor) or Ux (Unknown)

    COV-based classification:
    - U1: Excellent (COV < 5%)
    - U2: Good (COV 5-15%)
    - U3: Acceptable (COV 15-25%)
    - U4: Poor (COV > 25%)
    - Ux: Not determined / missing data
    """
    # Check if we have both value and uncertainty
    if not heat_flow.value or not heat_flow.uncertainty:
        return UScoreOptions.Ux

    try:
        # Calculate coefficient of variation as percentage
        cov_percent = (heat_flow.uncertainty / abs(heat_flow.value)) * 100

        if cov_percent < 5:
            return UScoreOptions.U1
        elif cov_percent < 15:
            return UScoreOptions.U2
        elif cov_percent < 25:
            return UScoreOptions.U3
        else:
            return UScoreOptions.U4

    except (ZeroDivisionError, TypeError):
        logger.warning(f"Could not calculate U-score for HeatFlow {heat_flow.pk}")
        return UScoreOptions.Ux


class ProbeQualityCalculator:
    """Calculate quality scores for probe-sensing measurements."""

    def __init__(self, heat_flow):
        self.heat_flow = heat_flow

    def calculate_M_score(self):
        """Calculate M-score for probe measurements."""
        t_score = self.calculate_T_score()
        tc_score = self.calculate_TC_score()

        # Final M-score is product of T and TC scores
        final_score = t_score * tc_score

        # Convert to categorical M-score
        if final_score > 0.75:
            return MScoreOptions.M1
        elif final_score > 0.5:
            return MScoreOptions.M2
        elif final_score > 0.25:
            return MScoreOptions.M3
        else:
            return MScoreOptions.M4

    def calculate_T_score(self):
        """Calculate temperature gradient score for probe measurements."""
        score = 1.0

        # Add individual penalties/bonuses
        score += self._penetration_penalty()
        score += self._temperature_points_penalty()
        score += self._water_depth_penalty()
        score += self._probe_tilt_penalty()

        # Ensure score stays within bounds
        return max(0.2, min(1.2, score))

    def calculate_TC_score(self):
        """Calculate thermal conductivity score for probe measurements."""
        if not self.heat_flow.thermal_conductivity:
            return 0.2  # Minimum score if no TC data

        score = 1.0
        tc = self.heat_flow.thermal_conductivity

        # Add individual penalties/bonuses
        score += self._tc_location_penalty(tc)
        score += self._tc_source_penalty(tc)
        score += self._tc_number_penalty(tc)
        score += self._tc_pt_conditions_penalty(tc)

        # Ensure score stays within bounds
        return max(0.2, min(1.2, score))

    def _penetration_penalty(self):
        """Penetration depth penalty/bonus."""
        penetration = self.heat_flow.probe_penetration
        if not penetration:
            return -0.2  # Unspecified

        if penetration > 10:
            return 0.1
        elif penetration > 3:
            return 0.0
        elif penetration > 1:
            return -0.1
        else:
            return -0.2

    def _temperature_points_penalty(self):
        """Temperature points penalty/bonus."""
        if not self.heat_flow.thermal_gradient:
            return -0.2

        number = self.heat_flow.thermal_gradient.number
        if not number:
            return -0.2

        if number > 5:
            return 0.1
        elif number >= 3:
            return 0.0
        elif number >= 1:
            return -0.1
        else:
            return -0.2

    def _water_depth_penalty(self):
        """Water depth penalty (for marine measurements)."""
        # Get water depth from site elevation (negative for below sea level)
        site = self.heat_flow.parent.sample if self.heat_flow.parent else None
        if not site or not hasattr(site, "location") or not site.location:
            return -0.2

        # Check if corrected for bottom water temperature
        corrected_for_bwt = (
            hasattr(self.heat_flow, "corr_SUR_flag")
            and self.heat_flow.corr_SUR_flag
            and hasattr(self.heat_flow.corr_SUR_flag, "id")
            and self.heat_flow.corr_SUR_flag.id == "present_corrected"
        )

        try:
            water_depth = -site.location.y if hasattr(site.location, "y") else None

            if water_depth is None and not corrected_for_bwt:
                return -0.2
            elif (water_depth and water_depth > 2500) or corrected_for_bwt:
                return 0.0
            elif water_depth and water_depth >= 1500:
                return -0.1
            else:
                return -0.2
        except (AttributeError, TypeError):
            return -0.2

    def _probe_tilt_penalty(self):
        """Probe tilt penalty."""
        tilt = self.heat_flow.probe_tilt

        # Check if tilt corrected
        corrected = (
            hasattr(self.heat_flow, "corr_T_flag")
            and self.heat_flow.corr_T_flag.exists()
            and any("tilt" in str(flag).lower() for flag in self.heat_flow.corr_T_flag.all())
        )

        if tilt is None and not corrected:
            return -0.2

        if (tilt and tilt <= 10) or corrected:
            return 0.0
        elif tilt and tilt < 30:
            return -0.1
        else:
            return -0.2

    def _tc_location_penalty(self, tc):
        """Thermal conductivity location penalty."""
        if not tc.location.exists():
            return -0.2

        location_ids = list(tc.location.values_list("id", flat=True))
        if "actual" in location_ids or "in_situ" in location_ids:
            return 0.0
        elif "other" in location_ids or "nearby" in location_ids:
            return -0.1
        else:  # literature or unknown
            return -0.2

    def _tc_source_penalty(self, tc):
        """Thermal conductivity source penalty."""
        if not tc.source.exists():
            return -0.2

        source_ids = list(tc.source.values_list("id", flat=True))
        if "in_situ_probe" in source_ids:
            return 0.1
        elif "core" in source_ids:
            return -0.1
        else:  # literature or other
            return -0.2

    def _tc_number_penalty(self, tc):
        """Thermal conductivity number of measurements penalty."""
        if not tc.number:
            return -0.1

        if tc.number > 10:
            return 0.1
        elif tc.number >= 3:
            return 0.0
        else:
            return -0.1

    def _tc_pt_conditions_penalty(self, tc):
        """Thermal conductivity pressure-temperature conditions penalty."""
        if not tc.pT_conditions.exists():
            return -0.2

        pt_ids = list(tc.pT_conditions.values_list("id", flat=True))
        if "in_situ" in pt_ids:
            return 0.1
        elif "ambient" in pt_ids:
            return -0.1
        else:
            return -0.2


class BoreholeQualityCalculator:
    """Calculate quality scores for borehole/mine measurements."""

    def __init__(self, heat_flow):
        self.heat_flow = heat_flow

    def calculate_M_score(self):
        """Calculate M-score for borehole measurements."""
        t_score = self.calculate_T_score()
        tc_score = self.calculate_TC_score()

        # Final M-score is product of T and TC scores
        final_score = t_score * tc_score

        # Convert to categorical M-score
        if final_score > 0.75:
            return MScoreOptions.M1
        elif final_score > 0.5:
            return MScoreOptions.M2
        elif final_score > 0.25:
            return MScoreOptions.M3
        else:
            return MScoreOptions.M4

    def calculate_T_score(self):
        """Calculate temperature gradient score for borehole measurements."""
        if not self.heat_flow.thermal_gradient:
            return 0.4  # Minimum for borehole

        tg = self.heat_flow.thermal_gradient
        score = 1.0

        # Determine measurement type and correction status
        score += self._temperature_method_penalty(tg)

        return max(0.4, min(1.1, score))

    def calculate_TC_score(self):
        """Calculate thermal conductivity score for borehole measurements."""
        if not self.heat_flow.thermal_conductivity:
            return 0.1  # Minimum score

        tc = self.heat_flow.thermal_conductivity
        score = 1.0

        # Check if interval depth is reported
        if not self._has_interval_depth():
            return 0.1  # Stop here with minimum score

        score += self._tc_location_penalty_borehole(tc)
        score += self._tc_source_penalty_borehole(tc)
        score += self._tc_number_penalty_borehole(tc)
        score += self._tc_saturation_pt_penalty(tc)

        return max(0.1, min(1.2, score))

    def _has_interval_depth(self):
        """Check if interval depth is reported."""
        # This should check if the heat flow has associated depth intervals
        # For now, assume it's reported if thermal_conductivity exists
        return bool(self.heat_flow.thermal_conductivity)

    def _temperature_method_penalty(self, tg):
        """Temperature measurement method penalty."""
        # This is simplified - in reality would check method_top and method_bottom
        # and determine if continuous log, multiple points, or single point

        # Check if corrected/equilibrium vs perturbed
        is_corrected = tg.is_corrected() if hasattr(tg, "is_corrected") else False

        # Estimate measurement type from number of points
        number = tg.number or 1

        if number > 10:  # Continuous log
            return -0.1
        elif number > 3:  # Multiple points
            return -0.1 if is_corrected else -0.5
        else:  # Single point
            return -0.3 if is_corrected else -0.6

    def _tc_location_penalty_borehole(self, tc):
        """Thermal conductivity location penalty for borehole."""
        if not tc.location.exists():
            return -0.1

        location_ids = list(tc.location.values_list("id", flat=True))
        if "actual" in location_ids:
            return 0.0
        elif "nearby" in location_ids or "other" in location_ids:
            return -0.1
        else:  # literature
            return -0.2

    def _tc_source_penalty_borehole(self, tc):
        """Thermal conductivity source penalty for borehole."""
        if not tc.source.exists():
            return -0.2

        source_ids = list(tc.source.values_list("id", flat=True))
        if "in_situ" in source_ids or "core_log" in source_ids:
            return 0.1
        elif "core" in source_ids:
            return 0.0
        else:  # literature
            return -0.2

    def _tc_number_penalty_borehole(self, tc):
        """Thermal conductivity number penalty for borehole."""
        if not tc.number or tc.number <= 15:
            return -0.1
        else:
            return 0.0

    def _tc_saturation_pt_penalty(self, tc):
        """Thermal conductivity saturation and p-T conditions penalty."""
        # This is complex - simplified implementation
        if not tc.saturation.exists() or not tc.pT_conditions.exists():
            return -0.2

        saturation_ids = list(tc.saturation.values_list("id", flat=True))
        pt_ids = list(tc.pT_conditions.values_list("id", flat=True))

        is_saturated = "saturated" in saturation_ids
        is_in_situ = "in_situ" in pt_ids

        if is_saturated and is_in_situ:
            return 0.0
        elif is_saturated or is_in_situ:
            return -0.1
        else:
            return -0.2


def calculate_perturbation_flags(heat_flow):
    """
    Calculate perturbation flags (p-flags) for a heat flow measurement.

    Returns:
        str: 7-character string representing perturbation effects

    Flag meanings:
    - Uppercase: Present and corrected
    - Lowercase: Present but not corrected
    - X: Present but insignificant
    - x: Not present/not recognized
    - -: Insufficient information
    """
    flags = []

    # Define the seven perturbation effects
    corrections = [
        ("S", heat_flow.corr_S_flag),  # Sedimentation
        ("E", heat_flow.corr_E_flag),  # Erosion
        ("T", heat_flow.corr_TOPO_flag),  # Topography
        ("P", heat_flow.corr_PAL_flag),  # Paleoclimate
        ("V", heat_flow.corr_SUR_flag),  # Surface/bottom water variations
        ("C", heat_flow.corr_CONV_flag),  # Convection
        ("R", heat_flow.corr_HR_flag),  # Heat refraction
    ]

    for letter, flag in corrections:
        if not flag or not hasattr(flag, "id"):
            flags.append("-")  # Insufficient information
        elif flag.id == "present_corrected":
            flags.append(letter.upper())
        elif flag.id == "present_uncorrected":
            flags.append(letter.lower())
        elif flag.id == "present_insignificant":
            flags.append("X")
        elif flag.id == "not_present":
            flags.append("x")
        else:
            flags.append("-")  # Default for unknown states

    return "".join(flags)


def calculate_heat_flow_quality(heat_flow):
    """
    Calculate complete quality assessment for a heat flow measurement.

    Args:
        heat_flow: HeatFlow model instance

    Returns:
        dict: Quality assessment with U-score, M-score, and P-flags
    """
    # Step 1: Calculate U-score
    u_score = calculate_U_score(heat_flow)

    # Step 2: Calculate M-score based on measurement type
    if heat_flow.is_probe:
        calculator = ProbeQualityCalculator(heat_flow)
        m_score = calculator.calculate_M_score()
    else:
        calculator = BoreholeQualityCalculator(heat_flow)
        m_score = calculator.calculate_M_score()

    # Step 3: Calculate P-flags
    p_flags = calculate_perturbation_flags(heat_flow)

    return {
        "u_score": u_score,
        "m_score": m_score,
        "p_flags": p_flags,
        "quality_string": f"{u_score}{m_score}{p_flags}",
    }


def calculate_parent_quality(parent_heat_flow):
    """
    Calculate quality for parent level (ParentHeatFlow) based on children.

    Args:
        parent_heat_flow: ParentHeatFlow model instance (from ghfdb app)

    Returns:
        dict: Parent level quality assessment
    """
    children = parent_heat_flow.children.all()

    if not children.exists():
        return {
            "u_score": UScoreOptions.Ux,
            "m_score": MScoreOptions.Mx,
            "p_flags": "-------",
            "quality_string": f"{UScoreOptions.Ux}{MScoreOptions.Mx}-------",
        }

    if children.count() == 1:
        # Single child: inherit its quality
        child = children.first()
        return calculate_heat_flow_quality(child)

    # Multiple children: use relevant ones or all if none marked as relevant
    relevant_children = children.filter(relevant_child=True)
    if not relevant_children.exists():
        relevant_children = children

    # Get quality for all relevant children
    child_qualities = [calculate_heat_flow_quality(child) for child in relevant_children]

    # Inherit the worst quality (highest number/letter)
    worst_u = max((q["u_score"] for q in child_qualities), key=lambda x: ["U1", "U2", "U3", "U4", "Ux"].index(x))
    worst_m = max((q["m_score"] for q in child_qualities), key=lambda x: ["M1", "M2", "M3", "M4", "Mx"].index(x))

    # For P-flags, combine all flags (show worst case for each position)
    combined_flags = list("-------")
    for quality in child_qualities:
        for i, flag in enumerate(quality["p_flags"]):
            if flag.isupper():  # Corrected
                if combined_flags[i] in ["-", "x", "X"]:
                    combined_flags[i] = flag
            elif flag.islower() or (flag == "X" and combined_flags[i] in ["-", "x"]):
                # Uncorrected (worst case) or insignificant but better than nothing
                combined_flags[i] = flag

    p_flags = "".join(combined_flags)

    return {
        "u_score": worst_u,
        "m_score": worst_m,
        "p_flags": p_flags,
        "quality_string": f"{worst_u}{worst_m}{p_flags}",
    }
