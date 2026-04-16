# Quickstart: GHFDB Import / Export

**Feature**: 003-ghfdb-import-export
**Split from**: `002-ghfdb-proxy` quickstart.md — import/export sections

> **Prerequisite**: The `GHFDB` proxy model from `002-ghfdb-proxy` must be installed and migrated before running any import or export.

## Module Layout

```
project/ghfdb/resources/
├── __init__.py          # Public API: GHFDBParentImportResource, GHFDBChildImportResource, GHFDBExportResource, GHFDBImportFormat
├── _base.py             # GHFDBImportFormat, GHFDB_COLUMN_ORDER, PARENT_COLUMNS, CORRECTION_COL_MAP
├── _widgets.py          # ConceptWidget, MultiConceptWidget, QuantityWidget, YesNoWidget, RelatedModelWidget subclasses
├── parent.py            # GHFDBParentImportResource
├── child.py             # GHFDBChildImportResource
└── export.py            # GHFDBExportResource
```

## Import Workflow

### 1. Import Parent Records

1. Navigate to **Admin → GHFDB → GHFDB entries**
2. Click **Import** and select the **"Parent Import"** resource
3. Upload the GHFDB XLSX file
4. The parent import processes the `"data list"` sheet, deduplicating rows by `ID_parent` (or by `lat_NS`/`long_EW` for standard templates that omit `ID_parent`)
5. Preview shows one row per unique parent record with a diff of changed fields
6. Confirm to create/update parent records, or cancel to discard

### 2. Import Child Measurements

1. After parent records are imported, click **Import** again and select the **"Child Import"** resource
2. Upload the **same** GHFDB XLSX file
3. The child import processes every row, linking each child measurement to its parent
4. For each row, the import creates/updates:
   - `HeatFlowInterval` (depth interval)
   - `HeatFlow` (the measurement)
   - `ThermalGradient` (if `T_grad_mean` is non-empty)
   - `IntervalConductivity` (if `tc_mean` is non-empty)
   - `ProbeMetadata` (if any probe column is non-empty)
   - 9 `HeatFlowCorrection` records (from `corr_*_flag` columns)
5. Confirm to apply, or cancel to discard

> **Order matters**: Always import parent records first. The child import looks up `ParentHeatFlow` by `local_id`; if the parent doesn't exist, child rows error.

### Template Types

| Template Type | `ID_parent` / `ID` present? | Upsert Key |
|---|---|---|
| Official GHFDB release (round-trip) | Yes | `local_id` (stored from `ID`/`ID_parent`) |
| Standard individual-dataset upload | No | `lat_NS` + `long_EW` (parent); location + depth + `publication_reference` (child) |

## Export Workflow

1. Navigate to **Admin → GHFDB → GHFDB entries**
2. Optionally filter the queryset (search, list filters)
3. Select records (or select all)
4. Choose **Export** from the action dropdown and select XLSX format
5. The export produces a GHFDB-compliant XLSX: 62 columns in canonical order, M2M fields semicolon-joined, Pint quantities as plain numeric magnitudes

## Running Tests

```bash
# All import/export tests
poetry run pytest tests/test_ghfdb/test_resources/ -v

# Individual test modules
poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_export.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_roundtrip.py -v

# Full GHFDB suite
poetry run pytest tests/test_ghfdb/ -v
```

## Vocabulary Normalisation (FR-016)

Spreadsheet cells may contain bracket-wrapped, mixed-case vocabulary labels (e.g., `[Onshore (continental)]`). All tokens are normalised before lookup:

```python
normalize_vocab_token("[Onshore (continental)]")
# → "onshore (continental)"  (brackets stripped, lowercased)
```

Invalid tokens raise `ValueError` with the **original** text preserved in the error message.
