# GHFDB App Separation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Decouple the `heat_flow` app from GHFDB-specific concepts by removing `SurfaceHeatFlow`, the `parent` FK, and `relevant_child` from `heat_flow`, and ensuring all GHFDB administrative logic lives exclusively in the `ghfdb` app.

**Architecture:** Parent heat flow moves to `ghfdb.ParentHeatFlow` (inheriting FairDM `Measurement`), linked to `heat_flow.HeatFlow` via a M2M with `ParentChildRelation` through model. The `heat_flow` app retains only pure scientific measurement models with no GHFDB knowledge.

**Tech Stack:** Django 5.0+, FairDM framework, django-tables2, django-filter, django-import-export, factory_boy, pytest

**Design Document:** `docs/plans/2026-02-05-ghfdb-app-separation-design.md`

---

## Pre-requisites

Before starting, read the design document for full context on architectural decisions:
- `docs/plans/2026-02-05-ghfdb-app-separation-design.md`

All commands must be prefixed with `poetry run`.

---

### Task 1: Clean up `heat_flow.HeatFlow` model — remove `parent` FK and `relevant_child`

**Files:**
- Modify: `project/heat_flow/models/measurements.py`

**Step 1: Remove the `parent` ForeignKey field from `HeatFlow`**

Remove these lines (~L209-217):
```python
parent = models.ForeignKey(
    SurfaceHeatFlow,
    null=True,
    blank=True,
    verbose_name=_("parent"),
    help_text=_("parent heat flow site"),
    related_name="children",
    on_delete=models.CASCADE,
)
```

**Step 2: Remove the `relevant_child` field from `HeatFlow`**

Remove these lines (~L254-260):
```python
relevant_child = models.BooleanField(
    verbose_name=_("Relevant child"),
    help_text=_(
        "Specify whether the child entry is used for computation of representative location heat flow values at the"
        " parent level or not."
    ),
    default=False,
)
```

**Step 3: Update `HeatFlow.Meta` — remove references to `parent` and `relevant_child`**

In `HeatFlow.Meta`:
- Change `ordering = ["parent", "relevant_child"]` → `ordering = ["pk"]`
- Remove `models.Index(fields=["relevant_child"])` from `indexes`

**Step 4: Remove unused `HeatFlowQuerySet` methods that reference `relevant_child`**

In `HeatFlowQuerySet` (~L44-49), remove:
```python
def relevant_children_only(self):
    """Filter to only relevant child measurements."""
    return self.filter(relevant_child=True)
```

In `HeatFlowManager` (~L83-84), remove:
```python
def relevant_children_only(self):
    return self.get_queryset().relevant_children_only()
```

**Step 5: Commit**

```bash
git add project/heat_flow/models/measurements.py
git commit -m "refactor(heat_flow): remove parent FK and relevant_child from HeatFlow

Part of GHFDB app separation. These fields are GHFDB-specific
and will be handled via ghfdb.ParentChildRelation."
```

---

### Task 2: Remove `SurfaceHeatFlow` model entirely

**Files:**
- Modify: `project/heat_flow/models/measurements.py`
- Modify: `project/heat_flow/models/__init__.py`

**Step 1: Remove the entire `SurfaceHeatFlow` class from `measurements.py`**

Remove the full class definition (~L96-198), including the docstring, all fields, Meta class, save method, `__str__`, `site` property, and `get_quality` method.

**Step 2: Update `__init__.py` to remove `SurfaceHeatFlow` exports**

In `project/heat_flow/models/__init__.py`:
- Remove `SurfaceHeatFlow` from the import line
- Remove `SurfaceHeatFlow` from `__all__`

Result should be:
```python
from .measurements import HeatFlow, IntervalConductivity, ThermalGradient
from .samples import HeatFlowInterval, HeatFlowSite

__all__ = [
    "HeatFlow",
    "HeatFlowInterval",
    "HeatFlowSite",
    "IntervalConductivity",
    "ThermalGradient",
]
```

**Step 3: Commit**

```bash
git add project/heat_flow/models/measurements.py project/heat_flow/models/__init__.py
git commit -m "refactor(heat_flow): remove SurfaceHeatFlow model

Replaced by ghfdb.ParentHeatFlow. The heat_flow app now has no
parent heat flow concept — it is purely scientific measurements."
```

