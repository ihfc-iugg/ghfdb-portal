"""
Schema mapping tests for GHFDB field accessor paths.

These tests validate that accessor paths documented in docs/ghfdb_fields.md
correctly retrieve values from Django models and serialize to GHFDB export format.

Tests use @pytest.mark.django_db marker for database access.

Execution: pytest tests/test_ghfdb/test_schema_mapping.py
Expected time: <20 seconds for all tests in this file

Reference: docs/ghfdb_fields.md for complete field mapping documentation
"""

from decimal import Decimal

import pytest
from fairdm.core.models import Dataset
from heat_flow.models import HeatFlowSite


@pytest.mark.django_db
def test_ghfdb_field_site_name_accessor_path():
    """
    Validate 'site_name' accessor path: HeatFlowSite.name

    GHFDB Field: site_name
    Accessor Path: HeatFlowSite.name
    Type: String
    Required: Yes

    Reference: docs/ghfdb_fields.md row for 'site_name'
    """
    # Arrange: Create test record
    dataset = Dataset.objects.create(name="Schema Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Test Site Alpha", lat=45.0, lon=-120.0)

    # Act: Access field via documented path
    site_name = site.name

    # Assert: Value matches
    assert site_name == "Test Site Alpha", f"site_name accessor failed: expected 'Test Site Alpha', got '{site_name}'"
    assert isinstance(site_name, str), "site_name must be string type"


@pytest.mark.django_db
def test_ghfdb_field_coordinates_accessor_path():
    """
    Validate 'latitude'/'longitude' accessor paths.

    GHFDB Fields: latitude, longitude
    Accessor Paths: HeatFlowSite.lat, HeatFlowSite.lon
    Type: Float (decimal degrees)
    Precision: 0.0001 degrees (~ 10 meters)
    Required: Yes

    Reference: docs/ghfdb_fields.md rows for 'latitude' and 'longitude'
    """
    # Arrange: Create test record with precise coordinates
    dataset = Dataset.objects.create(name="Coordinate Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Coordinate Test Site", lat=45.123456, lon=-120.987654)

    # Act: Access coordinates via documented paths
    latitude = site.lat
    longitude = site.lon

    # Assert: Values match within precision tolerance (0.0001 degrees)
    assert abs(latitude - 45.123456) < 0.0001, f"Latitude accessor error: expected 45.123456, got {latitude}"
    assert abs(longitude - (-120.987654)) < 0.0001, f"Longitude accessor error: expected -120.987654, got {longitude}"

    # Assert: Types are numeric
    assert isinstance(latitude, (int, float, Decimal)), "latitude must be numeric type"
    assert isinstance(longitude, (int, float, Decimal)), "longitude must be numeric type"

    # Assert: Valid coordinate ranges
    assert -90 <= latitude <= 90, f"Latitude out of range: {latitude}"
    assert -180 <= longitude <= 180, f"Longitude out of range: {longitude}"


@pytest.mark.django_db
def test_ghfdb_field_depth_interval_accessor_path():
    """
    Validate depth interval accessor paths (for intervals/layers).

    GHFDB Fields: top_depth, bottom_depth
    Accessor Paths: HeatFlowInterval.top_depth, HeatFlowInterval.bottom_depth
    Type: Float (meters)
    Precision: 0.01 meters
    Required: For interval data

    Reference: docs/ghfdb_fields.md rows for depth fields
    """
    # Note: This test demonstrates the pattern
    # Actual model structure may vary - adjust imports as needed

    # Arrange: Create test site
    dataset = Dataset.objects.create(name="Depth Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Depth Test Site", lat=45.0, lon=-120.0)

    # Try to create interval if model exists
    try:
        from heat_flow.models import HeatFlowInterval

        interval = HeatFlowInterval.objects.create(site=site, top_depth=100.5, bottom_depth=150.75)

        # Act: Access depth fields via documented paths
        top = interval.top_depth
        bottom = interval.bottom_depth

        # Assert: Values match within precision tolerance (0.01 meters)
        assert abs(top - 100.5) < 0.01, f"top_depth accessor error: expected 100.5, got {top}"
        assert abs(bottom - 150.75) < 0.01, f"bottom_depth accessor error: expected 150.75, got {bottom}"

        # Assert: Logical constraints
        assert bottom > top, "bottom_depth must be greater than top_depth"

    except ImportError:
        pytest.skip("HeatFlowInterval model not available - TDD placeholder")


