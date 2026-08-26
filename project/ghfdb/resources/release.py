"""
GHFDB release import resource and reading format (specs/003-ghfdb-release-import).

``GHFDBReleaseCSVFormat`` reads the comma-separated format a published
release is distributed in. ``GHFDBReleaseImportResource`` validates a
file's header against the release column definitions in ``constants.py``
before any row is read (FR-003 to FR-007), reports every refused value by
the column name a curator sees in the header and the line it occupies in
the file (FR-009, FR-010), and turns each row into the records the portal
keeps: the dataset its publication reference resolves to, the site, the
site's parent heat flow value, the interval, and the determination with
the gradient, conductivity and corrections derived over it.

Nothing is written unless the whole file passes (docs/adr/0012). Reading
the same file again finds every record by its published identifier and
updates it in place rather than building a second one (docs/adr/0010).

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

import csv
from io import StringIO

import tablib
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower, Trim
from django.utils.encoding import force_str
from fairdm.core.models import Dataset
from heat_flow.models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from import_export import fields, widgets
from import_export.formats.base_formats import CSV
from import_export.resources import ModelResource
from literature.models import LiteratureItem

from ..constants import (
    CORRECTION_COL_MAP,
    MISSPELLED_COLUMNS,
    READ_COLUMNS,
    RELEASE_COLUMNS,
)
from .widgets import (
    ConductivityWidget,
    GradientWidget,
    IntervalWidget,
    MultiConceptWidget,
    ParentWidget,
    QuantityWidget,
    YesNoWidget,
    normalize_vocab_token,
)

# FR-006: a column the release format requires. DISCARDED_COLUMNS is
# deliberately excluded - two of its members (the legacy per-row quality
# codes) are never present in a real release (R1), so their absence cannot
# be a fault, and the rest are recognised only if a file happens to carry
# them (D13).
REQUIRED_COLUMNS = READ_COLUMNS


ABSENT_VALUE_MARKER = "[Unspecified]"


def _blank_absent_values(row):
    """The row every field and builder reads, with the published
    absent-value marker (R1: ``[Unspecified]``, the only non-numeric
    value a numeric column holds) read as no value in every column
    (FR-012, T076, T077) - not refused as a fault, and not left for a
    quantity widget to crash outright on. Replaces the narrower,
    builder-scoped workaround T052/T053 left in place pending this
    task, which covered only the columns this story's own row-to-record
    builders touched.
    """
    return {
        key: "" if value == ABSENT_VALUE_MARKER else value for key, value in row.items()
    }


def _normalize_publication_reference(reference: str) -> str:
    """FR-017: two publication references are the same reference once
    surrounding whitespace and case are ignored."""
    return reference.strip().lower()


def _record_publication_year(literature_item, year):
    """FR-037: persist a publication's year onto its bibliographic record,
    in the one existing field that already carries a date
    (``LiteratureItem.issued``, derived from its CSL ``item`` blob on
    save) - the only place a site's earliest-year comparison (T103-T107)
    can read a publication's year back from on a later, separate import
    pass, since ``Year`` itself is discarded rather than stored (D26).
    Never overwrites a year the record already carries from elsewhere,
    and does nothing for a row that gives no year at all."""
    if not year or literature_item.issued is not None:
        return
    try:
        year_number = int(year)
    except ValueError:
        return
    literature_item.item = {
        **literature_item.item,
        "issued": {"date-parts": [[year_number]]},
    }
    literature_item.save()


def _publication_year(dataset):
    """The year recorded for a dataset's own publication (T103-T107), or
    ``None`` where none was ever supplied - read back off the same field
    ``_record_publication_year`` writes."""
    reference = getattr(dataset, "reference", None)
    issued = getattr(reference, "issued", None) if reference is not None else None
    return issued.date.year if issued is not None else None


def _correction_status(raw: str) -> str:
    """FR-030, T068, T069: a correction flag is normalised the same way as
    any other controlled-vocabulary value - surrounding brackets stripped
    and lowercased - before being matched to its
    ``HeatFlowCorrection.StatusChoices`` term, so a bracketed or
    differently cased flag is read rather than lost."""
    from heat_flow.models import HeatFlowCorrection

    token = normalize_vocab_token(raw)
    label_to_status = {
        label.lower(): value
        for value, label in HeatFlowCorrection.StatusChoices.choices
    }
    key_to_status = {
        value.lower(): value
        for value, _label in HeatFlowCorrection.StatusChoices.choices
    }
    status = label_to_status.get(token) or key_to_status.get(token)
    if status is None:
        raise ValueError(f"'{raw}' does not match a correction status.")
    return status


def _depth_magnitude(value):
    """The comparable identity of an interval's top or bottom depth
    (T059, T060): its numeric magnitude, or ``None`` when the row gives
    no depth at all - the indeterminate interval's own identity (D17)."""
    return getattr(value, "magnitude", value)


