"""
Tests for heat flow factories.
"""

import pytest
from django.test import TestCase
from heat_flow.factories import (
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ThermalGradientFactory,
)


class TestHeatFlowFactories(TestCase):
    """Test heat flow factories functionality."""

    def test_all_factories_can_create_instances(self):
        """Test that all heat flow factories can create basic instances without errors."""
        # Test site and interval factories
        site = HeatFlowSiteFactory()
        interval = HeatFlowIntervalFactory()

        # Test measurement factories
        # Note: SurfaceHeatFlow removed, now using ParentHeatFlow in ghfdb app
        heat_flow = HeatFlowFactory()
        thermal_gradient = ThermalGradientFactory()
        interval_conductivity = IntervalConductivityFactory()

        # Basic assertions to ensure objects were created
        self.assertIsNotNone(site.pk)
        self.assertIsNotNone(interval.pk)
        # Note: SurfaceHeatFlow removed, now using ParentHeatFlow in ghfdb app
        self.assertIsNotNone(heat_flow.pk)
        self.assertIsNotNone(thermal_gradient.pk)
        self.assertIsNotNone(interval_conductivity.pk)

    def test_all_factories_can_build_instances(self):
        """Test that all heat flow factories can build instances without saving."""
        # Test site and interval factories
        site = HeatFlowSiteFactory.build()
        interval = HeatFlowIntervalFactory.build()

        # Test measurement factories
        # Note: SurfaceHeatFlow removed, now using ParentHeatFlow in ghfdb app
        heat_flow = HeatFlowFactory.build()
        thermal_gradient = ThermalGradientFactory.build()
        interval_conductivity = IntervalConductivityFactory.build()

        # Built instances should not have PKs
        self.assertIsNone(site.pk)
        self.assertIsNone(interval.pk)
        # Note: SurfaceHeatFlow removed, now using ParentHeatFlow in ghfdb app
        self.assertIsNone(heat_flow.pk)
        self.assertIsNone(thermal_gradient.pk)
        self.assertIsNone(interval_conductivity.pk)

    def test_heat_flow_site_factory_fields(self):
        """Test that HeatFlowSiteFactory populates vocabulary fields correctly."""
        site = HeatFlowSiteFactory()

        # Check that vocabulary fields are populated
        self.assertIsNotNone(site.environment)
        # explo_method and explo_purpose can be None as they're nullable

    def test_heat_flow_factory_fields(self):
        """Test that HeatFlowFactory populates fields correctly."""
        heat_flow = HeatFlowFactory()

        # Check that required fields are populated
        self.assertIsNotNone(heat_flow.value)
        self.assertIsNotNone(heat_flow.uncertainty)
        # Note: relevant_child field removed from HeatFlow model

        # Check that uncertainty is reasonable
        self.assertGreater(heat_flow.uncertainty, 0)
        self.assertLess(heat_flow.uncertainty, heat_flow.value)

    def test_thermal_gradient_factory_fields(self):
        """Test that ThermalGradientFactory populates fields correctly."""
        thermal_gradient = ThermalGradientFactory()

        # Check that required fields are populated
        self.assertIsNotNone(thermal_gradient.value)
        self.assertIsNotNone(thermal_gradient.uncertainty)
        self.assertIsNotNone(thermal_gradient.score)

        # Check that score is within valid range
        self.assertGreaterEqual(thermal_gradient.score, 0.0)
        self.assertLessEqual(thermal_gradient.score, 1.0)

        # Check that number is positive
        if thermal_gradient.number:
            self.assertGreater(thermal_gradient.number, 0)

    def test_interval_conductivity_factory_fields(self):
        """Test that IntervalConductivityFactory populates fields correctly."""
        conductivity = IntervalConductivityFactory()

        # Check that required fields are populated
        self.assertIsNotNone(conductivity.value)
        self.assertIsNotNone(conductivity.uncertainty)

        # Check that values are positive
        self.assertGreater(conductivity.value, 0)
        self.assertGreater(conductivity.uncertainty, 0)

        # Check that number is positive
        if conductivity.number:
            self.assertGreater(conductivity.number, 0)

    def test_factories_with_relationships(self):
        \"\"\"Test creating factories with relationships - DISABLED due to architectural changes.\"\"\"
        # NOTE: This test disabled because parent-child relationship changed.
        # Previously: HeatFlow had FK to SurfaceHeatFlow (parent field)
        # Now: ParentHeatFlow has M2M to HeatFlow via ParentChildRelation through table
        # This test would need to be rewritten for the new ghfdb app structure.
        pytest.skip(\"Parent-child relationship changed - test needs rewrite for ParentChildRelation\")

    def test_thermal_gradient_with_corrections(self):
        """Test that thermal gradient can have corrected values."""
        # Create gradient without corrected values
        gradient1 = ThermalGradientFactory(corrected_value=None, corrected_uncertainty=None)
        self.assertIsNone(gradient1.corrected_value)
        self.assertIsNone(gradient1.corrected_uncertainty)

        # Create gradient with corrected values
        gradient2 = ThermalGradientFactory()
        if gradient2.corrected_value:
            self.assertIsNotNone(gradient2.corrected_uncertainty)

    def test_factory_batch_creation(self):
        """Test creating multiple instances at once."""
        # Create batch of heat flow measurements
        heat_flows = HeatFlowFactory.create_batch(5)
        self.assertEqual(len(heat_flows), 5)

        # All should have valid PKs
        for hf in heat_flows:
            self.assertIsNotNone(hf.pk)
            self.assertIsNotNone(hf.value)
