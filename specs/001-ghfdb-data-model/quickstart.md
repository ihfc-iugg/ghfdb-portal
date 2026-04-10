# Quickstart: GHFDB Normalized Relational Data Model

**Phase 1 Output** | **Feature**: 001-ghfdb-data-model

---

## Prerequisites

- Python ≥3.13
- Poetry (package manager)
- FairDM framework (`fairdm`, `fairdm-geo`) installed
- GHFDB portal repository cloned and configured

## Setup

```bash
# Install dependencies
poetry install

# Apply migrations
poetry run python manage.py migrate

# Verify system checks pass
poetry run python manage.py check
```

## Creating Data via the ORM

### Full Object Graph: Site → Interval → Child Heat Flow

```python
from heat_flow.models import (
    HeatFlowSite,
    HeatFlowInterval,
    ParentHeatFlow,
    HeatFlow,
    ThermalGradient,
    IntervalConductivity,
    ProbeMetadata,
    HeatFlowCorrection,
)

# 1. Create a site (Sample)
site = HeatFlowSite.objects.create(
    name="KTB-Oberpfalz",
    environment="onshore_continental",
    country="Germany",
    continent="Europe",
)

# 2. Create the parent heat flow (Measurement → Site)
parent = ParentHeatFlow.objects.create(
    sample=site,
    value=51.0,  # mW/m²
    uncertainty=3.0,
    corr_HP_flag=True,
    comment="Deep continental borehole",
)

# 3. Create a depth interval (Sample → Site)
interval = HeatFlowInterval.objects.create(
    sample=site,
    top=0,     # m
    bottom=500,  # m
)

# 4. Create sub-measurements (Measurement → Interval)
gradient = ThermalGradient.objects.create(
    sample=interval,
    value=25.0,   # K/km
    uncertainty=2.0,
    number=15,
)

conductivity = IntervalConductivity.objects.create(
    sample=interval,
    value=2.5,   # W/mK
    uncertainty=0.3,
    number=8,
)

# 5. Create child heat flow (Measurement → Interval, FK → Parent, FK → Gradient/Conductivity)
child = HeatFlow.objects.create(
    sample=interval,
    parent=parent,
    value=50.5,  # mW/m²
    uncertainty=4.0,
    thermal_gradient=gradient,
    thermal_conductivity=conductivity,
    is_relevant=True,
    expedition="KTB Deep Drilling Program",
)

# 6. Attach corrections
HeatFlowCorrection.objects.create(
    heat_flow=child,
    correction_type="T",
    status="present_corrected",
)
HeatFlowCorrection.objects.create(
    heat_flow=child,
    correction_type="PAL",
    status="present_corrected",
)

# 7. (Optional) Attach probe metadata to the interval
probe = ProbeMetadata.objects.create(
    interval=interval,
    penetration=3.5,  # m
    length=5.0,
    tilt=2.0,
)
```

### Querying Relationships

```python
# All children of a parent
parent.children.all()

# Relevant children only
parent.children.filter(is_relevant=True)

# Corrections for a child
child.corrections.all()

# Probe metadata for an interval
interval.probe_metadata  # raises RelatedObjectDoesNotExist if none

# Check if a child is from a probe
child.is_probe  # True if interval has probe_metadata
```

## Using Factories in Tests

### Factory Philosophy

All factory classes in this project follow the **minimal, flat** convention:

- Each factory provides sensible defaults for the model's own scalar and choice fields.
- A factory MAY include **one level** of `SubFactory` where a non-nullable FK is present (e.g., `HeatFlowIntervalFactory.sample = SubFactory(HeatFlowSiteFactory)`).
- Factories do **not** create deep chains, M2M records, or second-level related objects through `SubFactory` or `@factory.post_generation` hooks.
- Complex multi-model object graphs (e.g., `site → interval → ThermalGradient + IntervalConductivity → HeatFlow → ParentHeatFlow`) are constructed **explicitly in pytest fixtures** (in `conftest.py`), not inside factory definitions.

This keeps factory output predictable, tests surgically isolated, and avoids unexpected DB writes.

### Simple Factory Usage

```python
import pytest
from heat_flow.factories import (
    HeatFlowSiteFactory,
    HeatFlowIntervalFactory,
    HeatFlowFactory,
    ThermalGradientFactory,
    IntervalConductivityFactory,
    ProbeMetadataFactory,
)

@pytest.mark.django_db
def test_full_object_graph():
    site = HeatFlowSiteFactory()
    assert site.pk is not None

    interval = HeatFlowIntervalFactory(sample=site)
    gradient = ThermalGradientFactory(sample=interval)
    conductivity = IntervalConductivityFactory(sample=interval)

    child = HeatFlowFactory(
        sample=interval,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
    )
    assert child.pk is not None
    assert child.thermal_gradient == gradient

@pytest.mark.django_db
def test_probe_metadata():
    interval = HeatFlowIntervalFactory()
    probe = ProbeMetadataFactory(interval=interval)
    assert interval.probe_metadata == probe
```

### Complex Graph via pytest Fixture

For tests that need the full site → interval → child hierarchy, define a reusable fixture in `conftest.py` rather than burying the construction logic in a factory:

```python
# tests/conftest.py
import pytest
from heat_flow.factories import (
    HeatFlowSiteFactory,
    HeatFlowIntervalFactory,
    ParentHeatFlowFactory,
    ThermalGradientFactory,
    IntervalConductivityFactory,
    HeatFlowFactory,
)

@pytest.fixture
def full_graph(db):
    site = HeatFlowSiteFactory()
    parent = ParentHeatFlowFactory(sample=site)
    interval = HeatFlowIntervalFactory(sample=site)
    gradient = ThermalGradientFactory(sample=interval)
    conductivity = IntervalConductivityFactory(sample=interval)
    child = HeatFlowFactory(
        sample=interval,
        parent=parent,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
    )
    return {"site": site, "parent": parent, "interval": interval,
            "gradient": gradient, "conductivity": conductivity, "child": child}
```

## Running Tests

```bash
# Run all heat_flow tests
poetry run pytest tests/test_heat_flow/

# Run with verbose output
poetry run pytest tests/test_heat_flow/ -v

# Run specific test file
poetry run pytest tests/test_heat_flow/test_models.py
```

## FairDM Registry Verification

```python
import fairdm
from heat_flow.models import (
    HeatFlowSite, HeatFlowInterval, ParentHeatFlow, HeatFlow,
    ThermalGradient, IntervalConductivity,
)

# Verify all six Measurement/Sample subclasses are registered
for model in [HeatFlowSite, HeatFlowInterval, ParentHeatFlow, HeatFlow,
              ThermalGradient, IntervalConductivity]:
    config = fairdm.registry.get_config(model)
    assert config is not None, f"{model.__name__} not registered"
    print(f"{model.__name__}: {config.description[:50]}...")
```