---

### Task 3: Update `ghfdb.ParentHeatFlow` model

**Files:**
- Modify: `project/ghfdb/models.py`

**Step 1: Update `ParentHeatFlow` to ensure it has all necessary fields**

The model already exists and looks mostly correct. Ensure:
- It inherits from `Measurement`
- It has `value`, `uncertainty`, `corr_HP_flag`, `comment`, `is_ghfdb`
- The `children` M2M points to `heat_flow.HeatFlow` via `ParentChildRelation`

**Step 2: Add `save()` method to enforce one parent per site**

Add to `ParentHeatFlow`:
```python
def save(self, *args, **kwargs):
    from django.core.exceptions import ValidationError
    
    if self.sample_id:
        existing = ParentHeatFlow.objects.filter(
            sample=self.sample
        ).exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(
                f"A ParentHeatFlow already exists for site {self.sample}. "
                f"Only one parent per site is allowed."
            )
    super().save(*args, **kwargs)
```

**Step 3: Add `unique=True` to `ParentChildRelation.child`**

In `ParentChildRelation`, update the `child` field to add `unique=True`:
```python
child = models.ForeignKey(
    "heat_flow.HeatFlow",
    on_delete=models.CASCADE,
    verbose_name=_("child heat flow"),
    unique=True,
)
```

**Step 4: Remove `GHFDBManager` if it references old structures**

The current `GHFDBManager` at the top of `ghfdb/models.py` references `parent__is_ghfdb` and `parent__sample` which assume the old FK structure from `HeatFlow.parent`. This manager needs to be rewritten or removed. Since children are now accessed via M2M, the manager should query `ParentHeatFlow` directly, not through children.

Remove `GHFDBManager` class entirely or rewrite it as a manager on `ParentHeatFlow`.

**Step 5: Remove the duplicate `HeatFlowSite` definition from `ghfdb/models.py`**

Currently `ghfdb/models.py` has its own `HeatFlowSite` class (~L32-107) that duplicates `heat_flow.HeatFlowSite`. Remove it — the canonical `HeatFlowSite` lives in `heat_flow.models.samples`.

**Step 6: Update `get_quality` method to use M2M through model**

The `get_quality` method on `ParentHeatFlow` should filter via the through model:
```python
def get_quality(self):
    relevant = self.children.filter(
        parentchildrelation__is_relevant=True
    )
    count = relevant.count()
    if count == 0:
        return None
    elif count == 1:
        return relevant.first().get_quality()
    else:
        return relevant.order_by("quality").first().get_quality()
```

**Step 7: Commit**

```bash
git add project/ghfdb/models.py
git commit -m "refactor(ghfdb): update ParentHeatFlow with one-per-site constraint

- Add save() validation for one parent per site
- Add unique=True on ParentChildRelation.child
- Remove duplicate HeatFlowSite definition
- Remove obsolete GHFDBManager
- Update get_quality to use through model"
```

---

### Task 4: Update heat_flow admin

**Files:**
- Modify: `project/heat_flow/admin.py`

**Step 1: Remove `SurfaceHeatFlowAdmin` registration**

Remove the import of `SurfaceHeatFlow` and the entire `@admin.register(SurfaceHeatFlow)` block (~L19-31).

**Step 2: Remove `parent` and `relevant_child` from `HeatFlowAdmin`**

In `HeatFlowAdmin`:
- Remove `"parent"` from `list_display`
- Remove `"parent"` and `"relevant_child"` from `fieldsets`

**Step 3: Commit**

```bash
git add project/heat_flow/admin.py
git commit -m "refactor(heat_flow): clean admin of SurfaceHeatFlow and parent refs"
```

---

### Task 5: Update `ghfdb` admin (add `ParentHeatFlowAdmin`)

**Files:**
- Modify: `project/ghfdb/admin.py`

**Step 1: Create admin for `ParentHeatFlow` with `ParentChildRelation` inline**

