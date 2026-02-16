# Test Fixtures

This directory contains test fixture data files for the Global Heat Flow Database (GHFDB) testing infrastructure. These fixtures support unit, integration, and contract testing across the codebase.

## Overview

Test fixtures are divided into two categories:

1. **Excel Fixtures** (`.xlsx`): GHFDB-formatted spreadsheet data for import/export testing
2. **JSON Fixtures** (`.json`): Django model fixtures representing database states

## Excel Fixtures

### minimal_ghfdb_import.xlsx

**Purpose**: Minimal valid dataset for basic import functionality testing

**Contents**:
- 5 heat flow sites with complete mandatory fields
- Diverse geographic locations and environments:
  - Offshore continental drilling (Spain, Bay of Biscay)
  - Onshore borehole (USA, Texas)
  - Marine probe (Pacific Ocean abyssal plain)
  - Continental drilling (Germany, Thuringian Basin)
  - Geothermal exploration (Iceland, Reykjanes Peninsula)
- All mandatory fields populated:
  - Site identification: `name`, `lat_NS`, `long_EW`
  - Environment and methods: `environment`, `explo_method`
  - Heat flow measurements: `q`, `q_uncertainty`
  - Child measurements: `qc`, `q_top`, `q_bottom`
  - Thermal data: `T_grad_mean`, `T_grad_uncertainty`
  - Conductivity: `tc_mean`, `tc_uncertainty`

**Usage**:
```python
from ghfdb.resources import GHFDBResource
from ghfdb.views import GHFDBImportFormat

resource = GHFDBResource(dataset)
file = get_file("fixtures/minimal_ghfdb_import.xlsx")
input_format = GHFDBImportFormat(encoding="utf-8-sig")
input_data = input_format.create_dataset(file)
result = resource.import_data(input_data)
```

**Test Files**: 
- `tests/test_ghfdb/test_basic_import.py` (to be created)
- `tests/test_ghfdb/test_schema_mapping.py` (to be created)

---

### invalid_ghfdb_import.xlsx

**Purpose**: Validation error testing - ensures proper error handling for invalid data

**Contents**:
- 5 deliberately invalid records demonstrating different error conditions:
  1. **Missing mandatory field**: `name` is `None` (should fail)
  2. **Out-of-bounds coordinate**: `lat_NS` = 95.0 (latitude must be ≤ 90)
  3. **Negative heat flow**: `q` = -25.0 (heat flow must be non-negative)
  4. **Missing environment**: `environment` field is `None` (mandatory field)
  5. **Inconsistent depth**: `q_top` (1000m) > `q_bottom` (500m) (logically invalid)

**Expected Behavior**:
- Import should fail with clear error messages
- Each validation error should be reported with:
  - Row number
  - Field name
  - Error type (missing, out-of-range, inconsistent)

**Usage**:
```python
result = resource.import_data(input_data, raise_errors=False)
assert result.has_errors()
assert len(result.invalid_rows) == 5
```

**Test Files**: 
- `tests/test_ghfdb/test_validation_errors.py` (to be created)
- `tests/test_ghfdb/test_importer.py` (existing - similar patterns)

---

### round_trip_reference.xlsx

**Purpose**: Comprehensive data coverage for export→import roundtrip integrity testing

**Contents**:
- 10 heat flow sites covering all field variations:
  - **All environment types**: Offshore (continental/oceanic), Continental (plateau/cratonic/orogenic/volcanic)
  - **All exploration methods**: Drilling, Probe
  - **All exploration purposes**: Hydrocarbon, Scientific, Geothermal
  - **All correction flags**: HP, IS, T, S, E, TOPO, PAL, SUR, CONV, HR
  - **All measurement types**:
    - Probe measurements (with probe_type, probe_length, probe_tilt, water_temperature)
    - Borehole measurements (BHT, Logging)
    - Laboratory measurements (all thermal conductivity methods)
  - **All controlled vocabularies**:
    - Geographic environments: 5 different types
    - Thermal measurement methods: BHT, Logging, Thermistor
    - Conductivity methods: Lab - TCS, Lab - divided bar, Lab - needle probe
    - Conductivity sources: Measurement, Publication, Database
    - Lithologies: Granite, Sandstone, Shale, Limestone, Basalt, Andesite, Schist, Gneiss
    - Stratigraphy: Precambrian, Paleozoic, Mesozoic, Cenozoic, Quaternary
  - **Optional fields**: expedition, probe details, temperature corrections, IGSN references
  - **Geographic diversity**: Sites from 6 continents, elevation range -4500m to +2450m

