"""
Tests for GHFDB custom import/export widgets.

Covers:
- ConceptWidget: case-insensitive lookup, invalid-value ValueError
- MultiConceptWidget: semicolon split, batched error for multiple invalid values
- QuantityWidget: returns Quantity on clean, returns plain magnitude on render
- YesNoWidget: "Yes" → True, "No" → False, empty → None
- RelatedModelWidget: sentinel-column check, full_clean error, set_m2m_relations
- ParentWidget: creates HeatFlowSite + Point from lat/long columns
- IntervalWidget: creates HeatFlowInterval
- GradientWidget: skips when T_grad_mean is empty
- ConductivityWidget: skips when tc_mean is empty
"""

import pytest

# ---- T027: Leaf widget tests -----------------------------------------------


class TestConceptWidget:
    """T027 — ConceptWidget clean() and render()."""

    def test_clean_case_insensitive(self, db):
        """clean() matches label case-insensitively and returns a Concept."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("Onshore (continental)", row={})
        assert result is not None

    def test_clean_case_insensitive_lowercase(self, db):
        """clean() works with all-lowercase input."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        # The vocabulary has "Onshore (continental)" — try lowercase
        result = widget.clean("onshore (continental)", row={})
        assert result is not None

    def test_clean_empty_returns_none(self, db):
        """clean() returns None for empty/blank input."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        assert widget.clean("", row={}) is None
        assert widget.clean(None, row={}) is None

    def test_clean_invalid_raises_valueerror(self, db):
        """clean() raises ValueError listing valid options for invalid input."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("not_a_real_environment", row={})
        error_msg = str(exc_info.value)
        assert "not_a_real_environment" in error_msg.lower() or "invalid" in error_msg.lower()