def _find_disagreements(dataset, key_fn, columns, normalize=None):
    """Group ``dataset.dict`` by ``key_fn`` and return, for each key, the
    columns where rows sharing that key give more than one distinct
    non-blank value, together with the values seen (T072-T075, D18,
    FR-035). A column left blank by a row is not part of the
    comparison - the row makes no statement about it, the same
    principle T066/T067 applies to a blank correction column - so a
    row that is merely silent never counts as disagreeing with one that
    supplies a value.
    """
    values_by_key_column = {}
    for row in dataset.dict:
        key = key_fn(row)
        if key is None:
            continue
        for column in columns:
            raw = (row.get(column) or "").strip()
            value = normalize(column, raw) if normalize else raw
            if not value:
                continue
            values_by_key_column.setdefault((key, column), set()).add(value)

    disagreements = {}
    for (key, column), values in values_by_key_column.items():
        if len(values) > 1:
            disagreements.setdefault(key, {})[column] = sorted(values)
    return disagreements


PROBE_COLUMNS = ("probe_penetration", "probe_type", "probe_length", "probe_tilt")


def _disagreement_errors(disagreements, key, subject):
    """The refusal for each column that rows sharing ``subject`` disagree
    about (T072-T075, D18). ``subject`` reads into the message, so it is
    written as the reader sees it: ``this interval`` or ``site 'X'``."""
    return {
        column: ValidationError(
            force_str(
                f"Rows sharing {subject} disagree about '{column}': "
                f"{', '.join(values)}. The file is refused rather than "
                f"choosing between them."
            ),
            code="invalid",
        )
        for column, values in disagreements.get(key, {}).items()
    }


def _vocab_term(raw):
    """A controlled-vocabulary value reduced to the term it is compared
    under. ``Unspecified`` states nothing, so it reduces to blank and is
    indistinguishable from an empty cell."""
    normalized = normalize_vocab_token(raw)
    return "" if normalized == "unspecified" else normalized


def _probe_column_value(column, raw):
    """The comparable value of a probe column for disagreement purposes
    (T072, T073): ``probe_type`` is a vocabulary column, so it is
    normalised and treated as blank when unspecified, the same as any
    other controlled-vocabulary value. The quantity columns compare on
    their raw text."""
    if column == "probe_type":
        return _vocab_term(raw)
    return raw


def _interval_disagreement_key(row):
    """The interval identity a row's probe columns are compared under
    (T072, T073): the same ``(site, top, bottom)`` shape
    ``_build_interval`` identifies an interval by (D15), computed here
    from the row alone since the site is not resolved yet when the
    header is first scanned."""
    local_id = (row.get("ID_parent") or "").strip()
    if not local_id:
        return None
    blanked = _blank_absent_values(row)
    top = _depth_magnitude(QuantityWidget("m").clean(blanked.get("q_top")))
    bottom = _depth_magnitude(QuantityWidget("m").clean(blanked.get("q_bottom")))
    return (local_id, top, bottom)


# T074, T075: the site's own columns - the scalar fields
# ``_build_new_site`` sets from ``ParentWidget`` plus the coordinates it
# sets directly (D10, D14) - compared for disagreement between rows
# sharing a published site identifier (FR-035).
SITE_COLUMNS = (
    "name",
    "lat_NS",
    "long_EW",
    "elevation",
    "environment",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
    "Country",
    "Region",
    "Continent",
    "Domain",
)


