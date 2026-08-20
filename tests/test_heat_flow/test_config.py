"""
Tests for heat_flow FairDM registry configuration – User Story US-5.

US-5: every model is served by the framework, without custom view code
(FR-029–FR-032, FR-034, SC-001, SC-007, SC-007a).
"""

import inspect

import fairdm
import pytest
from django_filters import FilterSet
from django_tables2 import Table
from fairdm.registry.config import ModelConfiguration

ALL_MODELS_NAMES = [
    "HeatFlowSite",
    "HeatFlowInterval",
    "ParentHeatFlow",
    "HeatFlow",
    "ThermalGradient",
    "IntervalConductivity",
]


def _get_all_models():
    from heat_flow.models import (
        HeatFlow,
        HeatFlowInterval,
        HeatFlowSite,
        IntervalConductivity,
        ParentHeatFlow,
        ThermalGradient,
    )

    return [
        HeatFlowSite,
        HeatFlowInterval,
        ParentHeatFlow,
        HeatFlow,
        ThermalGradient,
        IntervalConductivity,
    ]


def _recognised_attribute_names() -> set[str]:
    """The data attribute names `ModelConfiguration` itself recognises (R4).

    Derived from the framework's own class body rather than hard-coded, so that a
    change to the framework's contract changes what this test allows without a
    separate edit here.
    """
    return {
        name
        for name, value in vars(ModelConfiguration).items()
        if not name.startswith("_") and not inspect.isroutine(value)
    }


class TestHeatFlowRegistryConfig:
    def test_all_six_models_registered(self):
        """
        T066 – All six heat-flow models appear in the FairDM registry (FR-029, SC-007).
        """
        for model in _get_all_models():
            assert fairdm.registry.is_registered(model), (
                f"{model.__name__} is not registered with the FairDM registry"
            )

    def test_registry_config_has_fields(self):
        """
        T067 – Every registered model config declares a non-empty fields list (FR-031, SC-007).
        """
        for model in _get_all_models():
            config = fairdm.registry.get_for_model(model)
            assert bool(config.fields), f"{model.__name__} config.fields is empty"

    def test_metadata_carries_authority_and_citation(self):
        """
        T068 – Every configuration's metadata carries the commission's authority and
        its citation (FR-030, SC-007). The registry reads `metadata`, not the bare
        `authority`/`citation` class attributes a configuration might declare.
        """
        from heat_flow.config import IHFCConfig

        for model in _get_all_models():
            config = fairdm.registry.get_for_model(model)
            assert config.metadata is not None, f"{model.__name__} has no metadata"
            assert config.metadata.authority is not None, (
                f"{model.__name__} metadata carries no authority"
            )
            assert config.metadata.authority.name == IHFCConfig.authority.name
            assert config.metadata.citation is not None, (
                f"{model.__name__} metadata carries no citation"
            )
            assert config.metadata.citation.text == IHFCConfig.citation.text

    def test_filterset_and_table_classes_are_usable(self):
        """
        T069 – Every configuration resolves to a usable filter set class and a usable
        table class, whether supplied or generated (FR-032, SC-007).
        """
        for model in _get_all_models():
            config = fairdm.registry.get_for_model(model)
            filterset_class = config.get_filterset_class()
            assert issubclass(filterset_class, FilterSet), (
                f"{model.__name__} filterset class {filterset_class!r} is not usable"
            )
            table_class = config.get_table_class()
            assert issubclass(table_class, Table), (
                f"{model.__name__} table class {table_class!r} is not usable"
            )

    def test_no_configuration_declares_an_unread_attribute(self):
        """
        T070 – No configuration in this app declares an attribute the registry does
        not read (FR-031, SC-007a). Checked against the framework's own recognised
        set, so the class of defect is closed rather than today's three instances.
        """
        recognised = _recognised_attribute_names()
        # IHFCConfig's own contract (T073): consumed by its __init__ to build the
        # `metadata` the registry reads. Not dead, even though the registry never
        # reads a configuration's `authority`/`citation`/`keywords`/`repository_url`
        # directly.
        recognised |= {"authority", "citation", "repository_url", "keywords"}

        for model in _get_all_models():
            config_cls = type(fairdm.registry.get_for_model(model))
            for klass in config_cls.__mro__:
                if klass.__module__ != "heat_flow.config":
                    continue
                declared = {
                    name
                    for name, value in vars(klass).items()
                    if not name.startswith("_") and not inspect.isroutine(value)
                }
                unread = declared - recognised
                assert not unread, (
                    f"{klass.__name__} declares attribute(s) the registry does not "
                    f"read: {sorted(unread)}"
                )

    def test_probe_metadata_and_correction_are_not_registered(self):
        """
        T072 – Models extending neither `Sample` nor `Measurement` are absent from
        the registry (FR-029).
        """
        from heat_flow.models import HeatFlowCorrection, ProbeMetadata

        assert not fairdm.registry.is_registered(ProbeMetadata)
        assert not fairdm.registry.is_registered(HeatFlowCorrection)

    @pytest.mark.django_db
    def test_system_checks_pass(self):
        """
        T071 – Django system checks report no errors and no warnings (FR-034, SC-001).
        The default failure level only fails on ERROR; raised to WARNING here so a
        warning cannot hide behind an exit code of zero.
        """
        from django.core.management import call_command

        call_command("check", fail_level="WARNING")