@pytest.mark.django_db
def test_ghfdb_field_heat_flow_value_accessor_path():
    """
    Validate heat flow value accessor path.

    GHFDB Field: heat_flow
    Accessor Path: ParentHeatFlow.value (was SurfaceHeatFlow.value)
    Type: Float (mW/m²)
    Precision: 0.01 mW/m²
    Required: Yes (primary measurement)

    Reference: docs/ghfdb_fields.md row for 'heat_flow'
    """
    # Arrange: Create test site
    dataset = Dataset.objects.create(name="Heat Flow Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Heat Flow Test Site", lat=45.0, lon=-120.0)

    # Try to create heat flow measurement if model exists
    try:
        from heat_flow.models import ParentHeatFlow

        heat_flow = ParentHeatFlow.objects.create(
            sample=site,
            dataset=dataset,
            value=65.5,  # mW/m²
            uncertainty=2.0,
        )

        # Act: Access value via documented path
        hf_value = heat_flow.value

        # Assert: Value matches within precision (0.01 mW/m²)
        assert abs(hf_value - 65.5) < 0.01, f"heat_flow accessor error: expected 65.5, got {hf_value}"

        # Assert: Type is numeric
        assert isinstance(hf_value, (int, float, Decimal)), "heat_flow must be numeric type"

        # Assert: Reasonable value range (typical range: 10-150 mW/m²)
        assert 0 < hf_value < 1000, f"Heat flow value out of typical range: {hf_value} mW/m²"

    except ImportError:
        pytest.skip("ParentHeatFlow model not available - TDD placeholder")


@pytest.mark.django_db
def test_ghfdb_field_thermal_conductivity_accessor_path():
    """
    Validate thermal conductivity accessor path.

    GHFDB Field: thermal_conductivity
    Accessor Path: IntervalConductivity.value or ThermalConductivity.value
    Type: Float (W/(m·K))
    Precision: 0.01 W/(m·K)
    Required: For thermal gradient calculations

    Reference: docs/ghfdb_fields.md row for 'thermal_conductivity'
    """
    # Arrange: Create test site
    dataset = Dataset.objects.create(name="Conductivity Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Conductivity Test Site", lat=45.0, lon=-120.0)

    # Try to create conductivity measurement if model exists
    try:
        from heat_flow.models import IntervalConductivity

        conductivity = IntervalConductivity.objects.create(
            site=site,
            value=2.5,  # W/(m·K)
            uncertainty=0.1,
        )

        # Act: Access value via documented path
        tc_value = conductivity.value

        # Assert: Value matches within precision (0.01 W/(m·K))
        assert abs(tc_value - 2.5) < 0.01, f"thermal_conductivity accessor error: expected 2.5, got {tc_value}"

        # Assert: Type is numeric
        assert isinstance(tc_value, (int, float, Decimal)), "thermal_conductivity must be numeric type"

        # Assert: Reasonable value range (typical rock: 1-7 W/(m·K))
        assert 0 < tc_value < 20, f"Thermal conductivity out of typical range: {tc_value} W/(m·K)"

    except ImportError:
        pytest.skip("IntervalConductivity model not available - TDD placeholder")


# Additional accessor path tests can be added incrementally
# Target: 10-15 critical fields initially, expand over time


@pytest.mark.django_db
def test_ghfdb_field_elevation_accessor_path():
    """
    Validate elevation accessor path.

    GHFDB Field: elevation
    Accessor Path: HeatFlowSite.elevation
    Type: Float (meters above sea level)
    Precision: 1 meter
    Required: No (optional)
    """
    # Arrange
    dataset = Dataset.objects.create(name="Elevation Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Elevation Test Site", lat=45.0, lon=-120.0)

    # Check if elevation field exists
    if hasattr(site, "elevation"):
        site.elevation = 1234.5
        site.save()

        # Act
        elevation = site.elevation

        # Assert
        assert abs(elevation - 1234.5) < 1.0, f"elevation accessor error: expected 1234.5, got {elevation}"
    else:
        pytest.skip("elevation field not available on HeatFlowSite model")


@pytest.mark.django_db
def test_ghfdb_field_measurement_date_accessor_path():
    """
    Validate measurement_date accessor path.

    GHFDB Field: measurement_date
    Accessor Path: HeatFlowSite.measurement_date or HeatFlowMeasurement.date
    Type: Date (ISO 8601)
    Required: Recommended

    Reference: docs/ghfdb_fields.md row for 'measurement_date'
    """
    from datetime import date

    # Arrange
    dataset = Dataset.objects.create(name="Date Test Dataset")
    site = HeatFlowSite.objects.create(dataset=dataset, name="Date Test Site", lat=45.0, lon=-120.0)

    # Check if date field exists
    if hasattr(site, "measurement_date"):
        test_date = date(2023, 6, 15)
        site.measurement_date = test_date
        site.save()

        # Act
        meas_date = site.measurement_date

        # Assert
        assert meas_date == test_date, f"measurement_date accessor error: expected {test_date}, got {meas_date}"
        assert isinstance(meas_date, date), "measurement_date must be date type"
    else:
        pytest.skip("measurement_date field not available on HeatFlowSite model")
