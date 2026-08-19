"""
Tests for heat flow factories.

T049 — US5: All 7 factory classes produce saved instances.
"""

import pytest


class TestHeatFlowFactories:
    @pytest.mark.django_db
    def test_all_factories_produce_saved_instances(self):
        """
        T049 – Each of the 7 factory classes creates a saved instance with a non-null PK
        in a single call (FR-028, SC-007, A7).
        """
        from heat_flow.factories import (
            HeatFlowFactory,
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            IntervalConductivityFactory,
            ParentHeatFlowFactory,
            ProbeMetadataFactory,
            ThermalGradientFactory,
        )

        assert HeatFlowSiteFactory().pk is not None
        assert HeatFlowIntervalFactory().pk is not None
        assert ParentHeatFlowFactory().pk is not None
        assert ThermalGradientFactory().pk is not None
        assert IntervalConductivityFactory().pk is not None
        assert HeatFlowFactory().pk is not None
        assert ProbeMetadataFactory().pk is not None

    @pytest.mark.django_db
    def test_heat_flow_site_factory_save(self):
        """T049 – HeatFlowSiteFactory smoke test."""
        from heat_flow.factories import HeatFlowSiteFactory

        assert HeatFlowSiteFactory().pk is not None

    @pytest.mark.django_db
    def test_heat_flow_interval_factory_save(self):
        """T049 – HeatFlowIntervalFactory smoke test; site FK populated via SubFactory."""
        from heat_flow.factories import HeatFlowIntervalFactory

        interval = HeatFlowIntervalFactory()
        assert interval.pk is not None
        assert interval.site_id is not None

    @pytest.mark.django_db
    def test_parent_heat_flow_factory_save(self):
        """T049 – ParentHeatFlowFactory smoke test; creates a ParentHeatFlow with a HeatFlowSite sample."""
        from heat_flow.factories import ParentHeatFlowFactory

        parent = ParentHeatFlowFactory()
        assert parent.pk is not None
        assert (
            parent.sample_id is not None
        )  # SubFactory(HeatFlowSiteFactory) provides a valid site

    @pytest.mark.django_db
    def test_probe_metadata_factory_save(self):
        """T049 – ProbeMetadataFactory smoke test; interval SubFactory creates linked interval."""
        from heat_flow.factories import ProbeMetadataFactory

        probe = ProbeMetadataFactory()
        assert probe.pk is not None
        assert probe.interval_id is not None