**Geographic Coverage**:
| Site | Location | Environment | Elevation | Purpose |
|------|----------|-------------|-----------|---------|
| 1001 | France (Bay of Biscay) | Offshore continental | -125.5m | Hydrocarbon |
| 1002 | Tasman Sea | Offshore oceanic | -4500m | Scientific |
| 1003 | Russia (Siberian Platform) | Continental cratonic | 125m | Scientific |
| 1004 | Greece (Hellenic Arc) | Continental orogenic | 850m | Geothermal |
| 1005 | Samoa | Continental volcanic | 320m | Geothermal |
| 1006 | Kenya (East African Rift) | Continental orogenic | 1200m | Scientific |
| 1007 | USA (Gulf of Mexico) | Offshore continental | -1850m | Hydrocarbon |
| 1008 | Iraq (Mesopotamian Basin) | Continental cratonic | 45m | Hydrocarbon |
| 1009 | Canada (Saskatchewan) | Continental cratonic | 525m | Scientific |
| 1010 | Switzerland (Swiss Alps) | Continental orogenic | 2450m | Scientific |

**Usage**:
```python
# Test export
resource = GHFDBResource(dataset)
export_data = resource.export()

# Test import of exported data
input_data = GHFDBImportFormat().create_dataset(export_data)
result = resource.import_data(input_data)

# Verify data integrity
assert all_fields_match(original_data, re_imported_data)
```

**Test Files**: 
- `tests/test_ghfdb/test_round_trip.py` (to be created)
- `tests/test_ghfdb/test_export.py` (to be created)

---

## JSON Fixtures

### review_submission_dataset.json

**Purpose**: Represents a dataset submission in "pending review" state

**Contents**:
- **Project** (pk=100): "Test Review Project"
  - Status: Active (1)
  - Visibility: Public (1)
  
- **Dataset** (pk=100): "Test Submission - Pending Review"
  - Visibility: Private (0) - not yet published
  - Submitted: 2025-07-10
  - Collection period: 2025-01-15 to 2025-03-20
  
- **Dataset Descriptions**:
  - Abstract: Summary of test dataset purpose
  - Methods: Description of data collection methodology
  
- **Dataset Dates**:
  - Submitted: 2025-07-10
  - CollectionStart: 2025-01-15
  - CollectionEnd: 2025-03-20

**Workflow State**: Dataset awaiting admin/reviewer approval

**Usage**:
```python
from django.core.management import call_command

# Load fixture
call_command('loaddata', 'review_submission_dataset.json')

# Verify state
dataset = Dataset.objects.get(pk=100)
assert dataset.visibility == 0  # Private
assert not hasattr(dataset, 'review')  # No review yet
```

**Test Files**: 
- `tests/test_review/test_submission_workflow.py` (to be created)
- `tests/test_review/test_dataset_states.py` (to be created)

---

### admin_approval_dataset.json

**Purpose**: Represents a dataset that has been reviewed and approved for publication

**Contents**:
- **Project** (pk=200): "Test Approved Project"
  - Status: Completed (3)
  - Visibility: Public (1)
  
- **Dataset** (pk=200): "Test Dataset - Approved and Published"
  - Visibility: Public (1) - published
  - Submitted: 2025-06-01
  - Published: 2025-06-15
  - Collection period: 2024-09-01 to 2024-11-30
  
- **Dataset Descriptions**:
  - Abstract: Approved dataset summary
  - Methods: QA/QC methodology details
  - TechnicalInfo: GHFDB format version and metadata standards
  
- **Dataset Dates**:
  - Submitted: 2025-06-01
  - Available: 2025-06-15 (publication date)
  - CollectionStart: 2024-09-01
  - CollectionEnd: 2024-11-30
  
- **Review** (pk=200):
  - Status: Complete (2)
  - Start date: 2025-06-05
  - End date: 2025-06-15
  - Comment: "Dataset reviewed and approved. All quality checks passed..."