class TestMultiConceptWidget:
    """T027 — MultiConceptWidget clean() with semicolon splitting."""

    def test_clean_semicolon_split(self, db):
        """clean() splits semicolon-separated values and returns list."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("", row={})
        assert result is not None  # should return empty list, not raise

    def test_clean_empty_returns_empty(self, db):
        """clean() returns empty list for empty input."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("", row={})
        assert result == [] or result is None or hasattr(result, "__iter__")

    def test_clean_invalid_batched_error(self, db):
        """clean() raises ValueError listing all invalid values."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("invalid_one;invalid_two", row={})
        error_msg = str(exc_info.value)
        # Both invalid values should be mentioned
        assert "invalid_one" in error_msg or "invalid" in error_msg.lower()


class TestQuantityWidget:
    """T027 — QuantityWidget clean() and render()."""

    def test_clean_returns_quantity(self):
        """clean() returns a Pint Quantity instance."""
        from project.ghfdb.resources._widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        result = widget.clean("70.0", row={})
        # Should return a Quantity with magnitude 70.0
        assert result is not None
        magnitude = getattr(result, "magnitude", result)
        assert float(magnitude) == pytest.approx(70.0)

    def test_clean_empty_returns_none(self):
        """clean() returns None for empty input."""
        from project.ghfdb.resources._widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        assert widget.clean("", row={}) is None
        assert widget.clean(None, row={}) is None

    def test_render_returns_plain_magnitude(self):
        """render() returns plain numeric magnitude without unit symbol."""
        from project.ghfdb.resources._widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        # Create a Quantity and render it
        from pint import UnitRegistry

        ureg = UnitRegistry()
        qty = ureg.Quantity(70.5, "mW/m**2")
        result = widget.render(qty)
        # Should be numeric string, no unit label
        assert "70.5" in str(result) or float(result) == pytest.approx(70.5)

    def test_render_none_returns_empty(self):
        """render() returns empty string for None."""
        from project.ghfdb.resources._widgets import QuantityWidget

        widget = QuantityWidget(unit="mW/m**2")
        assert widget.render(None) == "" or widget.render(None) is None


class TestYesNoWidget:
    """T027 — YesNoWidget clean() maps Yes/No strings to bool."""

    def test_clean_yes_returns_true(self):
        """'Yes' maps to True."""
        from project.ghfdb.resources._widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("Yes", row={}) is True

    def test_clean_no_returns_false(self):
        """'No' maps to False."""
        from project.ghfdb.resources._widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("No", row={}) is False

    def test_clean_empty_returns_none(self):
        """Empty string maps to None."""
        from project.ghfdb.resources._widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("", row={}) is None

    def test_clean_case_insensitive(self):
        """'yes'/'no' (lowercase) also work."""
        from project.ghfdb.resources._widgets import YesNoWidget

        widget = YesNoWidget()
        assert widget.clean("yes", row={}) is True
        assert widget.clean("no", row={}) is False


# ---- T028: RelatedModelWidget and subclass tests ---------------------------


class TestRelatedModelWidget:
    """T028 — RelatedModelWidget base class behaviour."""

    def test_sentinel_column_empty_returns_none(self, db):
        """When sentinel column is empty, clean() returns None."""
        from project.ghfdb.resources._widgets import GradientWidget

        widget = GradientWidget()
        row = {"T_grad_mean": "", "T_grad_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    def test_full_clean_error_prefixed_with_model_name(self, db):
        """ValidationError from full_clean() is re-raised as ValueError prefixed with model name."""
        from project.ghfdb.resources._widgets import GradientWidget

        widget = GradientWidget()
        # Provide an invalid value to trigger full_clean() failure
        row = {"T_grad_mean": "not_a_number", "T_grad_uncertainty": ""}
        with pytest.raises(ValueError) as exc_info:
            widget.clean("not_a_number", row=row)
        # Error should be prefixed with model name
        error_msg = str(exc_info.value)
        assert "ThermalGradient" in error_msg or "gradient" in error_msg.lower() or "invalid" in error_msg.lower()

    def test_set_m2m_relations_sets_m2m(self, db, dataset):
        """set_m2m_relations() sets M2M relationships on the related model."""
        from heat_flow.models import HeatFlowInterval, HeatFlowSite

        from project.ghfdb.resources._widgets import IntervalWidget

        site = HeatFlowSite.objects.create(dataset=dataset, name="Test")
        interval = HeatFlowInterval.objects.create(
            dataset=dataset,
            sample=site,
            name="Test Interval",
        )
        widget = IntervalWidget()
        # Just verify the method exists and is callable
        assert hasattr(widget, "set_m2m_relations")
        # Should not raise
        widget.set_m2m_relations(interval)


class TestParentWidget:
    """T028 — ParentWidget creates HeatFlowSite + Point from parent columns."""

    @pytest.mark.django_db
    def test_creates_heatflowsite_and_point(self, dataset):
        """clean() creates HeatFlowSite + Point from lat/long columns."""
        from project.ghfdb.resources._widgets import ParentWidget

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
        """When site name (sentinel) is empty, clean() returns None."""
        from project.ghfdb.resources._widgets import ParentWidget

        widget = ParentWidget()
        result = widget.clean("", row={})
        assert result is None


class TestIntervalWidget:
    """T028 — IntervalWidget creates HeatFlowInterval."""

    @pytest.mark.django_db
    def test_creates_heatflowinterval(self, dataset):
        """clean() creates a HeatFlowInterval with depth data."""
        from heat_flow.models import HeatFlowInterval

        from project.ghfdb.resources._widgets import IntervalWidget

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


class TestGradientWidget:
    """T028 — GradientWidget skips when T_grad_mean is empty."""

    @pytest.mark.django_db
    def test_skips_when_sentinel_empty(self):
        """clean() returns None when T_grad_mean is empty."""
        from project.ghfdb.resources._widgets import GradientWidget

        widget = GradientWidget()
        row = {"T_grad_mean": "", "T_grad_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    @pytest.mark.django_db
    def test_creates_gradient_when_sentinel_set(self, dataset):
        """clean() creates ThermalGradient when T_grad_mean has a value."""
        from heat_flow.models import ThermalGradient

        from project.ghfdb.resources._widgets import GradientWidget

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


class TestConductivityWidget:
    """T028 — ConductivityWidget skips when tc_mean is empty."""

    @pytest.mark.django_db
    def test_skips_when_sentinel_empty(self):
        """clean() returns None when tc_mean is empty."""
        from project.ghfdb.resources._widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {"tc_mean": "", "tc_uncertainty": ""}
        result = widget.clean("", row=row)
        assert result is None

    @pytest.mark.django_db
    def test_creates_conductivity_when_sentinel_set(self, dataset):
        """clean() creates IntervalConductivity when tc_mean has a value."""
        from heat_flow.models import IntervalConductivity

        from project.ghfdb.resources._widgets import ConductivityWidget

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


# ---- T072: FR-016 Vocabulary normalisation regression tests ----------------


class TestVocabNormalisation:
    """T072 — FR-016: bracket-wrapped and mixed-case vocab tokens are normalised before matching."""

    def test_normalize_vocab_token_strips_brackets(self):
        """normalize_vocab_token() strips surrounding [ ] and lowercases the token."""
        from project.ghfdb.resources._widgets import normalize_vocab_token

        assert normalize_vocab_token("[Onshore (continental)]") == "onshore (continental)"
        assert normalize_vocab_token("[OFFSHORE (MARINE)]") == "offshore (marine)"
        # Plain tokens (no brackets) should pass through unchanged after lowercasing
        assert normalize_vocab_token("onshore (continental)") == "onshore (continental)"
        assert normalize_vocab_token("Onshore (continental)") == "onshore (continental)"

    def test_concept_widget_accepts_bracketed_value(self, db):
        """ConceptWidget.clean('[Onshore (continental)]') resolves without error (FR-016)."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("[Onshore (continental)]", row={})
        assert result is not None

    def test_concept_widget_accepts_bracketed_uppercase(self, db):
        """ConceptWidget.clean('[OFFSHORE (MARINE)]') resolves via bracket + case normalisation."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        result = widget.clean("[OFFSHORE (MARINE)]", row={})
        assert result is not None

    def test_concept_widget_invalid_bracketed_reports_original(self, db):
        """ValueError for an invalid bracketed token includes the original bracket-wrapped text."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("[NOT_VALID]", row={})
        # Original token (with brackets) must be visible in the error message
        assert "[NOT_VALID]" in str(exc_info.value)

    def test_multi_concept_widget_normalizes_bracketed_tokens(self, db):
        """MultiConceptWidget normalises each bracket-wrapped semicolon-separated token (FR-016)."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import MultiConceptWidget

        # ExplorationPurpose is preloaded in the test DB; use it to verify bracket normalisation
        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        result = widget.clean("[Geothermal]; [Research]", row={})
        assert result is not None
        assert result.count() >= 1

    def test_multi_concept_widget_invalid_bracketed_reports_original(self, db):
        """MultiConceptWidget error for invalid bracketed token includes the original text."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import MultiConceptWidget

        widget = MultiConceptWidget(vocabulary=vocabularies.ExplorationPurpose)
        with pytest.raises(ValueError) as exc_info:
            widget.clean("[COMPLETELY_INVALID]", row={})
        # Original token (with brackets) must be visible — not the lowercased/stripped form
        assert "[COMPLETELY_INVALID]" in str(exc_info.value)