def _site_column_value(column, raw):
    """The comparable value of a site column for disagreement purposes
    (T074, T075): ``environment`` and ``explo_method`` are vocabulary
    columns, normalised and treated as blank when unspecified, the same
    tolerance ``_probe_column_value`` already gives ``probe_type``.
    ``explo_purpose`` is the site's one many-valued column - the closure
    D24 flagged and left open - so it compares as an order-independent
    set of normalised terms rather than as text: reduced here to a
    canonical, sorted, semicolon-joined form, so two rows giving the same
    purposes in a different order are read as agreeing, and a term
    normalising to ``unspecified`` makes no statement, the same as a
    blank cell. The rest compare on their raw text."""
    if column in ("environment", "explo_method"):
        return _vocab_term(raw)
    if column == "explo_purpose":
        terms = {_vocab_term(term.strip()) for term in raw.split(";")}
        return ";".join(sorted(term for term in terms if term))
    return raw


def _site_disagreement_key(row):
    """The site identity a row's site columns are compared under (T074,
    T075): the published site identifier alone (D10), the same identity
    ``_build_site_and_parent`` already shares a site by."""
    return (row.get("ID_parent") or "").strip() or None


class GHFDBReleaseCSVFormat(CSV):
    """The format a published release is distributed in: one header row,
    one data row per determination (FR-002). The library's own
    comma-separated reader already reads the header from the first line
    and the data from the second; only the title a curator sees in the
    format list is added here.
    """

    def get_title(self) -> str:
        return "GHFDB Release Format"

    def create_dataset(self, in_stream, **kwargs):
        """Read the header from the first line and the data from the
        second (T009). Reimplemented rather than delegated to the
        library's own tablib-backed reader for two reasons: that reader
        looks up its tablib format by ``get_title()``, which the
        curator-facing title above no longer is, and it refuses a row
        that is wider than the header outright rather than reporting the
        header fault a curator can act on (FR-006) - a header missing one
        published column, with its data rows otherwise untouched, is
        exactly the shape a file missing a column takes.
        """
        if isinstance(in_stream, bytes) and self.encoding:
            in_stream = in_stream.decode(self.encoding)
        dataset = tablib.Dataset()
        for i, row in enumerate(csv.reader(StringIO(in_stream))):
            if i == 0:
                dataset.headers = row
            elif row:
                if len(row) < dataset.width:
                    row = row + [""] * (dataset.width - len(row))
                elif len(row) > dataset.width:
                    row = row[: dataset.width]
                dataset.append(row)
        return dataset