```python
from django.contrib import admin
from .models import ParentHeatFlow, ParentChildRelation, GHFDBRelease

class ParentChildRelationInline(admin.TabularInline):
    model = ParentChildRelation
    extra = 1
    autocomplete_fields = ["child"]

@admin.register(ParentHeatFlow)
class ParentHeatFlowAdmin(admin.ModelAdmin):
    list_display = ["sample", "value", "uncertainty", "corr_HP_flag", "is_ghfdb"]
    list_filter = ["is_ghfdb", "corr_HP_flag"]
    search_fields = ["sample__name"]
    inlines = [ParentChildRelationInline]
    fieldsets = (
        (None, {"fields": ("sample", "dataset")}),
        ("Heat Flow", {"fields": (("value", "uncertainty"), "corr_HP_flag", "comment")}),
        ("GHFDB", {"fields": ("is_ghfdb",)}),
    )

@admin.register(GHFDBRelease)
class GHFDBReleaseAdmin(admin.ModelAdmin):
    list_display = ["version", "release_date"]
```

**Step 2: Commit**

```bash
git add project/ghfdb/admin.py
git commit -m "feat(ghfdb): add ParentHeatFlow admin with inline children"
```

---

### Task 6: Update heat_flow config (FairDM registration)

**Files:**
- Modify: `project/heat_flow/config.py`

**Step 1: Remove `SurfaceHeatFlowConfig` registration**

Remove:
- `SurfaceHeatFlow` from the model imports (~L12)
- `SurfaceHeatFlowTable` from the table imports (~L15)
- The entire `SurfaceHeatFlowConfig` class (~L107-131)

**Step 2: Remove `relevant_child` from `HeatFlowConfig.fields` if present**

Check that `HeatFlowConfig.fields` does not reference `relevant_child`. Currently it doesn't appear to, but verify.

**Step 3: Commit**

```bash
git add project/heat_flow/config.py
git commit -m "refactor(heat_flow): remove SurfaceHeatFlow from FairDM registration"
```

---

### Task 7: Update heat_flow tables

**Files:**
- Modify: `project/heat_flow/tables.py`

**Step 1: Remove `SurfaceHeatFlowTable`**

Remove:
- `SurfaceHeatFlow` from imports (~L7)
- The entire `SurfaceHeatFlowTable` class (~L72-90)

**Step 2: Update `GHFDBTable`**

The `GHFDBTable` at the bottom of the file (~L199-210) references `parent__value`, `parent__uncertainty`, `parent__sample__name` via the old FK traversal. This table is GHFDB-specific and should be moved to the ghfdb app or removed entirely (since queries go through `ParentHeatFlow` now, not through `HeatFlow`).

Remove `GHFDBTable` from `heat_flow/tables.py`. If needed, recreate in `ghfdb/tables.py`.

**Step 3: Commit**

```bash
git add project/heat_flow/tables.py
git commit -m "refactor(heat_flow): remove SurfaceHeatFlowTable and GHFDBTable"
```

---

### Task 8: Update heat_flow factories

**Files:**
- Modify: `project/heat_flow/factories.py`

**Step 1: Remove `SurfaceHeatFlowFactory`**

Remove:
- `SurfaceHeatFlow` from imports (~L13)
- The entire `SurfaceHeatFlowFactory` class (~L33-46)

**Step 2: Remove `relevant_child` from `HeatFlowFactory`**

Remove the line (~L59):
```python
relevant_child = Faker("boolean", chance_of_getting_true=0.8)
```

**Step 3: Create `ParentHeatFlowFactory` in ghfdb (optional — can be done later)**

If needed, create `project/ghfdb/factories.py` with a `ParentHeatFlowFactory`. This can be deferred.

**Step 4: Commit**

```bash
git add project/heat_flow/factories.py
git commit -m "refactor(heat_flow): remove SurfaceHeatFlowFactory and relevant_child"
```

---

### Task 9: Update heat_flow utils

**Files:**
- Modify: `project/heat_flow/utils.py`

**Step 1: Move or remove GHFDB-specific field mapping**

The `GHFDB_field_map` list in `utils.py` (~L10-73) contains parent traversal paths like `parent__value`, `parent__sample__name`, etc. These are GHFDB export concerns and should move to the `ghfdb` app.

