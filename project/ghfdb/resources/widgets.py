"""
Custom import/export widgets for the GHFDB product layer.

Widget hierarchy:
    import_export.widgets.Widget
    +----- ConceptWidget          -- Single research_vocabs Concept (case-insensitive label lookup)
    +----- MultiConceptWidget     -- Semicolon-separated Concepts
    +----- QuantityWidget         -- Pint Quantity <-> plain numeric magnitude
    +----- YesNoWidget            -- "Yes"/"No" <-> Boolean
    +----- RelatedModelWidget     -- Creates/updates a related model from multiple row columns
               +----- ParentWidget       -- Creates HeatFlowSite + Point from parent columns
               +----- IntervalWidget     -- Creates HeatFlowInterval from depth columns
               +----- GradientWidget     -- Creates ThermalGradient from gradient columns
               +----- ConductivityWidget -- Creates IntervalConductivity from conductivity columns

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from import_export.widgets import BooleanWidget, CharWidget, ManyToManyWidget, Widget
from research_vocabs.models import Concept

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _case_insensitive_qs(vocabulary, field="label"):
    """Return a QuerySet of Concepts with an ilabel annotation (lowercase)."""
    return Concept.get_for_vocabulary(vocabulary).annotate(ilabel=Lower(field))


def _validate_concept(values, vocabulary):
    """Raise ValueError if any value is not in the vocabulary's labels (case-insensitive)."""
    choices = _case_insensitive_qs(vocabulary, field="label").values_list(
        "ilabel", flat=True
    )
    invalid = [v for v in values if v not in choices]
    if invalid:
        raise ValueError(
            _(
                "The following values are not part of the %(vocab)s vocabulary: %(invalid)s"
            )
            % {"vocab": vocabulary.__name__, "invalid": invalid}
        )


def normalize_vocab_token(raw: str) -> str:
    """Strip surrounding square brackets and lowercase a vocabulary token (FR-016).

    GHFDB upload templates wrap vocabulary cell values in square brackets,
    e.g. '[Onshore (continental)]'. This helper normalises such tokens so they
    match the lowercase vocabulary definitions stored in the database.
    The caller should preserve the original raw value for error messages.

    Whitespace is stripped on both sides of the brackets, not just inside
    them. Real submissions carry cells like ``' [unspecified]'`` — a leading
    space defeats a bare ``strip("[]")``, because the first character is not
    a bracket and stripping stops there.
    """
    return raw.strip().strip("[]").strip().lower()


#: Cell values the assessment corpus uses to mean "nothing entered here
#: yet", beyond an empty or whitespace-only cell — a bare hyphen in a
#: reference column filled in later, such as ``Ref_IGSN``.
BLANK_CELL_MARKERS = {"-"}


def is_blank_cell(raw) -> bool:
    """Whether *raw* means no value was given for a reference-style column.

    True for ``None``, an empty or whitespace-only string, and any of
    ``BLANK_CELL_MARKERS``.
    """
    if raw is None:
        return True
    text = str(raw).strip()
    return not text or text in BLANK_CELL_MARKERS


# ---------------------------------------------------------------------------
# Leaf Widgets
# ---------------------------------------------------------------------------


class ConceptWidget(CharWidget):
    """Maps a human-readable concept label (or key) to its vocabulary key."""

    def __init__(self, vocabulary, **kwargs):
        self.vocabulary = vocabulary
        # vocabulary may be a class or instance; instantiate to access choices
        vocab_instance = vocabulary() if isinstance(vocabulary, type) else vocabulary
        self.choices = vocab_instance.choices
        # Label -> key (case-insensitive): "onshore (continental)" -> "onshore_continental"
        self.label_to_key = {label.lower(): key for key, label in self.choices}
        # Key -> key (pass-through): "onshore_continental" -> "onshore_continental"
        self.key_to_key = {key.lower(): key for key, _ in self.choices}
        super().__init__(**kwargs)

    def clean(self, value, row=None, column=None, **kwargs):
        try:
            val = super().clean(value, row, **kwargs)
        except AttributeError:
            raise ValueError(
                _(
                    "Column value %(val)r is not a text string; expected a vocabulary label for %(vocab)s."
                )
                % {"val": value, "vocab": self.vocabulary.__name__}
            ) from None
        if not val or normalize_vocab_token(val) == "unspecified":
            return None
        normalised = normalize_vocab_token(val)
        result = self.label_to_key.get(normalised) or self.key_to_key.get(normalised)
        if result is None:
            location = _("Column '%(column)s': ") % {"column": column} if column else ""
            raise ValueError(
                location
                + _(
                    "Invalid value '%(val)s' for %(vocab)s vocabulary. Valid options are: %(opts)s"
                )
                % {
                    "val": val,
                    "vocab": self.vocabulary.__name__,
                    "opts": sorted(self.label_to_key.keys()),
                }
            )
        return result