class GHFDBReleaseImportResource(ModelResource):
    """Checks a published release file against the release format before
    any row is written.

    Header validation runs in ``before_import`` and refuses the file for a
    misspelled published column name (FR-004, D7), a column the release
    format does not define (FR-005), or a required column the file does
    not carry (FR-006) - naming every offending column, not just the
    first. Emptying the dataset is what stops the row loop; raising alone
    does not, since the library catches ``before_import``'s exception and
    carries on to the row loop (R3). The library re-measures
    ``result.total_rows`` immediately afterwards for exactly this purpose.

    ``import_instance`` is overridden so a refused value is reported by
    the column name a curator sees in the header rather than the model
    attribute it would have been stored in (FR-010) - the library's own
    version keys the error by ``field.attribute``. ``import_data`` is
    overridden to correct the reported row number to count the header
    line, so the first data row reports as line 2 rather than the
    library's own line 1 (FR-010, R3).
    """

    qc = fields.Field(
        attribute="value",
        column_name="qc",
        widget=QuantityWidget("mW/m^2"),
    )
    qc_uncertainty = fields.Field(
        attribute="uncertainty",
        column_name="qc_uncertainty",
        widget=QuantityWidget("mW/m^2"),
    )
    local_id = fields.Field(
        attribute="local_id",
        column_name="ID",
        default="",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parent_widget = ParentWidget()
        self._interval_widget = IntervalWidget()
        self._gradient_widget = GradientWidget()
        self._conductivity_widget = ConductivityWidget()

    @staticmethod
    def _header_faults(headers):
        """Every reason this header is refused, in reporting order: a
        misspelled published name, a name the release format does not
        define, then a required name the file does not carry."""
        header_set = set(headers)
        faults = []

        misspelled_present = [name for name in MISSPELLED_COLUMNS if name in header_set]
        for name in misspelled_present:
            correct = MISSPELLED_COLUMNS[name]
            faults.append(
                f"Column '{name}' is the outdated, misspelled form of the "
                f"published column '{correct}'. This file follows an "
                f"outdated template; correct the header before importing."
            )

        undefined = [name for name in headers if name not in RELEASE_COLUMNS]
        for name in undefined:
            faults.append(f"Column '{name}' is not part of the release format.")

        corrected_present = {MISSPELLED_COLUMNS[name] for name in misspelled_present}
        missing = [
            name
            for name in REQUIRED_COLUMNS
            if name not in header_set and name not in corrected_present
        ]
        for name in sorted(missing):
            faults.append(
                f"The release format requires column '{name}', which this "
                f"file does not carry."
            )

        return faults

    def before_import(self, dataset, **kwargs):
        faults = self._header_faults(dataset.headers or [])
        if faults:
            del dataset[:]
            raise ValueError(" ".join(faults))

        self._datasets_by_reference, self._ambiguous_references = (
            self._resolve_publication_datasets(dataset)
        )
        # T057, T058: sites and their parent heat flow values are shared
        # across every row that carries the same published site
        # identifier, within this pass and across passes - cleared per
        # ``before_import`` call, one per resource instance (R4, R8).
        self._sites_by_local_id = {}
        self._parents_by_site_id = {}
        # T059-T062: an interval is shared by every row giving the same
        # site and depth range, within this pass - cleared per
        # ``before_import`` call.
        self._intervals_by_key = {}
        # T070, T071: probe metadata belongs to the interval, at most one
        # record per interval - cleared per ``before_import`` call, keyed
        # on the interval's own primary key once built.
        self._probe_metadata_by_interval_id = {}
        # T072, T073: rows sharing an interval but disagreeing about the
        # probe that sampled it are refused (D18) - found once, before
        # any row is read, the same shape ``_resolve_publication_datasets``
        # already sets for the ambiguous-reference check.
        self._interval_probe_disagreements = _find_disagreements(
            dataset,
            _interval_disagreement_key,
            PROBE_COLUMNS,
            normalize=_probe_column_value,
        )
        # T074, T075: rows sharing a published site identifier but
        # disagreeing about the site's own columns are refused (FR-035),
        # found once here for the same reason.
        self._site_disagreements = _find_disagreements(
            dataset,
            _site_disagreement_key,
            SITE_COLUMNS,
            normalize=_site_column_value,
        )
        # T116, T117: a published determination identifier seen once
        # already in this pass - checked against this set alone, never
        # the database, so a reimport of the same file (US-4) still
        # updates rather than being caught as a within-file repeat.
        self._local_ids_seen = set()

    def _resolve_publication_datasets(self, table):
        """T035, T036: collect the file's distinct publication references
        once, before any row is read, and create the dataset each one
        belongs to (D4) - a bibliographic record carrying the reference's
        citation key is created where none exists yet (T041, D5). A
        reference matching more than one bibliographic record is recorded
        as ambiguous rather than resolved to either one (T043, D5); no
        dataset or record is created for it here, and its rows are
        refused later, in ``import_instance``.

        Two references differing only by case or surrounding whitespace
        are one reference (FR-017, T037): grouped here by their
        normalised form, keeping the first raw spelling the file gives so
        the citation key created for it is stable rather than whichever
        variant a set happened to iterate first.
        """
        references_by_normalized = {}
        years_by_normalized = {}
        for row in table.dict:
            raw_reference = (row.get("publication_reference") or "").strip()
            if not raw_reference:
                continue
            normalized = _normalize_publication_reference(raw_reference)
            references_by_normalized.setdefault(normalized, raw_reference)
            years_by_normalized.setdefault(normalized, (row.get("Year") or "").strip())

        datasets_by_reference = {}
        ambiguous_references = {}
        for normalized, reference in references_by_normalized.items():
            matches = list(
                LiteratureItem.objects.annotate(
                    normalized_citation_key=Lower(Trim("citation_key"))
                ).filter(normalized_citation_key=normalized)
            )
            if len(matches) > 1:
                ambiguous_references[normalized] = matches
                continue
            if matches:
                literature_item = matches[0]
            else:
                literature_item = LiteratureItem.objects.create(citation_key=reference)
            _record_publication_year(
                literature_item, years_by_normalized.get(normalized)
            )
            release_dataset, _created = Dataset.all_objects.get_or_create(
                reference=literature_item,
                defaults={
                    "name": literature_item.title or literature_item.citation_key
                },
            )
            datasets_by_reference[normalized] = release_dataset
        return datasets_by_reference, ambiguous_references

    def before_import_row(self, row, **kwargs):
        """Read the published absent-value marker as no value, in every
        column, before anything else reads the row (FR-012, T076,
        T077) - both the declared field widgets ``import_instance``
        parses below and the builders ``before_save_instance`` runs
        later see the same blanked row, since this mutates ``row`` in
        place rather than returning a copy only some callers used.
        """
        row.update(_blank_absent_values(row))

    def import_instance(self, instance, row, **kwargs):
        errors = {}

        # T116, T117: a published determination identifier that repeats
        # inside this file is refused at its second occurrence - identity
        # is the published identifier alone (D10), so a row that reuses
        # one is a fault in the file, not a second measurement of it.
        local_id = (row.get("ID") or "").strip()
        if local_id:
            if local_id in self._local_ids_seen:
                errors["ID"] = ValidationError(
                    force_str(
                        f"Determination identifier '{local_id}' is repeated "
                        f"within this file. A published identifier must be "
                        f"unique within one release; the file is refused "
                        f"rather than letting this row overwrite the first."
                    ),
                    code="invalid",
                )
            else:
                self._local_ids_seen.add(local_id)

        for field in self.get_import_fields():
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            try:
                self.import_field(field, instance, row, **kwargs)
            except ValueError as e:
                errors[field.column_name] = ValidationError(
                    force_str(e), code="invalid"
                )

        # T081-T084: a scalar or many-valued value the site, interval,
        # gradient or conductivity builders would refuse is checked here,
        # before ``before_save_instance`` ever calls ``save()`` on any of
        # them - the same "nothing is written for a refused row" shape the
        # interval and site disagreement checks below already give a row.
        # Each widget's own sentinel decides whether it has anything to
        # check at all (T_grad_mean/tc_mean absent means no gradient or
        # conductivity is built, so their columns are not consulted).
        for widget, sentinel_value in (
            (self._parent_widget, row.get("name")),
            (self._interval_widget, None),
            (self._gradient_widget, row.get("T_grad_mean")),
            (self._conductivity_widget, row.get("tc_mean")),
        ):
            try:
                widget.clean(sentinel_value, row=row)
            except ValueError as exc:
                column_errors = getattr(exc, "column_errors", None)
                if column_errors:
                    errors.update(column_errors)
                else:
                    errors["__related__"] = ValidationError(
                        force_str(exc), code="invalid"
                    )

        reference = (row.get("publication_reference") or "").strip()
        if not reference:
            errors["publication_reference"] = ValidationError(
                force_str("A row's publication reference must not be empty."),
                code="invalid",
            )
        else:
            normalized = _normalize_publication_reference(reference)
            matches = self._ambiguous_references.get(normalized)
            if matches is not None:
                matched_keys = ", ".join(sorted(m.citation_key for m in matches))
                errors["publication_reference"] = ValidationError(
                    force_str(
                        f"Publication reference '{reference}' matches more "
                        f"than one bibliographic record: {matched_keys}."
                    ),
                    code="invalid",
                )

        interval_key = _interval_disagreement_key(row)
        errors.update(
            _disagreement_errors(
                self._interval_probe_disagreements, interval_key, "this interval"
            )
        )

        site_key = _site_disagreement_key(row)
        errors.update(
            _disagreement_errors(
                self._site_disagreements, site_key, f"site '{site_key}'"
            )
        )

        if errors:
            raise ValidationError(errors)

    def import_data(self, dataset, *args, **kwargs):
        result = super().import_data(dataset, *args, **kwargs)
        for invalid_row in result.invalid_rows:
            invalid_row.number += 1
        for error_row in result.error_rows:
            error_row.number += 1
        return result

    def before_save_instance(self, instance, row, **kwargs):
        """Turn a checked row into the record graph the model defines
        (US-3): the site, its parent heat flow value, the interval, and
        the gradient and conductivity measured over that interval.

        T052: the site and its parent heat flow value. Each row builds
        its own for now - sharing a site across rows that carry the same
        published site identifier is T057/T058. ``row`` has already had
        the absent-value marker read as no value, in every column, by
        ``before_import_row`` (T076, T077).
        """
        reference = (row.get("publication_reference") or "").strip()
        normalized = _normalize_publication_reference(reference)
        dataset = self._datasets_by_reference[normalized]
        instance.dataset = dataset

        site, parent = self._build_site_and_parent(row, dataset)
        instance.parent = parent

        interval = self._build_interval(row, site, dataset)
        instance.sample = interval

        self._build_probe_metadata(row, interval)

        instance.thermal_gradient = self._build_gradient(row, interval, dataset)
        instance.thermal_conductivity = self._build_conductivity(row, interval, dataset)

        instance.c_comment = row.get("c_comment") or ""
        instance.expedition = row.get("expedition") or ""
        instance.water_temperature = QuantityWidget("°C").clean(
            row.get("water_temperature")
        )
        q_date = (row.get("q_date") or "").strip()
        instance.date_acquired = (
            None
            if not q_date or normalize_vocab_token(q_date) == "unspecified"
            else q_date
        )
        instance.is_relevant = YesNoWidget().clean(row.get("relevant_child")) or False

    def after_save_instance(self, instance, row, **kwargs):
        """Build the records that depend on the determination already
        being saved (T066, T067): a correction record for each correction
        the row supplies."""
        self._build_corrections(instance, row)
        self._set_method(instance, row)

    def _set_method(self, instance, row):
        """The heat-flow calculation method(s) the row reports, a
        many-valued vocabulary column like any other (``q_method``)."""
        from heat_flow import vocabularies

        raw = (row.get("q_method") or "").strip()
        if not raw:
            return
        queryset = MultiConceptWidget(vocabularies.HeatFlowMethod).clean(raw, row=row)
        if queryset is not None:
            instance.method.set(queryset)

    def _build_corrections(self, instance, row):
        """A correction record for each correction column the row
        supplies, and none for the rest (FR-029, T066, T067) - a blank
        column means the row makes no statement about that correction,
        not that the correction was checked and found absent. Found by
        its determination and correction type rather than created a
        second time on a reimport of the same row (T102) - the model's
        own ``unique_together`` on the two is what a correction is
        identified by (R7).
        """
        from heat_flow.models import HeatFlowCorrection

        for column, correction_type in CORRECTION_COL_MAP.items():
            raw = (row.get(column) or "").strip()
            if not raw:
                continue
            HeatFlowCorrection.objects.update_or_create(
                heat_flow=instance,
                correction_type=correction_type,
                defaults={"status": _correction_status(raw)},
            )

    def _build_interval(self, row, site, dataset):
        """Return the interval a row's determination is measured over
        (T053): the depth range the row gives, on the row's site -
        identified by that site together with the depth range (D15,
        T059, T060), shared with every earlier row that gave the same
        site and range. A row giving no depth range at all shares the
        site's one indeterminate interval (D17, T061, T062), since an
        empty range is a range like any other for identity purposes.

        Scalar and many-valued fields are only applied when the interval
        is built for the first time - a later row sharing it is linked,
        not re-applied, the same precedent ``_build_site_and_parent``
        already sets for a reused site or parent.

        The in-pass cache alone does not survive a second import pass
        (D23) - a row whose interval was not built this pass falls back
        to a database lookup, the same two-step ``_build_site_and_parent``
        already uses for the site itself, so a reimport finds and shares
        the interval an earlier pass created rather than building a
        second one (T097).
        """
        interval = self._interval_widget.clean(None, row=row) or HeatFlowInterval()
        key = (
            site.pk,
            _depth_magnitude(interval.top),
            _depth_magnitude(interval.bottom),
        )

        cached = self._intervals_by_key.get(key)
        if cached is not None:
            return cached

        existing = HeatFlowInterval.objects.filter(
            site=site, top=interval.top, bottom=interval.bottom
        ).first()
        if existing is not None:
            self._intervals_by_key[key] = existing
            return existing

        interval.site = site
        interval.dataset = dataset
        interval.save()
        self._interval_widget.set_m2m_relations(interval)
        self._intervals_by_key[key] = interval
        return interval

    def _build_probe_metadata(self, row, interval):
        """Probe metadata belongs to the interval, at most one record per
        interval (T070, T071, D18, FR-031) - the relationship is a
        one-to-one field on the model already and needs no change
        (research.md R7). Skipped where the row supplies no probe
        column, and skipped where the interval already has one, whether
        built by an earlier row in this pass, reused from a row that
        shares the interval, or already on the interval from an earlier
        import pass entirely - the in-pass cache alone would attempt a
        second record on reimport, the same gap D23 recorded for the
        interval itself (T097), so a cache miss falls back to the
        database before building anything.
        """
        if interval.pk in self._probe_metadata_by_interval_id:
            return

        from heat_flow.models import ProbeMetadata

        existing = ProbeMetadata.objects.filter(interval=interval).first()
        if existing is not None:
            self._probe_metadata_by_interval_id[interval.pk] = existing
            return

        penetration = QuantityWidget("m").clean(row.get("probe_penetration"))
        length = QuantityWidget("m").clean(row.get("probe_length"))
        tilt = QuantityWidget("°").clean(row.get("probe_tilt"))
        probe_type_given = bool(_vocab_term(row.get("probe_type") or ""))

        if (
            penetration is None
            and length is None
            and tilt is None
            and not probe_type_given
        ):
            return

        probe = ProbeMetadata(
            interval=interval,
            penetration=penetration,
            length=length,
            tilt=tilt,
        )
        probe.save()
        if probe_type_given:
            from heat_flow import vocabularies

            widget = MultiConceptWidget(vocabularies.ProbeType)
            queryset = widget.clean(row.get("probe_type"), row=row)
            if queryset is not None:
                probe.probe_type.set(queryset)
        self._probe_metadata_by_interval_id[interval.pk] = probe

    def _build_gradient(self, row, interval, dataset):
        """Build the thermal gradient a row's determination was derived
        from, measured over the row's interval (T055). Skipped (``None``)
        when the row gives no ``T_grad_mean``, per ``GradientWidget``'s
        own sentinel. Every row with a gradient gets its own, identified
        by that row's own published determination identifier (D16, T064,
        T065) - the file gives no identifier that would let two rows be
        recognised as reporting one measurement, so a determination
        derived again over an existing interval reports its own gradient
        rather than finding and updating an earlier row's. That row's own
        identifier is also what a reimport of the same row finds it by
        (T101): where a gradient with that identifier already exists, its
        scalar fields are refreshed from the row in place rather than
        duplicating the record - carrying the pk of a freshly built,
        otherwise-unpopulated instance onto ``save()`` instead would
        overwrite fields the widget never touches (the measurement
        base's own ``added``, in particular) with their defaults.
        """
        return self._build_measurement(
            ThermalGradient,
            self._gradient_widget,
            row.get("T_grad_mean"),
            row,
            interval,
            dataset,
        )

    @staticmethod
    def _build_measurement(model, widget, raw, row, interval, dataset):
        """The gradient and the conductivity are built the same way: the
        widget decides whether the row reports one at all, the published
        determination identifier decides whether it is a new record or an
        existing one to refresh, and only the fields the widget sets are
        carried over."""
        record = widget.clean(raw, row=row)
        if record is None:
            return None
        local_id = (row.get("ID") or "").strip()
        existing = model.objects.filter(local_id=local_id).first()
        if existing is not None:
            for field_name in widget.scalar_map:
                setattr(existing, field_name, getattr(record, field_name))
            record = existing
        record.dataset = dataset
        record.sample = interval
        record.local_id = local_id
        record.save()
        widget.set_m2m_relations(record)
        return record

    def _build_conductivity(self, row, interval, dataset):
        """Build the interval conductivity a row's determination was
        derived from (T055), identified by that row's own published
        determination identifier (D16, T064, T065) for the same reason as
        the gradient, and found and refreshed by it on a reimport of the
        same row (T101) the same way. Skipped (``None``) when the row
        gives no ``tc_mean``, per ``ConductivityWidget``'s own sentinel.
        """
        return self._build_measurement(
            IntervalConductivity,
            self._conductivity_widget,
            row.get("tc_mean"),
            row,
            interval,
            dataset,
        )

    def _build_site_and_parent(self, row, dataset):
        """Return the row's site and its parent heat flow value, building
        each once and reusing it for every later row that carries the
        same published site identifier (T057, T058) - a site is
        identified by that identifier alone (D10), no proximity or name
        matching, and a site holds only one parent (the model's own
        uniqueness constraint on ``ParentHeatFlow.sample``).
        """
        local_id = (row.get("ID_parent") or "").strip()

        site = self._sites_by_local_id.get(local_id)
        if site is None:
            try:
                site = HeatFlowSite.objects.get(local_id=local_id)
            except HeatFlowSite.DoesNotExist:
                site = self._build_new_site(row, local_id, dataset)
            self._sites_by_local_id[local_id] = site
        # A site just built already sits in this row's dataset, so the
        # comparison below is a no-op for it and the rule reads as one
        # rule applied to every resolved site (D6).
        self._reassign_site_dataset_if_earlier(site, dataset)

        parent = self._parents_by_site_id.get(site.pk)
        if parent is None:
            try:
                parent = ParentHeatFlow.objects.get(sample=site)
            except ParentHeatFlow.DoesNotExist:
                parent = ParentHeatFlow(
                    sample=site,
                    dataset=dataset,
                    local_id=local_id,
                    value=QuantityWidget("mW/m^2").clean(row.get("q")),
                    uncertainty=QuantityWidget("mW/m^2").clean(
                        row.get("q_uncertainty")
                    ),
                    comment=row.get("p_comment") or "",
                    corr_HP_flag=YesNoWidget().clean(row.get("corr_HP_flag")),
                )
                parent.save()
            self._parents_by_site_id[site.pk] = parent

        return site, parent

    def _reassign_site_dataset_if_earlier(self, site, dataset):
        """FR-037, FR-038: a site belongs to the dataset of the earliest
        publication year among the determinations reported for it,
        compared on every row that shares the site - within one import
        pass (T103, T104) and across separate ones (T105-T107), since the
        comparison reads the year back off each dataset's own
        bibliographic record rather than anything held only for this
        pass. Never moves the site when either year is unknown, or when
        the incoming publication is not strictly earlier (D6: the portal
        does not guess at supplied data).
        """
        if dataset.pk == site.dataset_id:
            return
        current_year = _publication_year(site.dataset)
        incoming_year = _publication_year(dataset)
        if (
            current_year is None
            or incoming_year is None
            or incoming_year >= current_year
        ):
            return
        site.dataset = dataset
        site.save(update_fields=["dataset"])

    def _build_new_site(self, row, local_id, dataset):
        """Build a site for a published site identifier seen for the
        first time (T052). ``ParentWidget`` is reused as it stands
        (plan.md) for the fields it already knows how to extract; the
        published site identifier and the location are set directly here
        (D10, D14) rather than through the widget's own name-based
        sentinel, since a site is built for every distinct identifier
        regardless of whether the row also gives it a name.
        """
        site = self._parent_widget.clean(row.get("name"), row=row) or HeatFlowSite()
        site.local_id = local_id
        site.dataset = dataset
        self._set_site_location(site, row)
        site.save()
        self._parent_widget.set_m2m_relations(site)
        return site

    def _set_site_location(self, site, row):
        """Set the site's location from the row's coordinates, whether or
        not the site's name is present (D14: an empty name never leaves a
        site without a location). ``ParentWidget`` may already have
        attached an unsaved ``Point`` (T052) - either way, the location
        assigned here is a saved one, since ``HeatFlowSite.save()``
        refuses an unsaved related object.
        """
        lat = (row.get("lat_NS") or "").strip()
        lon = (row.get("long_EW") or "").strip()
        if not lat or not lon:
            return
        from fairdm.contrib.location.models import Point

        point, _created = Point.objects.get_or_create(x=float(lon), y=float(lat))
        site.location = point

    class Meta:
        model = HeatFlow
        fields = ("qc", "qc_uncertainty", "local_id")
        # T100: a determination is identified by its published
        # identifier (D10, FR-026), the same field child.py's own
        # resource already upserts on - so a reimport of the same row
        # updates the existing determination rather than creating a
        # second one (T099).
        import_id_fields = ("local_id",)
