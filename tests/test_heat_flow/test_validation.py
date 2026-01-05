"""
Unit tests for temperature validation functions.

This module demonstrates unit testing best practices:
- Fast, isolated tests without database or external dependencies
- Clear test names describing behavior
- Comprehensive edge case coverage
- Use of parametrization for similar test cases
"""

import pytest
from heat_flow.utils import (
    validate_temperature_range,
    normalize_temperature_value,
    convert_temperature_units,
)


class TestTemperatureRangeValidation:
    """Unit tests for temperature range validation."""

    def test_validate_temperature_range_accepts_valid_celsius(self):
        """Temperature validation should accept valid Celsius values."""
        result = validate_temperature_range(25.0, unit="C")
        assert result is True

    def test_validate_temperature_range_accepts_zero_celsius(self):
        """Temperature validation should accept 0°C."""
        result = validate_temperature_range(0.0, unit="C")
        assert result is True

    def test_validate_temperature_range_accepts_negative_celsius(self):
        """Temperature validation should accept negative temperatures."""
        result = validate_temperature_range(-50.0, unit="C")
        assert result is True

    def test_validate_temperature_range_rejects_below_absolute_zero_celsius(self):
        """Temperature validation should reject values below absolute zero."""
        with pytest.raises(ValueError, match="below absolute zero"):
            validate_temperature_range(-300.0, unit="C")

    def test_validate_temperature_range_accepts_absolute_zero_kelvin(self):
        """Temperature validation should accept 0K (absolute zero)."""
        result = validate_temperature_range(0.0, unit="K")
        assert result is True

    def test_validate_temperature_range_rejects_negative_kelvin(self):
        """Kelvin scale cannot have negative values."""
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_temperature_range(-1.0, unit="K")

    @pytest.mark.parametrize(
        "temp,unit",
        [
            (25.0, "C"),
            (298.15, "K"),
            (77.0, "F"),
            (100.0, "C"),
            (373.15, "K"),
            (212.0, "F"),
        ],
        ids=[
            "room_temp_celsius",
            "room_temp_kelvin",
            "room_temp_fahrenheit",
            "boiling_celsius",
            "boiling_kelvin",
            "boiling_fahrenheit",
        ],
    )
    def test_validate_temperature_range_accepts_various_valid_temperatures(
        self, temp, unit
    ):
        """Temperature validation handles various valid temperature values."""
        result = validate_temperature_range(temp, unit=unit)
        assert result is True

    def test_validate_temperature_range_rejects_invalid_unit(self):
        """Temperature validation should reject unknown temperature units."""
        with pytest.raises(ValueError, match="Unsupported temperature unit"):
            validate_temperature_range(25.0, unit="X")


class TestTemperatureNormalization:
    """Unit tests for temperature value normalization."""

    def test_normalize_temperature_value_strips_whitespace(self):
        """Normalization should remove leading/trailing whitespace."""
        result = normalize_temperature_value("  25.5  ")
        assert result == 25.5

    def test_normalize_temperature_value_converts_string_to_float(self):
        """Normalization should convert valid string to float."""
        result = normalize_temperature_value("42.3")
        assert result == 42.3
        assert isinstance(result, float)

    def test_normalize_temperature_value_handles_scientific_notation(self):
        """Normalization should parse scientific notation correctly."""
        result = normalize_temperature_value("1.5e2")
        assert result == 150.0

    def test_normalize_temperature_value_raises_error_for_invalid_string(self):
        """Normalization should raise ValueError for non-numeric strings."""
        with pytest.raises(ValueError, match="Invalid temperature value"):
            normalize_temperature_value("not_a_number")

    def test_normalize_temperature_value_handles_none_input(self):
        """Normalization should return None for None input."""
        result = normalize_temperature_value(None)
        assert result is None

    def test_normalize_temperature_value_accepts_numeric_types(self):
        """Normalization should accept int and float without conversion."""
        assert normalize_temperature_value(25) == 25.0
        assert normalize_temperature_value(25.5) == 25.5


class TestTemperatureUnitConversion:
    """Unit tests for temperature unit conversion."""

    def test_convert_temperature_celsius_to_kelvin(self):
        """Celsius to Kelvin conversion: K = C + 273.15."""
        result = convert_temperature_units(0.0, from_unit="C", to_unit="K")
        assert result == 273.15

    def test_convert_temperature_kelvin_to_celsius(self):
        """Kelvin to Celsius conversion: C = K - 273.15."""
        result = convert_temperature_units(273.15, from_unit="K", to_unit="C")
        assert result == 0.0

    def test_convert_temperature_celsius_to_fahrenheit(self):
        """Celsius to Fahrenheit conversion: F = C * 9/5 + 32."""
        result = convert_temperature_units(0.0, from_unit="C", to_unit="F")
        assert result == 32.0

    def test_convert_temperature_fahrenheit_to_celsius(self):
        """Fahrenheit to Celsius conversion: C = (F - 32) * 5/9."""
        result = convert_temperature_units(32.0, from_unit="F", to_unit="C")
        assert result == 0.0

    @pytest.mark.parametrize(
        "value,from_unit,to_unit,expected",
        [
            (100.0, "C", "K", 373.15),
            (373.15, "K", "C", 100.0),
            (100.0, "C", "F", 212.0),
            (212.0, "F", "C", 100.0),
            (25.0, "C", "C", 25.0),  # Same unit
        ],
        ids=[
            "boiling_C_to_K",
            "boiling_K_to_C",
            "boiling_C_to_F",
            "boiling_F_to_C",
            "same_unit_no_change",
        ],
    )
    def test_convert_temperature_multiple_conversions(
        self, value, from_unit, to_unit, expected
    ):
        """Temperature conversion handles various unit combinations."""
        result = convert_temperature_units(value, from_unit=from_unit, to_unit=to_unit)
        assert abs(result - expected) < 0.01  # Allow small floating-point error

    def test_convert_temperature_raises_error_for_invalid_from_unit(self):
        """Conversion should reject unknown source unit."""
        with pytest.raises(ValueError, match="Unsupported temperature unit"):
            convert_temperature_units(25.0, from_unit="X", to_unit="K")

    def test_convert_temperature_raises_error_for_invalid_to_unit(self):
        """Conversion should reject unknown target unit."""
        with pytest.raises(ValueError, match="Unsupported temperature unit"):
            convert_temperature_units(25.0, from_unit="C", to_unit="X")