class MultiConceptWidget(ManyToManyWidget):
    """Maps semicolon-separated concept labels to a research_vocabs Concept QuerySet."""

    def __init__(self, vocabulary, separator=";", **kwargs):
        self._vocab_class = (
            vocabulary if isinstance(vocabulary, type) else type(vocabulary)
        )
        super().__init__(Concept, separator=separator, field="label", **kwargs)
        self.queryset = Concept.get_for_vocabulary(self._vocab_class)

    def clean(self, value, row=None, column=None, *args, **kwargs):
        if not value:
            return self.queryset.none()
        # Build (original, normalised) pairs; skip blank and "unspecified" tokens
        pairs = []
        for v in str(value).split(self.separator):
            raw = v.strip()
            if not raw:
                continue
            norm = normalize_vocab_token(raw)
            if norm != "unspecified":
                pairs.append((raw, norm))
        if not pairs:
            return self.queryset.none()
        # A cell names a concept by its label or by its key, and the upload
        # template uses both: the lithology and stratigraphic-age columns
        # offer keys ('alkali_feldspar_granite', 'CambrianSeries2') while
        # every other vocabulary column offers labels. ``ConceptWidget``
        # already reads either; matching on the label alone here made 174 of
        # the 265 lithologies and 29 of the 181 ages the template offers
        # unreachable, so a file using them was refused on values its own
        # template supplied.
        concepts = list(self.queryset)
        by_label = {concept.label.lower(): concept.pk for concept in concepts}
        by_key = {concept.name.lower(): concept.pk for concept in concepts}

        matched, invalid_originals = [], []
        for orig, norm in pairs:
            pk = by_label.get(norm, by_key.get(norm))
            if pk is None:
                invalid_originals.append(orig)
            else:
                matched.append(pk)

        if invalid_originals:
            location = _("Column '%(column)s': ") % {"column": column} if column else ""
            raise ValueError(
                location
                + _(
                    "The following values are not part of the %(vocab)s vocabulary: %(invalid)s"
                )
                % {"vocab": self._vocab_class.__name__, "invalid": invalid_originals}
            )
        return self.queryset.filter(pk__in=matched)


class AcquisitionDateWidget(CharWidget):
    """Reads the template's date-of-acquisition cell.

    The template's own vocabulary sheet offers two things in this column: a
    ``years-months`` date, and ``[unspecified]``. The sentinel is the same
    one every vocabulary column carries, so it means the same thing here —
    no date was given — and is read as an empty cell rather than being put
    to the date field, which refuses it.
    """

    def clean(self, value, row=None, **kwargs):
        if value is None:
            return None
        if isinstance(value, str) and normalize_vocab_token(value) == "unspecified":
            return None
        return super().clean(value, row=row, **kwargs)


class YesNoWidget(BooleanWidget):
    """Maps "Yes"/"No" strings to boolean values."""

    TRUE_VALUES = [
        "1",
        1,
        True,
        "true",
        "TRUE",
        "True",
        "Yes",
        "yes",
        "YES",
        "[Yes]",
        "[yes]",
    ]
    FALSE_VALUES = [
        "0",
        0,
        False,
        "false",
        "FALSE",
        "False",
        "No",
        "no",
        "NO",
        "[No]",
        "[no]",
    ]


