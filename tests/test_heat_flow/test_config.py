# Tests for heat_flow FairDM registry configuration – FS-001 User Story 5: every model
# is served by the framework, without custom view code (FR-029-FR-032, FR-034, SC-001,
# SC-007, SC-007a).

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
    """The data attribute names `ModelConfiguration` itself recognises (FS-001).

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
        for model in _get_all_models():
            assert fairdm.registry.is_registered(model), (
                f"{model.__name__} is not registered with the FairDM registry"
            )

    def test_registry_config_has_fields(self):
        for model in _get_all_models():
            config = fairdm.registry.get_for_model(model)
            assert bool(config.fields), f"{model.__name__} config.fields is empty"

    def test_metadata_carries_authority_and_citation(self):
        # FS-001 FR-030, SC-007: every configuration's metadata carries the commission's
        # authority and its citation. The registry reads `metadata`, not the bare
        # `authority`/`citation` class attributes a configuration might declare.
        from heat_flow.config import IHFCConfig

        for model in _get_all_models():
            config = fairdm.registry.get_for_model(model)
            assert config.metadata is not None, f"{model.__name__} has no metadata"
            assert config.metadata.authority is not None, (
                f"{model.__name__} metadata carries no authority"
            )
            assert config.metadata.authority.name == IHFCConfig.metadata.authority.name
            assert config.metadata.citation is not None, (
                f"{model.__name__} metadata carries no citation"
            )
            assert config.metadata.citation.text == IHFCConfig.metadata.citation.text

    def test_filterset_and_table_classes_are_usable(self):
        # FS-001 FR-032, SC-007: every configuration resolves to a usable filter set
        # class and a usable table class, whether supplied or generated.
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
        # FS-001 FR-031, SC-007a: no configuration in this app declares an attribute
        # the registry does not read. Checked against the framework's own recognised
        # set, so the class of defect is closed rather than today's three instances.
        recognised = _recognised_attribute_names()

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
        # FS-001 FR-029: models extending neither `Sample` nor `Measurement` are
        # absent from the registry.
        from heat_flow.models import HeatFlowCorrection, ProbeMetadata

        assert not fairdm.registry.is_registered(ProbeMetadata)
        assert not fairdm.registry.is_registered(HeatFlowCorrection)

    @pytest.mark.django_db
    def test_system_checks_pass(self):
        # FS-001 FR-034, SC-001: Django system checks report no errors and no warnings.
        # The default failure level only fails on ERROR; raised to WARNING here so a
        # warning cannot hide behind an exit code of zero.
        from django.core.management import call_command

        call_command("check", fail_level="WARNING")