Options:
- **Move** `GHFDB_field_map`, `GHFDB_db_fields`, `GHFDB_csv_fields`, and the `GHFDB` manager class to `project/ghfdb/utils.py`
- **Remove** from `heat_flow/utils.py`

Remove everything except the quality score utilities (`MScoreOptions`, `UScoreOptions`, `calculate_U_score`).

**Step 2: Update `__all__`**

```python
__all__ = ["MScoreOptions", "UScoreOptions", "calculate_U_score"]
```

Remove the `DataFrameManager` import if no longer needed.

**Step 3: Commit**

```bash
git add project/heat_flow/utils.py
git commit -m "refactor(heat_flow): move GHFDB field mapping to ghfdb app"
```

---

### Task 10: Update ghfdb resources (import/export)

**Files:**
- Modify: `project/ghfdb/resources.py`

**Step 1: Update imports**

Replace:
```python
from heat_flow.models.measurements import IntervalConductivity, SurfaceHeatFlow, ThermalGradient
```
With:
```python
from heat_flow.models.measurements import IntervalConductivity, ThermalGradient
from ghfdb.models import ParentHeatFlow
```

**Step 2: Update `get_parent_heat_flow` method**

Change the model reference from `SurfaceHeatFlow` to `ParentHeatFlow` (~L773):
```python
def get_parent_heat_flow(self, row):
    return ForeignObjectWidget(
        model=ParentHeatFlow,  # was SurfaceHeatFlow
        ...
    ).clean(None, row)
```

**Step 3: Update `relevant_child` field handling**

The `relevant_child` field in the resource (~L541) currently maps directly to `HeatFlow.relevant_child`. Since that field is removed, this needs to be handled differently:
- During import, after creating the `HeatFlow` child and linking it via `ParentChildRelation`, set `is_relevant` on the through model instead
- This likely requires overriding `after_import_row` or `after_save_instance`

**Step 4: Update `before_import_row` method**

The current method creates `SurfaceHeatFlow` instances. Update to create `ParentHeatFlow` instances instead. The comment referencing `SurfaceHeatFlow` (~L662-666) needs updating.

**Step 5: Commit**

```bash
git add project/ghfdb/resources.py
git commit -m "refactor(ghfdb): update import resource for ParentHeatFlow

Replace SurfaceHeatFlow references with ParentHeatFlow.
Handle relevant_child via ParentChildRelation through model."
```

---

### Task 11: Update tests

**Files:**
- Modify: `tests/test_heat_flow/test_factories.py`
- Modify: `tests/test_heat_flow/test_models.py`
- Modify: `tests/test_ghfdb/test_models.py`
- Modify: `tests/test_ghfdb/test_schema_mapping.py`

**Step 1: Update `test_factories.py`**

- Remove `SurfaceHeatFlowFactory` from imports (~L11)
- Remove `test_surface_heat_flow_factory_fields` test method (~L68-77)
- Remove `SurfaceHeatFlowFactory()` calls from `test_all_factories_can_create_instances` and `test_all_factories_can_build_instances`
- Remove `test_factories_with_relationships` test (~L127-135) — it creates children via `HeatFlowFactory(parent=surface_heat_flow)` which no longer works
- Remove `relevant_child` assertion from `test_heat_flow_factory_fields` (~L87)
- Remove `is_ghfdb` assertion from `test_surface_heat_flow_factory_fields`

**Step 2: Update `test_schema_mapping.py`**

- Update `test_ghfdb_field_heat_flow_value_accessor_path` (~L127-161) — change `SurfaceHeatFlow` references to `ParentHeatFlow`
- Update import from `ghfdb.models` to use `ParentHeatFlow` instead of `SurfaceHeatFlow`

**Step 3: Update `test_models.py` (ghfdb)**

Add tests for new `ParentHeatFlow` behavior:
- Test one-parent-per-site constraint in `save()`
- Test `ParentChildRelation` unique constraint on `child`
- Test `get_quality` method with through model

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: update tests for GHFDB app separation