class QuantityWidget(Widget):
    """Converts a plain numeric magnitude to/from a Pint Quantity."""

    def __init__(self, unit):
        self.unit = unit

    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() == "":
            return None
        from quantityfield.units import ureg

        try:
            return ureg.Quantity(float(value), self.unit)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                _("Invalid quantity value '%(value)s': %(err)s")
                % {"value": value, "err": str(exc)}
            ) from exc

    def render(self, value, obj=None):
        if value is None:
            return ""
        return str(float(value.magnitude))


# ---------------------------------------------------------------------------
# RelatedModelWidget and subclasses
# ---------------------------------------------------------------------------


class RelatedModelWidget(Widget):
    """
    Base widget that creates an unsaved related model instance from multiple row columns.

    Scalar fields are extracted from the row using the declared widget_map and stored
    into the model instance.  M2M fields are deferred: call set_m2m_relations(instance)
    after the instance has been saved to apply them.

    The returned instance is *unsaved*; the resource is responsible for assigning any
    required FK fields (e.g. dataset, sample) and calling save().
    """

    def __init__(
        self,
        model,
        scalar_map=None,
        m2m_map=None,
        sentinel_column=None,
        widget_map=None,
    ):
        self.model = model
        # {model_field: row_col} - scalar columns
        self.scalar_map = scalar_map or {}
        # {model_field: (row_col, widget)} - M2M columns, applied after save
        self.m2m_map = m2m_map or {}
        self.sentinel_column = sentinel_column
        # {row_col: widget} - per-column widget overrides
        self.widget_map = widget_map or {}
        self._last_row = None

    def clean(self, value, row=None, **kwargs):
        self._last_row = row
        if self.sentinel_column is not None:
            raw_sentinel = (row or {}).get(self.sentinel_column)
            # Numeric values (int/float) are valid for quantity-type sentinel columns
            # (e.g. T_grad_mean, tc_mean) — treat as present and proceed.
            if isinstance(raw_sentinel, int | float):
                pass  # numeric sentinel → sub-record should be created
            else:
                try:
                    sentinel_val = (raw_sentinel or "").strip()
                except AttributeError:
                    raise ValueError(
                        _(
                            "Column '%(col)s' contains a non-text value %(val)r; expected a text string."
                        )
                        % {"col": self.sentinel_column, "val": raw_sentinel}
                    ) from None
                if not sentinel_val:
                    return None

        model_kwargs = {}
        for model_field, row_col in self.scalar_map.items():
            raw = (row or {}).get(row_col, "") or ""
            col_widget = self.widget_map.get(row_col)
            if col_widget:
                try:
                    model_kwargs[model_field] = col_widget.clean(
                        raw, row=row, column=row_col
                    )
                except (ValueError, ValidationError) as exc:
                    raise ValueError(
                        _("%(model)s: %(err)s")
                        % {"model": self.model.__name__, "err": str(exc)}
                    ) from exc
            else:
                model_kwargs[model_field] = raw or None

        return self.model(**model_kwargs)  # UNSAVED

    def set_m2m_relations(self, instance):
        """Set M2M relationships on an already-saved instance using the last cleaned row.

        Runs after the row is saved, inside the resource's row-processing
        call frame (``save_instance`` calls ``before_save_instance``, then
        ``after_save_instance``, which is where every caller of this method
        invokes it) — a raised error here still reaches ``import_row``'s own
        exception handling the same way a ``before_save_instance`` error
        does (D17, ``specs/004-import-upload-template/decisions.md``), so it
        refuses the file the same as any other located fault rather than
        being lost after the instance is already saved.
        """
        if instance is None or instance.pk is None or self._last_row is None:
            return
        for model_field, (row_col, m2m_widget) in self.m2m_map.items():
            raw = self._last_row.get(row_col, "")
            if raw:
                try:
                    qs = m2m_widget.clean(raw, row=self._last_row, column=row_col)
                except (ValueError, ValidationError) as exc:
                    raise ValueError(
                        _("%(model)s: %(err)s")
                        % {"model": self.model.__name__, "err": str(exc)}
                    ) from exc
                if qs is not None:
                    getattr(instance, model_field).set(qs)


