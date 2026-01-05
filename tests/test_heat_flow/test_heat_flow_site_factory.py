"""
Tests specifically for HeatFlowSiteFactory.
"""

from django.test import TestCase
from heat_flow.factories import HeatFlowSiteFactory
from heat_flow.models import HeatFlowSite


class TestHeatFlowSiteFactory(TestCase):
    """Test HeatFlowSiteFactory functionality."""

    def test_heat_flow_site_factory_can_create_instance(self):
        """Test that HeatFlowSiteFactory can create a basic instance."""
        site = HeatFlowSiteFactory()

        # Verify the instance was created and is the correct type
        self.assertIsInstance(site, HeatFlowSite)
        self.assertIsNotNone(site.pk)

    def test_heat_flow_site_factory_fields(self):
        """Test that HeatFlowSiteFactory creates instances with expected field values."""
        site = HeatFlowSiteFactory()

        # Test that basic fields are populated
        self.assertIsNotNone(site.environment)
        self.assertIsNotNone(site.explo_method)

        # Test that the environment field has a valid value
        self.assertIsInstance(site.environment, str)

        # Test that explo_method field has a valid value
        self.assertIsInstance(site.explo_method, str)

    def test_heat_flow_site_factory_batch_creation(self):
        """Test that HeatFlowSiteFactory can create multiple instances."""
        sites = HeatFlowSiteFactory.build_batch(5)

        # Verify we get the expected number of instances
        self.assertEqual(len(sites), 5)

        # Verify all instances are of the correct type
        for site in sites:
            self.assertIsInstance(site, HeatFlowSite)

    def test_heat_flow_site_factory_create_batch(self):
        """Test that HeatFlowSiteFactory can create and save multiple instances."""
        sites = HeatFlowSiteFactory.create_batch(3)

        # Verify we get the expected number of instances
        self.assertEqual(len(sites), 3)

        # Verify all instances are saved to the database
        for site in sites:
            self.assertIsInstance(site, HeatFlowSite)
            self.assertIsNotNone(site.pk)

        # Verify they exist in the database
        self.assertEqual(HeatFlowSite.objects.count(), 3)

    def test_heat_flow_site_factory_with_custom_values(self):
        """Test that HeatFlowSiteFactory can accept custom field values."""
        # Use a valid value from the choices
        custom_environment = "terrestrial"
        site = HeatFlowSiteFactory(environment=custom_environment)

        # Verify the custom value was used
        self.assertEqual(site.environment, custom_environment)

    def test_heat_flow_site_factory_build_vs_create(self):
        """Test the difference between build() and create() methods."""
        # build() should create instance without saving to database
        built_site = HeatFlowSiteFactory.build()
        self.assertIsInstance(built_site, HeatFlowSite)
        self.assertIsNone(built_site.pk)  # Not saved, so no primary key

        # create() should create and save instance to database
        created_site = HeatFlowSiteFactory.create()
        self.assertIsInstance(created_site, HeatFlowSite)
        self.assertIsNotNone(created_site.pk)  # Saved, so has primary key

        # Verify only the created site is in the database
        self.assertEqual(HeatFlowSite.objects.count(), 1)
        self.assertEqual(HeatFlowSite.objects.first(), created_site)

    def test_heat_flow_site_factory_inheritance(self):
        """Test that HeatFlowSiteFactory properly inherits from SampleFactory."""
        site = HeatFlowSiteFactory()

        # Verify inherited fields from Sample/Borehole are present
        # These should be inherited from the parent factory/model
        self.assertIsNotNone(site.name)  # Should inherit name field

        # Verify it has the specific HeatFlowSite fields
        self.assertTrue(hasattr(site, "environment"))
        self.assertTrue(hasattr(site, "explo_method"))
        self.assertTrue(hasattr(site, "explo_purpose"))

    def test_heat_flow_site_factory_many_to_many_field_handling(self):
        """Test that the factory handles the ConceptManyToManyField correctly."""
        site = HeatFlowSiteFactory()

        # explo_purpose is a ConceptManyToManyField that should be empty/not set by factory
        # since we commented it out in the factory
        self.assertEqual(site.explo_purpose.count(), 0)

        # But we should be able to add values to it manually
        # (This tests that the field exists and works correctly)
        self.assertTrue(hasattr(site.explo_purpose, "add"))
        self.assertTrue(hasattr(site.explo_purpose, "count"))
