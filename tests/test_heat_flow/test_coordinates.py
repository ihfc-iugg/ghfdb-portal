"""
Unit tests for coordinate normalization and validation.

This module demonstrates parametrized testing patterns:
- Multiple test cases with clear IDs
- Edge case coverage
- Error condition testing
- Decimal precision handling
"""

import pytest
from decimal import Decimal


class TestLatitudeNormalization:
    """Unit tests for latitude normalization from string format to decimal degrees."""

    @pytest.mark.parametrize(
        "lat_str,expected",
        [
            ("45.5N", 45.5),
            ("12.3S", -12.3),
            ("0.0N", 0.0),
            ("0.0S", 0.0),
            ("90.0N", 90.0),
            ("90.0S", -90.0),
            ("43.63333N", 43.63333),
            ("25.123456S", -25.123456),
        ],
        ids=[
            "northern_hemisphere_mid_latitude",
            "southern_hemisphere_low_latitude",
            "equator_north_notation",
            "equator_south_notation",
            "north_pole",
            "south_pole",
            "decimal_precision_north",
            "high_precision_south",
        ],
    )
    def test_normalize_latitude_valid_hemisphere_suffixes(self, lat_str, expected):
        """Latitude normalization converts N/S suffixes to positive/negative values."""
        from heat_flow.utils import normalize_latitude

        result = normalize_latitude(lat_str)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_lat",
        [
            "95.0N",  # > 90
            "100.0S",  # > 90 (absolute)
            "-90.5N",  # Negative with N suffix
            "45.5",  # Missing hemisphere
            "45.5E",  # Wrong hemisphere (E is for longitude)
            "ABC",  # Non-numeric
            "",  # Empty string
            "N45.5",  # Reversed format
        ],
        ids=[
            "exceeds_north_pole",
            "exceeds_south_pole_absolute",
            "negative_with_north",
            "missing_hemisphere",
            "wrong_hemisphere_indicator",
            "non_numeric",
            "empty_string",
            "reversed_format",
        ],
    )
    def test_normalize_latitude_rejects_invalid_formats(self, invalid_lat):
        """Latitude normalization raises ValueError for invalid inputs."""
        from heat_flow.utils import normalize_latitude

        with pytest.raises(ValueError):
            normalize_latitude(invalid_lat)

    def test_normalize_latitude_returns_float_type(self):
        """Latitude normalization should return float, not Decimal or string."""
        from heat_flow.utils import normalize_latitude

        result = normalize_latitude("45.5N")
        assert isinstance(result, float)

    def test_normalize_latitude_handles_lowercase_suffixes(self):
        """Latitude normalization should accept lowercase n/s suffixes."""
        from heat_flow.utils import normalize_latitude

        assert normalize_latitude("45.5n") == 45.5
        assert normalize_latitude("12.3s") == -12.3


class TestLongitudeNormalization:
    """Unit tests for longitude normalization from string format to decimal degrees."""

    @pytest.mark.parametrize(
        "lon_str,expected",
        [
            ("120.5E", 120.5),
            ("75.3W", -75.3),
            ("0.0E", 0.0),
            ("0.0W", 0.0),
            ("180.0E", 180.0),
            ("180.0W", -180.0),
            ("5.61667W", -5.61667),
            ("110.25E", 110.25),
        ],
        ids=[
            "eastern_hemisphere",
            "western_hemisphere",
            "prime_meridian_east",
            "prime_meridian_west",
            "dateline_east",
            "dateline_west",
            "decimal_precision_west",
            "decimal_precision_east",
        ],
    )
    def test_normalize_longitude_valid_hemisphere_suffixes(self, lon_str, expected):
        """Longitude normalization converts E/W suffixes to positive/negative values."""
        from heat_flow.utils import normalize_longitude

        result = normalize_longitude(lon_str)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_lon",
        [
            "185.0E",  # > 180
            "200.0W",  # > 180 (absolute)
            "-120.5E",  # Negative with E suffix
            "120.5",  # Missing hemisphere
            "120.5N",  # Wrong hemisphere (N is for latitude)
            "XYZ",  # Non-numeric
            "",  # Empty string
            "E120.5",  # Reversed format
        ],
        ids=[
            "exceeds_180_east",
            "exceeds_180_west_absolute",
            "negative_with_east",
            "missing_hemisphere",
            "wrong_hemisphere_indicator",
            "non_numeric",
            "empty_string",
            "reversed_format",
        ],
    )
    def test_normalize_longitude_rejects_invalid_formats(self, invalid_lon):
        """Longitude normalization raises ValueError for invalid inputs."""
        from heat_flow.utils import normalize_longitude

        with pytest.raises(ValueError):
            normalize_longitude(invalid_lon)

    def test_normalize_longitude_handles_lowercase_suffixes(self):
        """Longitude normalization should accept lowercase e/w suffixes."""
        from heat_flow.utils import normalize_longitude

        assert normalize_longitude("120.5e") == 120.5
        assert normalize_longitude("75.3w") == -75.3


