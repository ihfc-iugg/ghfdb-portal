"""
Tests for heat flow factories.
"""

from django.test import TestCase
from heat_flow.factories import (
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    SurfaceHeatFlowFactory,
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
        surface_heat_flow = SurfaceHeatFlowFactory()
        heat_flow = HeatFlowFactory()
        thermal_gradient = ThermalGradientFactory()
        interval_conductivity = IntervalConductivityFactory()

        # Basic assertions to ensure objects were created
        self.assertIsNotNone(site.pk)
        self.assertIsNotNone(interval.pk)
        self.assertIsNotNone(surface_heat_flow.pk)
        self.assertIsNotNone(heat_flow.pk)
        self.assertIsNotNone(thermal_gradient.pk)
        self.assertIsNotNone(interval_conductivity.pk)

    def test_all_factories_can_build_instances(self):
        """Test that all heat flow factories can build instances without saving."""
        # Test site and interval factories
        site = HeatFlowSiteFactory.build()
        interval = HeatFlowIntervalFactory.build()

        # Test measurement factories
        surface_heat_flow = SurfaceHeatFlowFactory.build()
        heat_flow = HeatFlowFactory.build()
        thermal_gradient = ThermalGradientFactory.build()
        interval_conductivity = IntervalConductivityFactory.build()

        # Built instances should not have PKs
        self.assertIsNone(site.pk)
        self.assertIsNone(interval.pk)
        self.assertIsNone(surface_heat_flow.pk)
        self.assertIsNone(heat_flow.pk)
        self.assertIsNone(thermal_gradient.pk)
        self.assertIsNone(interval_conductivity.pk)

    def test_heat_flow_site_factory_fields(self):
        """Test that HeatFlowSiteFactory populates vocabulary fields correctly."""
        site = HeatFlowSiteFactory()

        # Check that vocabulary fields are populated
        self.assertIsNotNone(site.environment)
        # explo_method and explo_purpose can be None as they're nullable

    def test_surface_heat_flow_factory_fields(self):
        """Test that SurfaceHeatFlowFactory populates fields correctly."""
        surface_heat_flow = SurfaceHeatFlowFactory()

        # Check that required fields are populated
        self.assertIsNotNone(surface_heat_flow.value)
        self.assertIsNotNone(surface_heat_flow.uncertainty)
        self.assertIsInstance(surface_heat_flow.is_ghfdb, bool)

        # Check that uncertainty is reasonable (should be a fraction of value)
        self.assertGreater(surface_heat_flow.uncertainty, 0)
        self.assertLess(surface_heat_flow.uncertainty, surface_heat_flow.value)

    def test_heat_flow_factory_fields(self):
        """Test that HeatFlowFactory populates fields correctly."""
        heat_flow = HeatFlowFactory()

        # Check that required fields are populated
        self.assertIsNotNone(heat_flow.value)
        self.assertIsNotNone(heat_flow.uncertainty)
        self.assertIsInstance(heat_flow.relevant_child, bool)

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
        """Test creating factories with relationships."""
        # Create a surface heat flow with children
        surface_heat_flow = SurfaceHeatFlowFactory()

        # Create child heat flow measurements
        child1 = HeatFlowFactory(parent=surface_heat_flow)
        child2 = HeatFlowFactory(parent=surface_heat_flow)

        # Check relationships
        self.assertEqual(child1.parent, surface_heat_flow)
        self.assertEqual(child2.parent, surface_heat_flow)
        self.assertIn(child1, surface_heat_flow.children.all())
        self.assertIn(child2, surface_heat_flow.children.all())

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