class ParentWidget(RelatedModelWidget):
    """
    Creates an unsaved HeatFlowSite from parent-level GHFDB columns.

    Also attaches an unsaved Point (x=long_EW, y=lat_NS) to the site's
    location attribute.  The resource is responsible for saving both the
    Point and the site (after assigning a dataset FK).
    """

    def __init__(self):
        from heat_flow import vocabularies
        from heat_flow.models import HeatFlowSite

        super().__init__(
            model=HeatFlowSite,
            sentinel_column="name",
            scalar_map={
                "name": "name",
                "environment": "environment",
                "explo_method": "explo_method",
                "elevation": "elevation",
                "length": "total_depth_MD",
                "vertical_depth": "total_depth_TVD",
                "country": "Country",
                "region": "Region",
                "continent": "Continent",
                "domain": "Domain",
            },
            m2m_map={
                "explo_purpose": (
                    "explo_purpose",
                    MultiConceptWidget(vocabularies.ExplorationPurpose),
                ),
            },
            widget_map={
                "environment": ConceptWidget(
                    vocabulary=vocabularies.GeographicEnvironment
                ),
                "explo_method": ConceptWidget(
                    vocabulary=vocabularies.ExplorationMethod
                ),
                "elevation": QuantityWidget("m"),
                "total_depth_MD": QuantityWidget("m"),
                "total_depth_TVD": QuantityWidget("m"),
            },
        )

    def clean(self, value, row=None, **kwargs):
        # A site name is a label, not a number, but a spreadsheet does not
        # know that: a submission whose sites are numbered 1, 2, 3 arrives
        # with integer cells, and refusing those refused 2,338 rows of the
        # assessment team's own files. Read whatever the cell holds as text.
        raw_name = (row or {}).get("name")
        if raw_name is not None and not isinstance(raw_name, str):
            row = dict(row)
            raw_name = row["name"] = str(raw_name)

        self._last_row = row
        if not (raw_name or "").strip():
            return None

        from fairdm.contrib.location.models import Point

        # A site is its coordinates (ADR 0006), so a named row with no
        # coordinate pair has nowhere to be placed and is a fault reported
        # against the row. Defaulting a blank cell to zero would file the
        # site in the Gulf of Guinea instead.
        raw_lat = (row or {}).get("lat_NS")
        raw_lng = (row or {}).get("long_EW")
        missing = [
            column
            for column, raw in (("lat_NS", raw_lat), ("long_EW", raw_lng))
            if not str(raw if raw is not None else "").strip()
        ]
        if missing:
            raise ValueError(
                _(
                    "Row names a site but leaves %(columns)s empty; a site cannot be "
                    "placed without both a latitude and a longitude."
                )
                % {"columns": " and ".join(f"'{column}'" for column in missing)}
            )

        lat = float(raw_lat)
        lng = float(raw_lng)

        instance = super().clean(value, row=row, **kwargs)
        if instance is not None:
            instance.location = Point(x=lng, y=lat)
        return instance  # UNSAVED (Point also unsaved)


class IntervalWidget(RelatedModelWidget):
    """
    Creates an unsaved HeatFlowInterval from depth columns.

    sentinel_column=None means the interval is always created (every child row
    should have interval data).
    """

    def __init__(self):
        from fairdm_geo.vocabularies.cgi.geosciml import SimpleLithology
        from fairdm_geo.vocabularies.stratigraphy import GeologicalTimescale
        from heat_flow.models import HeatFlowInterval

        super().__init__(
            model=HeatFlowInterval,
            sentinel_column=None,
            scalar_map={
                "top": "q_top",
                "bottom": "q_bottom",
            },
            m2m_map={
                "lithology": (
                    "geo_lithology",
                    MultiConceptWidget(SimpleLithology),
                ),
                "age": (
                    "geo_stratigraphy",
                    MultiConceptWidget(GeologicalTimescale),
                ),
            },
            widget_map={
                "q_top": QuantityWidget("m"),
                "q_bottom": QuantityWidget("m"),
            },
        )


