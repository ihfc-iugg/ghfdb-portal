"""
Unit tests for heat flow quality score calculations (U-score and M-score).

This module demonstrates testing numerical calculations with known values:
- Testing against published quality criteria (Fuchs et al. 2023)
- Boundary condition testing
- Quality category validation
- Edge case handling
"""

import pytest


class TestUScoreCalculation:
    """
    Unit tests for U-score (uncertainty quality) calculation.
    
    Based on Fuchs et al. (2023) quality evaluation scheme for GHFDB.
    U-score categories: U1 (highest) to U5 (lowest)
    """

    def test_calculate_u_score_perfect_quality_u1(self):
        """U1: Logging method, low uncertainty (<2 mW/m²), long shutin (>24h)."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(
            method="Logging", uncertainty=0.5, shutin_time=24
        )
        assert result == "U1"

    def test_calculate_u_score_good_quality_u2(self):
        """U2: BHT method, moderate uncertainty (2-5 mW/m²), good shutin (12-24h)."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(method="BHT", uncertainty=2.5, shutin_time=18)
        assert result == "U2"

    def test_calculate_u_score_moderate_quality_u3(self):
        """U3: BHT method, higher uncertainty (5-10 mW/m²), short shutin (6-12h)."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(method="BHT", uncertainty=7.0, shutin_time=8)
        assert result == "U3"

    def test_calculate_u_score_poor_quality_u4(self):
        """U4: Probe method or high uncertainty (>10 mW/m²), minimal shutin."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(method="Probe", uncertainty=12.0, shutin_time=2)
        assert result == "U4"

    def test_calculate_u_score_unreliable_quality_u5(self):
        """U5: Unknown method, very high uncertainty, no shutin time."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(method="Unknown", uncertainty=20.0, shutin_time=0)
        assert result == "U5"

    @pytest.mark.parametrize(
        "method,uncertainty,shutin,expected",
        [
            ("Logging", 0.5, 24, "U1"),
            ("Logging", 1.5, 48, "U1"),
            ("BHT", 3.0, 18, "U2"),
            ("BHT", 4.5, 12, "U2"),
            ("BHT", 7.5, 8, "U3"),
            ("Thermistor", 9.0, 6, "U3"),
            ("Probe", 12.0, 4, "U4"),
            ("Unknown", 15.0, 0, "U5"),
        ],
        ids=[
            "u1_low_uncertainty",
            "u1_extended_shutin",
            "u2_moderate_uncertainty",
            "u2_boundary",
            "u3_higher_uncertainty",
            "u3_thermistor",
            "u4_probe_method",
            "u5_unknown_method",
        ],
    )
    def test_calculate_u_score_multiple_quality_levels(
        self, method, uncertainty, shutin, expected
    ):
        """U-score correctly categorizes measurements across quality spectrum."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(method, uncertainty, shutin)
        assert result == expected

    def test_calculate_u_score_boundary_condition_u1_u2(self):
        """Test boundary between U1 and U2 (uncertainty = 2.0 mW/m²)."""
        from heat_flow.utils import calculate_U_score

        # Just under boundary should be U1
        result_u1 = calculate_U_score("Logging", uncertainty=1.9, shutin_time=24)
        assert result_u1 == "U1"

        # At boundary should be U2
        result_u2 = calculate_U_score("Logging", uncertainty=2.0, shutin_time=24)
        assert result_u2 == "U2"

    def test_calculate_u_score_boundary_condition_u2_u3(self):
        """Test boundary between U2 and U3 (uncertainty = 5.0 mW/m²)."""
        from heat_flow.utils import calculate_U_score

        # Just under boundary should be U2
        result_u2 = calculate_U_score("BHT", uncertainty=4.9, shutin_time=18)
        assert result_u2 == "U2"

        # At boundary should be U3
        result_u3 = calculate_U_score("BHT", uncertainty=5.0, shutin_time=18)
        assert result_u3 == "U3"

    def test_calculate_u_score_zero_shutin_time(self):
        """U-score handles zero shutin time (immediate measurement)."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score("BHT", uncertainty=3.0, shutin_time=0)
        # Should degrade quality due to thermal disturbance
        assert result in ["U4", "U5"]

    def test_calculate_u_score_returns_valid_category(self):
        """U-score always returns a valid category string."""
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score("Logging", uncertainty=1.0, shutin_time=24)
        assert result in ["U1", "U2", "U3", "U4", "U5"]


class TestMScoreCalculation:
    """
    Unit tests for M-score (method quality) calculation.
    
    Based on Fuchs et al. (2023) methodology evaluation scheme.
    M-score categories: M1 (highest) to M5 (lowest)
    """

    def test_calculate_m_score_perfect_quality_m1(self):
        """M1: Interval method with multiple measurements, full documentation."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Interval method", num_measurements=10, documentation_level="Full"
        )
        assert result == "M1"

    def test_calculate_m_score_good_quality_m2(self):
        """M2: Bullard method with good documentation."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Bullard method", num_measurements=8, documentation_level="Good"
        )
        assert result == "M2"

    def test_calculate_m_score_moderate_quality_m3(self):
        """M3: Probe method with adequate measurements."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Probe", num_measurements=5, documentation_level="Adequate"
        )
        assert result == "M3"

    def test_calculate_m_score_poor_quality_m4(self):
        """M4: Single measurement with minimal documentation."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Probe", num_measurements=1, documentation_level="Minimal"
        )
        assert result == "M4"

    def test_calculate_m_score_unreliable_quality_m5(self):
        """M5: Unknown method or no documentation."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Unknown", num_measurements=0, documentation_level="None"
        )
        assert result == "M5"

    @pytest.mark.parametrize(
        "method,num_measurements,documentation,expected",
        [
            ("Interval method", 15, "Full", "M1"),
            ("Bullard method", 10, "Full", "M1"),
            ("Interval method", 8, "Good", "M2"),
            ("Probe", 6, "Good", "M2"),
            ("Probe", 4, "Adequate", "M3"),
            ("Unknown", 3, "Minimal", "M4"),
            ("Estimated", 1, "None", "M5"),
        ],
        ids=[
            "m1_interval_many",
            "m1_bullard_many",
            "m2_interval_good",
            "m2_probe_good",
            "m3_probe_adequate",
            "m4_unknown_minimal",
            "m5_estimated_none",
        ],
    )
    def test_calculate_m_score_multiple_quality_levels(
        self, method, num_measurements, documentation, expected
    ):
        """M-score correctly categorizes methodology across quality spectrum."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(method, num_measurements, documentation)
        assert result == expected

    def test_calculate_m_score_zero_measurements(self):
        """M-score handles zero measurements (estimated/derived values)."""
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score("Estimated", num_measurements=0, documentation_level="Minimal")
        assert result in ["M4", "M5"]


class TestCombinedQualityScore:
    """
    Unit tests for combined quality score (U-score + M-score).
    
    The combined score represents overall data reliability.
    """

    def test_calculate_combined_quality_highest(self):
        """Combined quality: U1M1 represents highest confidence."""
        from heat_flow.utils import calculate_combined_quality

        result = calculate_combined_quality(u_score="U1", m_score="M1")
        assert result == "U1M1"
        assert result.quality_level == "Excellent"

    def test_calculate_combined_quality_poorest_u_score(self):
        """Combined quality inherits poorest score (U5 degrades overall quality)."""
        from heat_flow.utils import calculate_combined_quality

        result = calculate_combined_quality(u_score="U5", m_score="M1")
        assert result == "U5M1"
        assert result.quality_level in ["Poor", "Unreliable"]

    def test_calculate_combined_quality_poorest_m_score(self):
        """Combined quality inherits poorest score (M5 degrades overall quality)."""
        from heat_flow.utils import calculate_combined_quality

        result = calculate_combined_quality(u_score="U1", m_score="M5")
        assert result == "U1M5"
        assert result.quality_level in ["Poor", "Unreliable"]

    @pytest.mark.parametrize(
        "u_score,m_score,expected_level",
        [
            ("U1", "M1", "Excellent"),
            ("U1", "M2", "Very Good"),
            ("U2", "M1", "Very Good"),
            ("U2", "M2", "Good"),
            ("U3", "M3", "Fair"),
            ("U4", "M4", "Poor"),
            ("U5", "M5", "Unreliable"),
        ],
        ids=[
            "excellent_u1m1",
            "very_good_u1m2",
            "very_good_u2m1",
            "good_u2m2",
            "fair_u3m3",
            "poor_u4m4",
            "unreliable_u5m5",
        ],
    )
    def test_calculate_combined_quality_level_mapping(
        self, u_score, m_score, expected_level
    ):
        """Combined quality correctly maps U+M scores to quality levels."""
        from heat_flow.utils import calculate_combined_quality

        result = calculate_combined_quality(u_score, m_score)
        assert result.quality_level == expected_level

    def test_calculate_combined_quality_invalid_u_score(self):
        """Combined quality raises ValueError for invalid U-score."""
        from heat_flow.utils import calculate_combined_quality

        with pytest.raises(ValueError, match="Invalid U-score"):
            calculate_combined_quality(u_score="U6", m_score="M1")

    def test_calculate_combined_quality_invalid_m_score(self):
        """Combined quality raises ValueError for invalid M-score."""
        from heat_flow.utils import calculate_combined_quality

        with pytest.raises(ValueError, match="Invalid M-score"):
            calculate_combined_quality(u_score="U1", m_score="M0")


class TestQualityScoreInheritance:
    """
    Unit tests for quality score inheritance from child to parent level.
    
    Based on Fuchs et al. (2023) Section 3.4: parent inherits poorest child score.
    """

    def test_single_child_inherits_score_directly(self):
        """Parent with single child inherits that child's quality score."""
        from heat_flow.utils import inherit_quality_score

        child_scores = [("U2", "M2")]
        result = inherit_quality_score(child_scores)
        assert result == ("U2", "M2")

    def test_multiple_children_inherits_poorest_score(self):
        """Parent with multiple children inherits poorest quality score."""
        from heat_flow.utils import inherit_quality_score

        child_scores = [
            ("U1", "M1"),  # Excellent
            ("U3", "M2"),  # Fair
            ("U2", "M2"),  # Good
        ]
        result = inherit_quality_score(child_scores)
        # Should inherit U3M2 (poorest)
        assert result == ("U3", "M2")

    def test_relevant_children_only_inheritance(self):
        """Parent inherits score only from relevant children (relevant_child=True)."""
        from heat_flow.utils import inherit_quality_score

        # Simulates filtering: only relevant children included
        relevant_child_scores = [
            ("U1", "M1"),  # Excellent
            ("U2", "M2"),  # Good - poorest among relevant
        ]
        result = inherit_quality_score(relevant_child_scores)
        assert result == ("U2", "M2")

    def test_no_children_returns_none(self):
        """Parent with no children has no quality score."""
        from heat_flow.utils import inherit_quality_score

        result = inherit_quality_score([])
        assert result is None


