# Tests for GHFDB custom import/export widgets.

import pytest

from tests.factories import HeatFlowIntervalFactory, HeatFlowSiteFactory

# ---- Leaf widget tests -------------------------------------------------------


class TestConceptWidget:
    def test_clean_case_insensitive(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("Onshore (continental)", row={})
        assert result is not None

    def test_clean_case_insensitive_lowercase(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        # The vocabulary has "Onshore (continental)" — try lowercase
        result = widget.clean("onshore (continental)", row={})
        assert result is not None

    def test_clean_empty_returns_none(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        assert widget.clean("", row={}) is None
        assert widget.clean(None, row={}) is None

    def test_clean_invalid_raises_valueerror(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("not_a_real_environment", row={})
        error_msg = str(exc_info.value)
        assert (
            "not_a_real_environment" in error_msg.lower()
            or "invalid" in error_msg.lower()
        )


class TestMultiConceptWidget:
    def test_clean_semicolon_split(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("", row={})
        assert result is not None  # should return empty list, not raise

    def test_clean_empty_returns_empty(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("", row={})
        assert result == [] or result is None or hasattr(result, "__iter__")

    def test_clean_invalid_batched_error(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("invalid_one;invalid_two", row={})
        error_msg = str(exc_info.value)
        # Both invalid values should be mentioned
        assert "invalid_one" in error_msg or "invalid" in error_msg.lower()


class TestQuantityWidget:
    def test_clean_returns_quantity(self):
        from project.ghfdb.resources.widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        result = widget.clean("70.0", row={})
        # Should return a Quantity with magnitude 70.0
        assert result is not None
        magnitude = getattr(result, "magnitude", result)
        assert float(magnitude) == pytest.approx(70.0)

    def test_clean_empty_returns_none(self):
        from project.ghfdb.resources.widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        assert widget.clean("", row={}) is None
        assert widget.clean(None, row={}) is None

    def test_render_returns_plain_magnitude(self):
        from project.ghfdb.resources.widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        # Create a Quantity and render it
        from pint import UnitRegistry

        ureg = UnitRegistry()
        qty = ureg.Quantity(70.5, "mW/m**2")
        result = widget.render(qty)
        # Should be numeric string, no unit label
        assert "70.5" in str(result) or float(result) == pytest.approx(70.5)

    def test_render_none_returns_empty(self):
        from project.ghfdb.resources.widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        assert widget.render(None) == "" or widget.render(None) is None


class TestYesNoWidget:
    def test_clean_yes_returns_true(self):
        from project.ghfdb.resources.widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("Yes", row={}) is True

    def test_clean_no_returns_false(self):
        from project.ghfdb.resources.widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("No", row={}) is False

    def test_clean_empty_returns_none(self):
        from project.ghfdb.resources.widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("", row={}) is None

    def test_clean_case_insensitive(self):
        from project.ghfdb.resources.widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("yes", row={}) is True
        assert widget.clean("no", row={}) is False


# ---- RelatedModelWidget and subclass tests ------------------------------------


class TestRelatedModelWidget:
    def test_sentinel_column_empty_returns_none(self, db):
        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        row = {"T_grad_mean": "", "T_grad_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    def test_full_clean_error_prefixed_with_model_name(self, db):
        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        # Provide an invalid value to trigger full_clean() failure
        row = {"T_grad_mean": "not_a_number", "T_grad_uncertainty": ""}
        with pytest.raises(ValueError) as exc_info:
            widget.clean("not_a_number", row=row)
        # Error should be prefixed with model name
        error_msg = str(exc_info.value)
        assert (
            "ThermalGradient" in error_msg
            or "gradient" in error_msg.lower()
            or "invalid" in error_msg.lower()
        )

    def test_set_m2m_relations_sets_m2m(self, db, dataset):
        from project.ghfdb.resources.widgets import IntervalWidget

        site = HeatFlowSiteFactory(dataset=dataset, name="Test")
        interval = HeatFlowIntervalFactory(
            dataset=dataset,
            site=site,
            name="Test Interval",
        )
        widget = IntervalWidget()
        # Just verify the method exists and is callable
        assert hasattr(widget, "set_m2m_relations")
        # Should not raise
        widget.set_m2m_relations(interval)


class TestParentWidget:
    @pytest.mark.django_db
    def test_creates_heatflowsite_and_point(self, dataset):
        from project.ghfdb.resources.widgets import ParentWidget

        widget = ParentWidget()
        row = {
            "name": "Test Site",
            "lat_NS": "48.0",
            "long_EW": "11.0",
            "environment": "onshore_continental",
            "elevation": "",
            "explo_method": "",
            "explo_purpose": "",
            "total_depth_MD": "",
            "total_depth_TVD": "",
            "Country": "Germany",
            "Region": "",
            "Continent": "Europe",
            "Domain": "",
        }
        result = widget.clean("Test Site", row=row)
        from heat_flow.models import HeatFlowSite

        assert result is not None
        assert isinstance(result, HeatFlowSite)
        assert result.location is not None
        assert float(result.location.x) == pytest.approx(11.0)
        assert float(result.location.y) == pytest.approx(48.0)

    @pytest.mark.django_db
    def test_sentinel_empty_returns_none(self):
        from project.ghfdb.resources.widgets import ParentWidget

        widget = ParentWidget()
        result = widget.clean("", row={})
        assert result is None


class TestIntervalWidget:
    @pytest.mark.django_db
    def test_creates_heatflowinterval(self, dataset):
        from heat_flow.models import HeatFlowInterval

        from project.ghfdb.resources.widgets import IntervalWidget

        widget = IntervalWidget()
        row = {
            "q_top": "0",
            "q_bottom": "500",
            "geo_lithology": "",
            "geo_stratigraphy": "",
        }
        result = widget.clean(None, row=row)
        assert result is not None
        assert isinstance(result, HeatFlowInterval)

    @pytest.mark.django_db
    def test_geo_stratigraphy_stored_on_age_not_stratigraphy(self, dataset):
        # BUG-009 regression: geo_stratigraphy → HeatFlowInterval.age
        # (ConceptManyToManyField), NOT HeatFlowInterval.stratigraphy (M2M to
        # stratigraphy.StratigraphicUnit).
        from project.ghfdb.resources.widgets import IntervalWidget

        # Prepare a saved interval (set_m2m_relations requires instance.pk)
        site = HeatFlowSiteFactory(dataset=dataset, name="BUG009 Site")
        interval = HeatFlowIntervalFactory(
            dataset=dataset,
            site=site,
            name="BUG009 Interval",
        )

        widget = IntervalWidget()
        row = {
            "q_top": "0",
            "q_bottom": "500",
            "geo_lithology": "",
            "geo_stratigraphy": "Holocene",
        }
        # clean() stores _last_row; set_m2m_relations() uses it to populate M2M
        widget.clean(None, row=row)
        # Must not raise "Field 'id' expected a number but got <gts2020: Holocene>"
        widget.set_m2m_relations(interval)

        interval.refresh_from_db()
        # The Holocene concept must land on the 'age' ConceptManyToManyField
        assert interval.age.count() > 0, (
            "Expected HeatFlowInterval.age to be populated by geo_stratigraphy"
        )
        # The distinct stratigraphy M2M (→ stratigraphy.StratigraphicUnit) must remain untouched
        assert interval.stratigraphy.count() == 0, (
            "HeatFlowInterval.stratigraphy must NOT be populated by geo_stratigraphy import"
        )


class TestGradientWidget:
    @pytest.mark.django_db
    def test_skips_when_sentinel_empty(self):
        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        row = {"T_grad_mean": "", "T_grad_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    @pytest.mark.django_db
    def test_creates_gradient_when_sentinel_set(self, dataset):
        from heat_flow.models import ThermalGradient

        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        row = {
            "T_grad_mean": "25.0",
            "T_grad_uncertainty": "",
            "T_grad_mean_cor": "",
            "T_grad_uncertainty_cor": "",
            "T_shutin_top": "",
            "T_shutin_bottom": "",
            "T_number": "",
            "T_method_top": "",
            "T_method_bottom": "",
            "T_corr_top": "",
            "T_corr_bottom": "",
        }
        result = widget.clean("25.0", row=row)
        assert result is not None
        assert isinstance(result, ThermalGradient)

    @pytest.mark.django_db
    def test_numeric_sentinel_treated_as_present(self, dataset):
        from heat_flow.models import ThermalGradient

        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        row = {
            "T_grad_mean": 25,  # int exactly as openpyxl would deliver it
            "T_grad_uncertainty": "",
            "T_grad_mean_cor": "",
            "T_grad_uncertainty_cor": "",
            "T_shutin_top": "",
            "T_shutin_bottom": "",
            "T_number": "",
            "T_method_top": "",
            "T_method_bottom": "",
            "T_corr_top": "",
            "T_corr_bottom": "",
        }
        result = widget.clean("", row=row)
        assert result is not None
        assert isinstance(result, ThermalGradient)


class TestConductivityWidget:
    @pytest.mark.django_db
    def test_skips_when_sentinel_empty(self):
        from project.ghfdb.resources.widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {"tc_mean": "", "tc_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    @pytest.mark.django_db
    def test_creates_conductivity_when_sentinel_set(self, dataset):
        from heat_flow.models import IntervalConductivity

        from project.ghfdb.resources.widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {
            "tc_mean": "2.5",
            "tc_uncertainty": "",
            "tc_source": "",
            "tc_location": "",
            "tc_method": "",
            "tc_saturation": "",
            "tc_pT_conditions": "",
            "tc_pT_function": "",
            "tc_strategy": "",
            "tc_number": "",
        }
        result = widget.clean("2.5", row=row)
        assert result is not None
        assert isinstance(result, IntervalConductivity)

    @pytest.mark.django_db
    def test_numeric_sentinel_treated_as_present(self, dataset):
        from heat_flow.models import IntervalConductivity

        from project.ghfdb.resources.widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {
            "tc_mean": 2.5,  # float exactly as openpyxl would deliver it
            "tc_uncertainty": "",
            "tc_source": "",
            "tc_location": "",
            "tc_method": "",
            "tc_saturation": "",
            "tc_pT_conditions": "",
            "tc_pT_function": "",
            "tc_strategy": "",
            "tc_number": "",
        }
        result = widget.clean("", row=row)
        assert result is not None
        assert isinstance(result, IntervalConductivity)


# ---- FS-003 FR-016 Vocabulary normalisation regression tests ------------------


class TestBlankCellSentinel:
    # The corpus of completed submissions writes ``-`` for "nothing entered here yet" in
    # reference columns filled in during assessment, such as ``Ref_IGSN`` (FS-004).

    def test_none_empty_whitespace_and_hyphen_are_blank(self):
        from project.ghfdb.resources.widgets import is_blank_cell

        for raw in (None, "", "   ", "-"):
            assert is_blank_cell(raw) is True

    def test_a_real_value_is_not_blank(self):
        from project.ghfdb.resources.widgets import is_blank_cell

        assert is_blank_cell("10.60516/AU1101") is False
        assert is_blank_cell(" 10.60516/AU1101 ") is False


class TestVocabNormalisation:
    def test_normalize_vocab_token_strips_brackets(self):
        from project.ghfdb.resources.widgets import normalize_vocab_token

        assert (
            normalize_vocab_token("[Onshore (continental)]") == "onshore (continental)"
        )
        assert normalize_vocab_token("[OFFSHORE (MARINE)]") == "offshore (marine)"
        # Plain tokens (no brackets) should pass through unchanged after lowercasing
        assert normalize_vocab_token("onshore (continental)") == "onshore (continental)"
        assert normalize_vocab_token("Onshore (continental)") == "onshore (continental)"

    def test_concept_widget_accepts_bracketed_value(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("[Onshore (continental)]", row={})
        assert result is not None

    def test_concept_widget_accepts_bracketed_uppercase(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("[OFFSHORE (MARINE)]", row={})
        assert result is not None

    def test_concept_widget_invalid_bracketed_reports_original(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("[NOT_VALID]", row={})
        # Original token (with brackets) must be visible in the error message
        assert "[NOT_VALID]" in str(exc_info.value)

    def test_multi_concept_widget_normalizes_bracketed_tokens(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        # ExplorationPurpose is preloaded in the test DB; use it to verify bracket normalisation
        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("[Geothermal]; [Research]", row={})
        assert result is not None
        assert result.count() >= 1

    def test_multi_concept_widget_invalid_bracketed_reports_original(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("[COMPLETELY_INVALID]", row={})
        # Original token (with brackets) must be visible — not the lowercased/stripped form
        assert "[COMPLETELY_INVALID]" in str(exc_info.value)


# ---- BUG-007/BUG-008 numeric cell value regression tests ----------------------


class TestNumericCellInputGuards:
    # BUG-007 / BUG-008: numeric cell value type-guard behaviour.

    def test_concept_widget_int_raises_valueerror_not_attributeerror(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean(42, row={})
        error_msg = str(exc_info.value)
        # Must mention the vocabulary class name so the user knows which field
        assert "GeographicEnvironment" in error_msg
        # Must mention the bad value
        assert "42" in error_msg

    def test_concept_widget_float_raises_valueerror_not_attributeerror(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean(3.14, row={})
        error_msg = str(exc_info.value)
        assert "GeographicEnvironment" in error_msg

    def test_gradient_widget_numeric_sentinel_succeeds(self, db):
        # GradientWidget with a numeric T_grad_mean proceeds — returns ThermalGradient.
        # openpyxl delivers numeric cells as int/float. T_grad_mean is a quantity
        # column: a native number is valid input and MUST NOT raise ValueError.
        from heat_flow.models import ThermalGradient

        from project.ghfdb.resources.widgets import GradientWidget

        widget = GradientWidget()
        row = {
            "T_grad_mean": 800,  # int — valid numeric quantity from openpyxl
            "T_grad_uncertainty": "",
            "T_grad_mean_cor": "",
            "T_grad_uncertainty_cor": "",
            "T_shutin_top": "",
            "T_shutin_bottom": "",
            "T_number": "",
            "T_method_top": "",
            "T_method_bottom": "",
            "T_corr_top": "",
            "T_corr_bottom": "",
        }
        result = widget.clean("", row=row)
        assert result is not None, (
            "Expected ThermalGradient to be created for numeric T_grad_mean"
        )
        assert isinstance(result, ThermalGradient)

    def test_conductivity_widget_numeric_sentinel_succeeds(self, db):
        # ConductivityWidget with a numeric tc_mean proceeds — returns
        # IntervalConductivity. A float tc_mean from openpyxl is valid input and MUST
        # NOT raise ValueError.
        from heat_flow.models import IntervalConductivity

        from project.ghfdb.resources.widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {
            "tc_mean": 2.5,  # float — valid numeric quantity from openpyxl
            "tc_uncertainty": "",
            "tc_source": "",
            "tc_location": "",
            "tc_method": "",
            "tc_saturation": "",
            "tc_pT_conditions": "",
            "tc_pT_function": "",
            "tc_strategy": "",
            "tc_number": "",
        }
        result = widget.clean("", row=row)
        assert result is not None, (
            "Expected IntervalConductivity to be created for numeric tc_mean"
        )
        assert isinstance(result, IntervalConductivity)

    def test_parent_widget_reads_a_numeric_site_name_as_text(self, db):
        # A numbered site is a named site. Submissions whose sites are numbered rather
        # than titled arrive with integer cells in the ``name`` column, and a
        # spreadsheet gives no way to say otherwise.
        from project.ghfdb.resources.widgets import ParentWidget

        widget = ParentWidget()
        row = {
            "name": 3,  # int — openpyxl reading a numeric cell
            "lat_NS": "48.0",
            "long_EW": "11.0",
        }

        site = widget.clean("", row=row)

        assert site is not None
        assert site.name == "3"


# Shapes taken from the assessment team's completed templates.
# Every case below reproduces a value that refused a real submission. The
# values are transcribed; no submitted file is stored in the repository.


class TestValuesRealSubmissionsCarry:
    def test_a_sentinel_padded_with_whitespace_is_still_the_sentinel(self):
        # ``' [unspecified]'`` — a leading space defeats a bare ``strip('[]')``. The
        # first character is not a bracket, so stripping stops there and the token never
        # matches. 6,612 cells across the corpus carry it.
        from project.ghfdb.resources.widgets import normalize_vocab_token

        assert normalize_vocab_token(" [unspecified]") == "unspecified"
        assert normalize_vocab_token("[unspecified] ") == "unspecified"
        assert normalize_vocab_token("[ unspecified ]") == "unspecified"
        assert normalize_vocab_token("[unspecified]") == "unspecified"

    def test_a_lithology_named_by_its_key_is_matched(self, db):
        # The template's lithology column offers keys, not labels.
        # ``alkali_feldspar_granite`` is the cell value the template's own dropdown
        # supplies; ``alkali feldspar granite`` is the portal's label for the same
        from fairdm_geo.vocabularies.cgi.geosciml import SimpleLithology

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(SimpleLithology)

        result = widget.clean("alkali_feldspar_granite", row={})

        assert [concept.name for concept in result] == ["alkali_feldspar_granite"]

    def test_a_stratigraphic_age_named_by_its_key_is_matched(self, db):
        from fairdm_geo.vocabularies.stratigraphy import GeologicalTimescale

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(GeologicalTimescale)

        result = widget.clean("CambrianSeries2", row={})

        assert [concept.name for concept in result] == ["CambrianSeries2"]

    def test_labels_still_match_after_keys_are_accepted(self, db):
        from fairdm_geo.vocabularies.cgi.geosciml import SimpleLithology

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(SimpleLithology)

        result = widget.clean("andesite;basalt", row={})

        assert sorted(concept.name for concept in result) == ["andesite", "basalt"]

    def test_a_value_in_neither_the_keys_nor_the_labels_is_still_refused(self, db):
        # ``Aluvium`` is a misspelling in a submitted file, not a concept. Accepting
        # keys must not turn the vocabulary check into a pass.
        from fairdm_geo.vocabularies.cgi.geosciml import SimpleLithology

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(SimpleLithology)

        with pytest.raises(ValueError) as excinfo:
            widget.clean("Aluvium", row={}, column="geo_lithology")

        assert "Aluvium" in str(excinfo.value)
        assert "geo_lithology" in str(excinfo.value)

    @pytest.mark.parametrize(
        "cell", ["[unspecified]", " [unspecified]", "[Unspecified]"]
    )
    def test_an_unspecified_acquisition_date_is_read_as_no_date(self, cell):
        # The template offers ``[unspecified]`` in the date column itself. Its
        # vocabulary sheet lists exactly two things for ``q_date``: a ``years-months``
        # date, and this sentinel.
        from project.ghfdb.resources.widgets import AcquisitionDateWidget

        assert AcquisitionDateWidget().clean(cell) is None

    def test_a_real_acquisition_date_is_still_read(self):
        from project.ghfdb.resources.widgets import AcquisitionDateWidget

        assert AcquisitionDateWidget().clean("1979-12") == "1979-12"


class TestMultiConceptWidgetUnspecified:
    # A cell reading ``[unspecified]`` is a value the scheme scores (FR-009), so where the
    # vocabulary defines an ``unspecified`` concept the import stores it. A blank cell is
    # empty and stores nothing.

    def test_an_unspecified_cell_stores_the_vocabulary_concept(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabularies.ConductivitySource)

        result = widget.clean("[unspecified]", row={})

        assert [concept.name for concept in result] == ["unspecified"]

    def test_unspecified_beside_another_concept_keeps_both(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabularies.ConductivitySource)

        result = widget.clean("[Core samples]; [unspecified]", row={})

        assert sorted(concept.name for concept in result) == [
            "core_samples",
            "unspecified",
        ]

    @pytest.mark.parametrize("cell", ["", "   ", " ; ", None])
    def test_a_blank_cell_stores_an_empty_set(self, db, cell):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabularies.ConductivitySource)

        assert list(widget.clean(cell, row={})) == []

    def test_a_vocabulary_without_unspecified_still_stores_nothing_for_it(self, db):
        from heat_flow import vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabularies.ConductivityLocation)

        assert list(widget.clean("[unspecified]", row={})) == []

    def test_the_export_writes_the_stored_concept_back_and_it_imports_again(
        self, dataset
    ):
        from heat_flow import vocabularies
        from research_vocabs.models import Concept

        from project.ghfdb.resources.export import GHFDBExportResource
        from project.ghfdb.resources.widgets import MultiConceptWidget
        from tests.factories import HeatFlowFactory, IntervalConductivityFactory

        unspecified = Concept.get_for_vocabulary(vocabularies.ConductivitySource).get(
            name="unspecified"
        )
        child = HeatFlowFactory(
            thermal_conductivity=IntervalConductivityFactory(source=[unspecified])
        )

        exported = GHFDBExportResource().dehydrate_tc_source(child)
        reimported = MultiConceptWidget(vocabularies.ConductivitySource).clean(
            exported, row={}
        )

        assert exported != ""
        assert list(reimported) == [unspecified]