class GradientWidget(RelatedModelWidget):
    """
    Creates an unsaved ThermalGradient from T_grad_* columns.

    Skipped (returns None) when T_grad_mean is empty (sentinel column).
    """

    def __init__(self):
        from heat_flow import vocabularies
        from heat_flow.models import ThermalGradient

        super().__init__(
            model=ThermalGradient,
            sentinel_column="T_grad_mean",
            scalar_map={
                "value": "T_grad_mean",
                "uncertainty": "T_grad_uncertainty",
                "corrected_value": "T_grad_mean_cor",
                "corrected_uncertainty": "T_grad_uncertainty_cor",
                "shutin_top": "T_shutin_top",
                "shutin_bottom": "T_shutin_bottom",
                "number": "T_number",
                "temperature_top": "T_top_mean",
                "temperature_top_uncertainty": "T_top_uncertainty",
                "temperature_bottom": "T_bot_mean",
                "temperature_bottom_uncertainty": "T_bot_uncertainty",
            },
            m2m_map={
                "method_top": (
                    "T_method_top",
                    MultiConceptWidget(vocabularies.TemperatureMethod),
                ),
                "method_bottom": (
                    "T_method_bottom",
                    MultiConceptWidget(vocabularies.TemperatureMethod),
                ),
                "correction_top": (
                    "T_corr_top",
                    MultiConceptWidget(vocabularies.TemperatureCorrection),
                ),
                "correction_bottom": (
                    "T_corr_bottom",
                    MultiConceptWidget(vocabularies.TemperatureCorrection),
                ),
            },
            widget_map={
                "T_grad_mean": QuantityWidget("K/km"),
                "T_grad_uncertainty": QuantityWidget("K/km"),
                "T_grad_mean_cor": QuantityWidget("K/km"),
                "T_grad_uncertainty_cor": QuantityWidget("K/km"),
                "T_shutin_top": QuantityWidget("hr"),
                "T_shutin_bottom": QuantityWidget("hr"),
                "T_top_mean": QuantityWidget("°C"),
                "T_top_uncertainty": QuantityWidget("°C"),
                "T_bot_mean": QuantityWidget("°C"),
                "T_bot_uncertainty": QuantityWidget("°C"),
            },
        )


class ConductivityWidget(RelatedModelWidget):
    """
    Creates an unsaved IntervalConductivity from tc_* columns.

    Skipped (returns None) when tc_mean is empty (sentinel column).
    """

    def __init__(self):
        from heat_flow import vocabularies
        from heat_flow.models import IntervalConductivity

        super().__init__(
            model=IntervalConductivity,
            sentinel_column="tc_mean",
            scalar_map={
                "value": "tc_mean",
                "uncertainty": "tc_uncertainty",
                "number": "tc_number",
            },
            m2m_map={
                "source": (
                    "tc_source",
                    MultiConceptWidget(vocabularies.ConductivitySource),
                ),
                "location": (
                    "tc_location",
                    MultiConceptWidget(vocabularies.ConductivityLocation),
                ),
                "method": (
                    "tc_method",
                    MultiConceptWidget(vocabularies.ConductivityMethod),
                ),
                "saturation": (
                    "tc_saturation",
                    MultiConceptWidget(vocabularies.ConductivitySaturation),
                ),
                "pT_conditions": (
                    "tc_pT_conditions",
                    MultiConceptWidget(vocabularies.ConductivityPTConditions),
                ),
                "pT_function": (
                    "tc_pT_function",
                    MultiConceptWidget(vocabularies.ConductivityPTFunction),
                ),
                "strategy": (
                    "tc_strategy",
                    MultiConceptWidget(vocabularies.ConductivityStrategy),
                ),
            },
            widget_map={
                "tc_mean": QuantityWidget("W/mK"),
                "tc_uncertainty": QuantityWidget("W/mK"),
            },
        )