**Workflow State**: Complete review lifecycle - submitted → reviewed → approved → published

**Usage**:
```python
# Load fixture
call_command('loaddata', 'admin_approval_dataset.json')

# Verify state
dataset = Dataset.objects.get(pk=200)
assert dataset.visibility == 1  # Public
assert dataset.review.status == 2  # Complete
assert dataset.review.end_date == datetime(2025, 6, 15).date()
```

**Test Files**: 
- `tests/test_review/test_approval_workflow.py` (to be created)
- `tests/test_review/test_review_model.py` (to be created)

---

## Fixture Creation Scripts

Test fixtures are generated using automated scripts to ensure consistency:

### scripts/create_test_fixtures.py

Creates all Excel (`.xlsx`) fixtures:
- `minimal_ghfdb_import.xlsx`
- `invalid_ghfdb_import.xlsx`
- `round_trip_reference.xlsx`

**Run**: `poetry run python scripts/create_test_fixtures.py`

### scripts/create_json_fixtures.py

Creates all Django JSON fixtures:
- `review_submission_dataset.json`
- `admin_approval_dataset.json`

**Run**: `poetry run python scripts/create_json_fixtures.py`

---

## Fixture Loading in Tests

Fixtures are loaded using pytest fixtures defined in `tests/conftest.py`:

```python
# Excel fixture loading
@pytest.fixture
def minimal_ghfdb_import_data():
    """Load minimal GHFDB import fixture."""
    return get_file("fixtures/minimal_ghfdb_import.xlsx")

@pytest.fixture
def invalid_ghfdb_import_data():
    """Load invalid GHFDB import fixture for error testing."""
    return get_file("fixtures/invalid_ghfdb_import.xlsx")

@pytest.fixture
def round_trip_reference_data():
    """Load comprehensive round-trip reference fixture."""
    return get_file("fixtures/round_trip_reference.xlsx")

# Django JSON fixture loading
@pytest.fixture
def review_submission_dataset(django_db_blocker):
    """Load review submission workflow fixture."""
    with django_db_blocker.unblock():
        call_command('loaddata', 'review_submission_dataset.json')
    return Dataset.objects.get(pk=100)

@pytest.fixture
def admin_approval_dataset(django_db_blocker):
    """Load approved dataset with review fixture."""
    with django_db_blocker.unblock():
        call_command('loaddata', 'admin_approval_dataset.json')
    return Dataset.objects.get(pk=200)
```

---

## Data Provenance

All test fixtures are synthetic data created specifically for testing purposes. They do not represent real scientific measurements or published research.

**Key Characteristics**:
- **Realistic but fictional**: Data values are plausible for their geographic locations but are not actual measurements
- **Controlled test cases**: Designed to exercise specific code paths and edge cases
- **Geographic diversity**: Spans multiple continents and environments to test internationalization
- **Quality indicators**: Includes examples of high-quality and lower-quality data for QA testing
- **Completeness levels**: Ranges from minimal mandatory fields to comprehensive optional fields

**References**:
- GHFDB template structure: Fuchs et al. (2021, 2023)
- Field definitions: `docs/ghfdb_fields.md`
- Validation rules: `project/ghfdb/resources.py`

---

## Maintenance Guidelines

### When to Update Fixtures

1. **Schema changes**: If GHFDB template columns are added/removed/renamed
2. **New validation rules**: Add corresponding invalid test cases
3. **New controlled vocabularies**: Include examples in round-trip fixture
4. **Workflow changes**: Update JSON fixtures to reflect new dataset/review states

### Regenerating Fixtures

To regenerate all fixtures after updates to creation scripts:

```bash
poetry run python scripts/create_test_fixtures.py
poetry run python scripts/create_json_fixtures.py
```

### Fixture Versioning

Fixtures should be versioned alongside the GHFDB template version they represent:
- Current fixtures: **GHFDB v2.0** (as of 2025-01-01)
- Tracked in git to ensure test reproducibility
- Document breaking changes in this README

---

## Related Documentation

- [Test Organization Guide](../tests/README.md)
- [GHFDB Field Mapping](../docs/ghfdb_fields.md)
- [Testing Standards Guide](../docs/guides/testing-standards.md) (to be created)
- [Contributing Guide](../CONTRIBUTING.md)
