# Tests Directory Structure

This directory contains all tests for the Global Heat Flow Database project, organized by Django app.

## Directory Structure

```
tests/
├── __init__.py                 # Main tests package
├── test_heat_flow/            # Tests for heat_flow app
│   ├── __init__.py
│   ├── test_factories.py      # Factory tests
│   ├── test_models.py         # Model tests
│   └── test_views.py          # View tests
├── test_ghfdb/                # Tests for ghfdb app
│   ├── __init__.py
│   ├── test_importer.py       # Import functionality tests
│   ├── test_models.py         # Model tests
│   ├── test_views.py          # View tests
│   └── data/                  # Test data files
│       ├── importer_fail.xlsx
│       ├── importer_fail_single_row.xlsx
│       └── importer_success.xlsx
└── test_review/               # Tests for review app
    ├── __init__.py
    └── test_models.py         # Model tests
```

## Running Tests

### Run all tests
```bash
poetry run python -m pytest
```

### Run tests for a specific app
```bash
# Heat flow app tests
poetry run python -m pytest tests/test_heat_flow/ -v

# GHFDB app tests  
poetry run python -m pytest tests/test_ghfdb/ -v

# Review app tests
poetry run python -m pytest tests/test_review/ -v
```

### Run specific test files
```bash
# Factory tests only
poetry run python -m pytest tests/test_heat_flow/test_factories.py -v

# Importer tests only
poetry run python -m pytest tests/test_ghfdb/test_importer.py -v
```

### Run tests with markers
```bash
# Run tests marked as slow
poetry run python -m pytest -m slow

# Run integration tests
poetry run python -m pytest -m integration
```

## Test Organization Guidelines

- **test_heat_flow/**: Tests for the heat_flow Django app
  - Models, views, forms, factories, utilities
- **test_ghfdb/**: Tests for the ghfdb Django app  
  - Import functionality, data processing, models
- **test_review/**: Tests for the review Django app
  - Review workflow, models, views
- **data/**: Test data files should be placed in the appropriate app subdirectory

## Adding New Tests

When adding new tests:

1. Place them in the appropriate app subdirectory
2. Follow the naming convention: `test_*.py`
3. Use descriptive class and method names
4. Add appropriate markers for test categorization
5. Include docstrings for test classes and methods

## Test Data

Test data files are organized within each app's test directory under a `data/` subdirectory. This keeps test data close to the tests that use it while maintaining organization.