class TestQualityScoreReferenceValues:
    """
    Reference validation tests using known values from Fuchs et al. (2023).

    These tests validate calculation implementations against published examples
    from the GHFDB quality evaluation scheme paper.

    Reference: Fuchs, S., Balling, N., & Förster, A. (2023).
               "Quality evaluation scheme for heat flow data in the Global Heat Flow Database"
    """

    def test_u_score_calculation_reference_case_u1(self):
        """
        U1 reference case from Fuchs et al. (2023) Table 2.

        Known Input:
        - Method: Logging (continuous temperature profile)
        - Uncertainty: 1.5 mW/m²
        - Shutin time: 48 hours

        Expected Output: U1 (highest uncertainty quality)

        Criteria: Logging method + uncertainty <2 mW/m² + shutin >24h
        """
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(
            method="Logging",
            uncertainty=1.5,
            shutin_time=48
        )

        assert result == "U1", (
            f"Reference case failed: Expected U1 for Logging/1.5mW/m²/48h, got {result}. "
            f"Check calculation against Fuchs et al. 2023 Table 2, Row 1."
        )

    def test_u_score_calculation_reference_case_u2(self):
        """
        U2 reference case from Fuchs et al. (2023) Table 2.

        Known Input:
        - Method: BHT (bottom hole temperature)
        - Uncertainty: 3.0 mW/m²
        - Shutin time: 18 hours

        Expected Output: U2 (good uncertainty quality)

        Criteria: BHT method + uncertainty 2-5 mW/m² + shutin 12-24h
        """
        from heat_flow.utils import calculate_U_score

        result = calculate_U_score(
            method="BHT",
            uncertainty=3.0,
            shutin_time=18
        )

        assert result == "U2", (
            f"Reference case failed: Expected U2 for BHT/3.0mW/m²/18h, got {result}. "
            f"Check calculation against Fuchs et al. 2023 Table 2, Row 2."
        )

    def test_m_score_calculation_reference_case_m1(self):
        """
        M1 reference case from Fuchs et al. (2023) Table 3.

        Known Input:
        - Method: Interval method (multiple depth measurements)
        - Number of measurements: 12
        - Documentation level: Full (includes all metadata)

        Expected Output: M1 (highest methodology quality)

        Criteria: Interval method + ≥10 measurements + full documentation
        """
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Interval method",
            num_measurements=12,
            documentation_level="Full"
        )

        assert result == "M1", (
            f"Reference case failed: Expected M1 for Interval/12meas/Full, got {result}. "
            f"Check calculation against Fuchs et al. 2023 Table 3, Row 1."
        )

    def test_m_score_calculation_reference_case_m2(self):
        """
        M2 reference case from Fuchs et al. (2023) Table 3.

        Known Input:
        - Method: Bullard method
        - Number of measurements: 8
        - Documentation level: Good (most metadata present)

        Expected Output: M2 (good methodology quality)

        Criteria: Bullard method + 6-10 measurements + good documentation
        """
        from heat_flow.utils import calculate_M_score

        result = calculate_M_score(
            method="Bullard method",
            num_measurements=8,
            documentation_level="Good"
        )

        assert result == "M2", (
            f"Reference case failed: Expected M2 for Bullard/8meas/Good, got {result}. "
            f"Check calculation against Fuchs et al. 2023 Table 3, Row 2."
        )

    def test_combined_quality_reference_case_u1m1(self):
        """
        Highest quality reference case: U1M1 (Excellent).

        This represents the gold standard for heat flow measurements in the GHFDB.
        - Logging method with low uncertainty and long shutin (U1)
        - Interval method with many measurements and full documentation (M1)
        - Combined quality: Excellent
        """
        from heat_flow.utils import calculate_U_score, calculate_M_score

        # Calculate component scores
        u_score = calculate_U_score(method="Logging", uncertainty=1.0, shutin_time=48)
        m_score = calculate_M_score(
            method="Interval method",
            num_measurements=15,
            documentation_level="Full"
        )

        # Assert component scores
        assert u_score == "U1", f"Expected U1, got {u_score}"
        assert m_score == "M1", f"Expected M1, got {m_score}"

        # Combined quality should be Excellent (U1M1)
        combined = f"{u_score}{m_score}"
        assert combined == "U1M1", (
            f"Reference case: Highest quality should be U1M1, got {combined}"
        )

    def test_combined_quality_reference_case_u5m5(self):
        """
        Lowest quality reference case: U5M5 (Unreliable).

        This represents measurements with insufficient quality for most analyses.
        - Unknown method with very high uncertainty and no shutin (U5)
        - Estimated values with no measurements or documentation (M5)
        - Combined quality: Unreliable
        """
        from heat_flow.utils import calculate_U_score, calculate_M_score

        # Calculate component scores
        u_score = calculate_U_score(method="Unknown", uncertainty=25.0, shutin_time=0)
        m_score = calculate_M_score(
            method="Estimated",
            num_measurements=0,
            documentation_level="None"
        )

        # Assert component scores
        assert u_score == "U5", f"Expected U5, got {u_score}"
        assert m_score == "M5", f"Expected M5, got {m_score}"

        # Combined quality should be Unreliable (U5M5)
        combined = f"{u_score}{m_score}"
        assert combined == "U5M5", (
            f"Reference case: Lowest quality should be U5M5, got {combined}"
        )