class TestCoordinatePairValidation:
    """Unit tests for validating coordinate pairs (lat, lon) together."""

    @pytest.mark.parametrize(
        "lat,lon",
        [
            (45.0, -120.0),  # Valid mid-latitude
            (0.0, 0.0),  # Null Island
            (90.0, 180.0),  # Max valid coordinates
            (-90.0, -180.0),  # Min valid coordinates
            (43.63333, -5.61667),  # High precision (Bay of Biscay)
            (-12.45, -110.25),  # Pacific Ocean
        ],
        ids=[
            "mid_latitude_western_hemisphere",
            "null_island",
            "maximum_valid_coordinates",
            "minimum_valid_coordinates",
            "high_precision_atlantic",
            "high_precision_pacific",
        ],
    )
    def test_validate_coordinate_pair_accepts_valid_coordinates(self, lat, lon):
        """Coordinate pair validation accepts all valid lat/lon combinations."""
        from heat_flow.utils import validate_coordinate_pair

        result = validate_coordinate_pair(lat, lon)
        assert result is True

    @pytest.mark.parametrize(
        "lat,lon,error_pattern",
        [
            (95.0, 0.0, "Latitude.*out of range"),
            (-95.0, 0.0, "Latitude.*out of range"),
            (0.0, 185.0, "Longitude.*out of range"),
            (0.0, -185.0, "Longitude.*out of range"),
            (None, 120.0, "Latitude.*required"),
            (45.0, None, "Longitude.*required"),
        ],
        ids=[
            "latitude_too_high",
            "latitude_too_low",
            "longitude_too_high",
            "longitude_too_low",
            "missing_latitude",
            "missing_longitude",
        ],
    )
    def test_validate_coordinate_pair_rejects_invalid_coordinates(
        self, lat, lon, error_pattern
    ):
        """Coordinate pair validation rejects out-of-range or missing values."""
        from heat_flow.utils import validate_coordinate_pair

        with pytest.raises(ValueError, match=error_pattern):
            validate_coordinate_pair(lat, lon)


class TestCoordinateConversionToDecimal:
    """Unit tests for converting degrees/minutes/seconds to decimal degrees."""

    @pytest.mark.parametrize(
        "degrees,minutes,seconds,expected",
        [
            (45, 30, 0, 45.5),  # 45°30'00" = 45.5°
            (12, 18, 0, 12.3),  # 12°18'00" = 12.3°
            (43, 38, 0, 43.633333),  # 43°38'00" ≈ 43.633333°
            (0, 0, 0, 0.0),  # 0°0'0" = 0.0°
            (90, 0, 0, 90.0),  # 90°0'0" = 90.0°
            (1, 30, 30, 1.508333),  # 1°30'30" ≈ 1.508333°
        ],
        ids=[
            "simple_half_degree",
            "decimal_conversion",
            "bay_of_biscay_latitude",
            "zero_degrees",
            "north_pole",
            "with_seconds",
        ],
    )
    def test_convert_dms_to_decimal_valid_values(
        self, degrees, minutes, seconds, expected
    ):
        """DMS to decimal conversion handles various coordinate formats."""
        from heat_flow.utils import convert_dms_to_decimal

        result = convert_dms_to_decimal(degrees, minutes, seconds)
        assert abs(result - expected) < 0.000001  # 6 decimal places precision

    @pytest.mark.parametrize(
        "degrees,minutes,seconds",
        [
            (45, 60, 0),  # Minutes >= 60
            (45, 30, 60),  # Seconds >= 60
            (45, -5, 0),  # Negative minutes
            (45, 30, -10),  # Negative seconds
        ],
        ids=[
            "minutes_out_of_range",
            "seconds_out_of_range",
            "negative_minutes",
            "negative_seconds",
        ],
    )
    def test_convert_dms_to_decimal_rejects_invalid_components(
        self, degrees, minutes, seconds
    ):
        """DMS conversion rejects invalid minute/second values."""
        from heat_flow.utils import convert_dms_to_decimal

        with pytest.raises(ValueError):
            convert_dms_to_decimal(degrees, minutes, seconds)

    def test_convert_dms_to_decimal_preserves_sign_in_degrees(self):
        """DMS conversion should preserve negative degrees for southern/western hemispheres."""
        from heat_flow.utils import convert_dms_to_decimal

        # -12°18'00" should be -12.3°
        result = convert_dms_to_decimal(-12, 18, 0)
        assert result == -12.3
