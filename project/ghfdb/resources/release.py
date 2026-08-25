"""
GHFDB release import resource and reading format (specs/003-ghfdb-release-import).

Implements the first part of US-1: a release file is checked in full before
anything is written. ``GHFDBReleaseCSVFormat`` reads the comma-separated
format a published release is distributed in, and
``GHFDBReleaseImportResource`` validates a file's header against the
release column definitions in ``constants.py`` before any row is read
(FR-003 to FR-007), then reports every refused value by the column name a
curator sees in the header and the line it occupies in the file (FR-009,
FR-010).

This part of the story checks a file and reports its faults. It does not
turn a row into the site, interval and determination it describes, or
create the dataset and literature a row's publication reference resolves
to - that is later work, and ``save_instance`` is a deliberate no-op here
for that reason.

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
from heat_flow.models import HeatFlow, HeatFlowInterval, HeatFlowSite, ParentHeatFlow
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
    normalize_vocab_token,
)

# FR-006: a column the release format requires. DISCARDED_COLUMNS is
# deliberately excluded - two of its members (the legacy per-row quality
# codes) are never present in a real release (R1), so their absence cannot
# be a fault, and the rest are recognised only if a file happens to carry
# them (D13).
REQUIRED_COLUMNS = READ_COLUMNS


def _blank_row_for_quantity_widgets(row):
    """The row a quantity-parsing widget sees, with the published
    absent-value marker (R1: ``[Unspecified]``, the only non-numeric value
    a numeric column holds) blanked out.

    Reading the marker as no value everywhere, for every widget, is
    FR-012's job in full and is T076/T077's - out of this story's scope.
    This reaches only as far as this story's own row-to-record builders
    need: the real base fixture carries the marker by design (T004), and
    without this, ``QuantityWidget`` crashes outright on it rather than
    refusing cleanly, which would break US-1's already-passing
    whole-fixture tests the moment a real interval, gradient or
    conductivity is built from every row. The vocabulary widgets already
    tolerate the marker on their own (``normalize_vocab_token``).
    """
    return {
        key: "" if value == "[Unspecified]" else value for key, value in row.items()
    }


def _normalize_publication_reference(reference: str) -> str:
    """FR-017: two publication references are the same reference once
    surrounding whitespace and case are ignored."""
    return reference.strip().lower()


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

    def before_import(self, dataset, **kwargs):
        headers = dataset.headers or []
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

    def _resolve_publication_datasets(self, dataset):
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
        for row in dataset.dict:
            raw_reference = (row.get("publication_reference") or "").strip()
            if not raw_reference:
                continue
            references_by_normalized.setdefault(
                _normalize_publication_reference(raw_reference), raw_reference
            )

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
            release_dataset, _created = Dataset.all_objects.get_or_create(
                reference=literature_item,
                defaults={
                    "name": literature_item.title or literature_item.citation_key
                },
            )
            datasets_by_reference[normalized] = release_dataset
        return datasets_by_reference, ambiguous_references

    def import_instance(self, instance, row, **kwargs):
        errors = {}
        for field in self.get_import_fields():
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            try:
                self.import_field(field, instance, row, **kwargs)
            except ValueError as e:
                errors[field.column_name] = ValidationError(
                    force_str(e), code="invalid"
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
        published site identifier is T057/T058.
        """
        reference = (row.get("publication_reference") or "").strip()
        normalized = _normalize_publication_reference(reference)
        dataset = self._datasets_by_reference[normalized]
        instance.dataset = dataset

        row = _blank_row_for_quantity_widgets(row)

        site, parent = self._build_site_and_parent(row, dataset)
        instance.parent = parent

        interval = self._build_interval(row, site, dataset)
        instance.sample = interval

        self._build_probe_metadata(row, interval)

        instance.thermal_gradient = self._build_gradient(row, interval, dataset)
        instance.thermal_conductivity = self._build_conductivity(row, interval, dataset)

    def after_save_instance(self, instance, row, **kwargs):
        """Build the records that depend on the determination already
        being saved (T066, T067): a correction record for each correction
        the row supplies."""
        self._build_corrections(instance, row)

    def _build_corrections(self, instance, row):
        """A correction record for each correction column the row
        supplies, and none for the rest (FR-029, T066, T067) - a blank
        column means the row makes no statement about that correction,
        not that the correction was checked and found absent."""
        from heat_flow.models import HeatFlowCorrection

        for column, correction_type in CORRECTION_COL_MAP.items():
            raw = (row.get(column) or "").strip()
            if not raw:
                continue
            HeatFlowCorrection.objects.create(
                heat_flow=instance,
                correction_type=correction_type,
                status=_correction_status(raw),
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
        built by an earlier row in this pass or reused from a row that
        shares the interval.
        """
        if interval.pk in self._probe_metadata_by_interval_id:
            return

        penetration = QuantityWidget("m").clean(row.get("probe_penetration"))
        length = QuantityWidget("m").clean(row.get("probe_length"))
        tilt = QuantityWidget("°").clean(row.get("probe_tilt"))
        probe_type_normalized = normalize_vocab_token(row.get("probe_type") or "")
        probe_type_given = (
            bool(probe_type_normalized) and probe_type_normalized != "unspecified"
        )

        if (
            penetration is None
            and length is None
            and tilt is None
            and not probe_type_given
        ):
            return

        from heat_flow.models import ProbeMetadata

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
        rather than finding and updating an earlier row's.
        """
        gradient = self._gradient_widget.clean(row.get("T_grad_mean"), row=row)
        if gradient is None:
            return None
        gradient.dataset = dataset
        gradient.sample = interval
        gradient.local_id = (row.get("ID") or "").strip()
        gradient.save()
        self._gradient_widget.set_m2m_relations(gradient)
        return gradient

    def _build_conductivity(self, row, interval, dataset):
        """Build the interval conductivity a row's determination was
        derived from (T055), identified by that row's own published
        determination identifier (D16, T064, T065) for the same reason as
        the gradient. Skipped (``None``) when the row gives no
        ``tc_mean``, per ``ConductivityWidget``'s own sentinel."""
        conductivity = self._conductivity_widget.clean(row.get("tc_mean"), row=row)
        if conductivity is None:
            return None
        conductivity.dataset = dataset
        conductivity.sample = interval
        conductivity.local_id = (row.get("ID") or "").strip()
        conductivity.save()
        self._conductivity_widget.set_m2m_relations(conductivity)
        return conductivity

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
                )
                parent.save()
            self._parents_by_site_id[site.pk] = parent

        return site, parent

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
        # No upsert identity yet: finding a determination by its published
        # identifier is later work (US-4). Every row is a new, unsaved
        # instance until then.
        import_id_fields = ()