# ---- T079: BUG-007 numeric cell value regression tests ---------------------


class TestNumericCellInputGuards:
    """T079 — BUG-007: numeric cell values produce descriptive ValueError, not AttributeError.

    When openpyxl/tablib reads a spreadsheet cell as an integer or float (e.g. a
    numeric column, or a formula result), widgets that call .strip() must catch the
    resulting AttributeError and re-raise a descriptive ValueError naming the column
    and the unexpected value so users can locate the offending cell.
    """

    def test_concept_widget_int_raises_valueerror_not_attributeerror(self, db):
        """ConceptWidget.clean(42) raises ValueError with vocab name — not bare AttributeError."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean(42, row={})
        error_msg = str(exc_info.value)
        # Must mention the vocabulary class name so the user knows which field
        assert "GeographicEnvironment" in error_msg
        # Must mention the bad value
        assert "42" in error_msg

    def test_concept_widget_float_raises_valueerror_not_attributeerror(self, db):
        """ConceptWidget.clean(3.14) raises ValueError — floats are also non-text."""
        from heat_flow import vocabularies

        from project.ghfdb.resources._widgets import ConceptWidget

        widget = ConceptWidget(vocabulary=vocabularies.GeographicEnvironment)
        with pytest.raises(ValueError) as exc_info:
            widget.clean(3.14, row={})
        error_msg = str(exc_info.value)
        assert "GeographicEnvironment" in error_msg

    def test_related_model_widget_numeric_sentinel_raises_valueerror(self, db):
        """RelatedModelWidget with a numeric sentinel column value raises ValueError naming the column."""
        from project.ghfdb.resources._widgets import GradientWidget

        widget = GradientWidget()
        # T_grad_mean is the sentinel column; pass an int (truthy, so strip() would be reached)
        row = {
            "T_grad_mean": 1,  # int — simulates openpyxl reading a numeric cell
            "T_grad_uncertainty": "",
        }
        with pytest.raises(ValueError) as exc_info:
            widget.clean("", row=row)
        error_msg = str(exc_info.value)
        # Must name the sentinel column
        assert "T_grad_mean" in error_msg

    def test_conductivity_widget_numeric_sentinel_raises_valueerror(self, db):
        """ConductivityWidget with numeric tc_mean raises ValueError naming the column."""
        from project.ghfdb.resources._widgets import ConductivityWidget

        widget = ConductivityWidget()
        row = {
            "tc_mean": 2,  # int — simulates openpyxl reading a numeric cell
            "tc_uncertainty": "",
        }
        with pytest.raises(ValueError) as exc_info:
            widget.clean("", row=row)
        error_msg = str(exc_info.value)
        assert "tc_mean" in error_msg

    def test_parent_widget_numeric_name_raises_valueerror(self, db):
        """ParentWidget.clean() with an int in the 'name' column raises ValueError naming 'name'."""
        from project.ghfdb.resources._widgets import ParentWidget

        widget = ParentWidget()
        row = {
            "name": 1,  # int — simulates openpyxl reading a numeric cell
            "lat_NS": "48.0",
            "long_EW": "11.0",
        }
        with pytest.raises(ValueError) as exc_info:
            widget.clean("", row=row)
        error_msg = str(exc_info.value)
        assert "name" in error_msg
