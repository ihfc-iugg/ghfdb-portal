# Tests

Tests mirror the source tree. A test module sits at the path its subject sits at under `project/`, with `test_` prefixed at each level, so `project/ghfdb/resources/export.py` is tested by `tests/test_ghfdb/test_resources/test_export.py`.

## Layout

```
tests/
├── conftest.py                 # settings shared by the whole suite
├── fixtures/                   # sample spreadsheets and JSON, see fixtures/README.md
│
├── test_ghfdb/                 # project/ghfdb/
│   ├── conftest.py
│   ├── test_admin.py
│   ├── test_managers.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_resources/         # project/ghfdb/resources/
│       ├── conftest.py
│       ├── test_child_import.py
│       ├── test_export.py
│       ├── test_managers.py
│       ├── test_parent_import.py
│       ├── test_roundtrip.py
│       ├── test_schema_coverage.py
│       └── test_widgets.py
│
└── test_heat_flow/             # project/heat_flow/
    ├── conftest.py
    ├── test_config.py
    ├── test_factories.py
    └── test_models.py
```

`project/review/` has no tests yet.

## Conventions

**Group tests in classes.** Related tests live together in a `Test<Subject>` class named for what they exercise, not as loose module-level functions. A test that spans two functions belongs in the module of its subject, as another class.

**Name tests for their outcome.** `test_<action>_<condition>_<expected_result>` — `test_zero_thickness_interval_rejected` rather than `test_interval_validation`. The name should say what broke without opening the file.

**Fixtures live in `conftest.py`,** at the narrowest level that serves them. Construction shared by one app's tests goes in that app's `conftest.py`, not repeated in each module.

**Fixtures for the models under test use direct ORM calls, deliberately.** Factories fill fields with generated values, which hides whether a field was required and masks the validation paths several of these tests exist to exercise. Factories are used for supporting objects that are infrastructure rather than subject — `DatasetFactory` is the usual one. `project/heat_flow/factories.py` holds the app's own factories, subclassing FairDM's `SampleFactory` and `MeasurementFactory`.

## Running them

```bash
pytest                                   # everything
pytest tests/test_heat_flow/             # one app
pytest tests/test_heat_flow/test_models.py::TestHeatFlowInterval
pytest --cov --cov-report=html           # with coverage
```

`--reuse-db` and `--nomigrations` are on by default, so the first run builds the test database and later runs reuse it. Pass `--create-db` after a migration change.

## Markers

| Marker | For |
|---|---|
| `heat_flow`, `ghfdb`, `review` | the app a test belongs to |
| `integration` | needs the full stack rather than one unit |
| `slow` | takes more than a few seconds |

Select with `pytest -m heat_flow` or exclude with `pytest -m "not slow"`.

## Test data

Shared spreadsheets and JSON live in `fixtures/`, described in `fixtures/README.md`. Anything used by a single module belongs beside that module rather than in the shared directory.

## Adding tests

Write the test first and watch it fail before writing the code that passes it. Put it in the module that mirrors its subject, in a class named for that subject, and give it a name that states the expected outcome. If a fixture would be useful to more than one module, move it up to the nearest `conftest.py`.

The project's engineering standards are in `memory/constitution.md`. Note that `docs/constitution/` is unrelated — that is governance and published reference material.