- Remove SurfaceHeatFlow factory tests
- Remove relevant_child assertions
- Update schema mapping tests for ParentHeatFlow
- Add ParentHeatFlow constraint tests"
```

---

### Task 12: Generate and run migrations

**Files:**
- Create: `project/heat_flow/migrations/XXXX_remove_parent_structure.py` (auto-generated)
- Create: `project/ghfdb/migrations/XXXX_update_parent_structure.py` (auto-generated)

**Step 1: Generate migrations**

```bash
poetry run python manage.py makemigrations heat_flow ghfdb
```

Expected output: Django should detect:
- Removal of `SurfaceHeatFlow` model
- Removal of `parent` FK from `HeatFlow`
- Removal of `relevant_child` from `HeatFlow`
- Changes to `ParentChildRelation.child` (unique=True)
- Removal of duplicate `HeatFlowSite` from ghfdb

**Step 2: Apply migrations on clean database**

```bash
poetry run python manage.py migrate
```

Expected: All migrations apply cleanly (no data to preserve).

**Step 3: Verify migration state**

```bash
poetry run python manage.py showmigrations heat_flow ghfdb
```

All migrations should show `[X]`.

**Step 4: Commit**

```bash
git add project/heat_flow/migrations/ project/ghfdb/migrations/
git commit -m "chore: add migrations for GHFDB app separation"
```

---

### Task 13: Run full test suite and fix remaining issues

**Step 1: Run tests**

```bash
poetry run pytest --tb=short
```

**Step 2: Fix any remaining import errors or broken references**

Search the full codebase for any remaining references to:
- `SurfaceHeatFlow`
- `relevant_child` (on HeatFlow)
- `HeatFlow.parent` (the old FK)

```bash
grep -r "SurfaceHeatFlow" project/ tests/ --include="*.py"
grep -r "relevant_child" project/ tests/ --include="*.py"
```

Fix any remaining references found.

**Step 3: Run linter**

```bash
poetry run ruff check project/ tests/
```

Fix any linting issues.

**Step 4: Commit any remaining fixes**

```bash
git add -A
git commit -m "fix: resolve remaining references from GHFDB separation"
```

---

### Task 14: Update documentation

**Files:**
- Modify: `docs/ghfdb_fields.md`
- Modify: `docs/field_map.csv`
- Modify: `docs/data_models/measurements.md` (if it has autodjango-model directive for SurfaceHeatFlow)

**Step 1: Update field mapping documentation**

In `docs/ghfdb_fields.md`, update all rows that reference `SurfaceHeatFlow` to reference `ParentHeatFlow` in the ghfdb app.

**Step 2: Update field_map.csv**

Update `heat_flow_surfaceheatflow` table references to the new ghfdb table name.

**Step 3: Commit**

```bash
git add docs/
git commit -m "docs: update field mapping for GHFDB app separation"
```

---

## Task Summary

| # | Task | Primary Files | Estimated Complexity |
|---|------|---------------|---------------------|
| 1 | Remove parent FK + relevant_child from HeatFlow | `models/measurements.py` | Low |
| 2 | Remove SurfaceHeatFlow model | `models/measurements.py`, `__init__.py` | Low |
| 3 | Update ghfdb.ParentHeatFlow | `ghfdb/models.py` | Medium |
| 4 | Update heat_flow admin | `heat_flow/admin.py` | Low |
| 5 | Add ghfdb admin | `ghfdb/admin.py` | Low |
| 6 | Update heat_flow config | `heat_flow/config.py` | Low |
| 7 | Update heat_flow tables | `heat_flow/tables.py` | Low |
| 8 | Update heat_flow factories | `heat_flow/factories.py` | Low |
| 9 | Update heat_flow utils | `heat_flow/utils.py` | Medium |
| 10 | Update ghfdb resources | `ghfdb/resources.py` | High |
| 11 | Update tests | `tests/test_heat_flow/`, `tests/test_ghfdb/` | Medium |
| 12 | Generate & apply migrations | auto-generated | Low |
| 13 | Full test suite + cleanup | cross-cutting | Medium |
| 14 | Update documentation | `docs/` | Low |

**Execution order:** Tasks 1–2 must be done first (model changes). Tasks 3–11 can be done in any order but are listed in a logical sequence. Task 12 (migrations) must come after all model changes. Task 13 is final validation. Task 14 can be done any time after Task 12.

**Total estimated tasks:** 14 tasks, ~30-40 individual steps
