# GHFDB App Separation Design

**Date:** 2026-02-05  
**Status:** Approved  
**Authors:** Design discussion with project team

## Context

The current database structure conflates two conceptually distinct entities:

1. **Child heat flow** — actual scientific measurements of heat flow, thermal conductivity, and thermal gradient collected over depth intervals at geographic sites. This is what researchers measure and report.

2. **Parent heat flow** — an administrative construct specific to the Global Heat Flow Database (GHFDB) used by database curators to represent a canonical/representative heat flow value for each site after reviewing all available child measurements.

The existing implementation has parent heat flow spread across two locations:
- `heat_flow.SurfaceHeatFlow` model with `HeatFlow.parent` FK pointing to it
- `ghfdb.ParentHeatFlow` model with M2M to `HeatFlow` via `ParentChildRelation`

Additionally, `HeatFlow` has a `relevant_child` field that is GHFDB-specific (indicating whether a child was used in parent calculation).

## Problem Statement

**The heat_flow app should be domain-focused and reusable by any researcher measuring heat flow, independent of the GHFDB administrative layer.**

Current issues:
- Parent heat flow logic is split between two apps
- `heat_flow.HeatFlow` has GHFDB-specific fields (`relevant_child`)
- `heat_flow.HeatFlow` has FK to parent, coupling it to GHFDB concepts
- Unclear separation between scientific measurement models and GHFDB administrative models

## Goals

1. **Decouple heat_flow from ghfdb** — heat_flow should have zero knowledge of GHFDB parent structures
2. **Single source of truth** — one clear parent heat flow model in the ghfdb app
3. **Clean domain model** — heat_flow focuses purely on scientific measurements
4. **Maintain data integrity** — enforce one parent per site, one parent per child
5. **Preserve FairDM integration** — continue using FairDM's Sample/Measurement hierarchy where appropriate
6. **Performance** — efficient queries for GHFDB data product generation

## Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      heat_flow app                          │
│              (reusable, domain-focused)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HeatFlowSite (Borehole/Sample)                            │
│  ├─ location, coordinates, depth                           │
│  ├─ environment, explo_method, explo_purpose               │
│  └─ country, region, continent, domain*                    │
│                                                             │
│  HeatFlow (Measurement)                                    │
│  ├─ value, uncertainty, method                             │
│  ├─ probe fields (penetration, type, length, tilt)        │
│  ├─ correction flags (IS, T, S, E, TOPO, PAL, etc.)       │
│  ├─ thermal_gradient (OneToOne)                            │
│  ├─ thermal_conductivity (OneToOne)                        │
│  └─ quality scores (U_score, M_score)                      │
│                                                             │
│  * These fields are temporary placeholders until FairDM    │
│    implements automatic geographic tagging                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ depends on (one-directional)
                            │
┌─────────────────────────────────────────────────────────────┐
│                       ghfdb app                             │
│            (GHFDB-specific administrative layer)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ParentHeatFlow (Measurement)                              │
│  ├─ sample → FK to HeatFlowSite (via FairDM)              │
│  ├─ value, uncertainty, corr_HP_flag                       │
│  ├─ comment, is_ghfdb                                      │
│  ├─ save() enforces max one parent per site               │
│  └─ children → M2M to HeatFlow via ParentChildRelation     │
│                                                             │
│  ParentChildRelation (through model)                       │
│  ├─ parent → FK to ParentHeatFlow                          │
│  ├─ child → FK to HeatFlow (unique=True)                  │
│  └─ is_relevant → whether child used in parent calc        │
│                                                             │
│  GHFDBRelease                                              │
│  └─ version, release_date, description, file               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Model Specifications

#### heat_flow.HeatFlowSite

**No changes required** — already clean as a FairDM Borehole/Sample.

Fields:
- Inherited from Borehole: `location`, `coordinates`, `depth`, `length`, `vertical_depth`
- Domain-specific: `environment`, `explo_method`, `explo_purpose`
- Temporary GHFDB fields: `country`, `region`, `continent`, `domain` (will be removed when FairDM implements auto-tagging)

#### heat_flow.HeatFlow

**Changes:**
- **REMOVE**: `parent = ForeignKey(SurfaceHeatFlow)` — breaks coupling to parent structure
- **REMOVE**: `relevant_child = BooleanField()` — GHFDB-specific, moves to through model

**Keeps:**
- All measurement data fields
- All probe sensing fields
- All correction flags
- Relationships to ThermalGradient and IntervalConductivity
- Quality scores (U_score, M_score)

This makes `HeatFlow` a pure scientific measurement model with no GHFDB knowledge.

#### heat_flow.SurfaceHeatFlow

**REMOVE ENTIRELY** — replaced by `ghfdb.ParentHeatFlow`.

All references to `SurfaceHeatFlow` throughout the codebase must be updated to use `ghfdb.ParentHeatFlow`.

#### ghfdb.ParentHeatFlow

**Inherits from:** `fairdm.core.models.Measurement`

**Fields:**
```python
class ParentHeatFlow(Measurement):
    # sample FK to HeatFlowSite inherited from Measurement base class
    
    value = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("heat flow"),
        help_text=_("Representative heat-flow density for this site..."),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_("Uncertainty of the representative heat-flow value..."),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    
    corr_HP_flag = models.BooleanField(
        verbose_name=_("HP correction flag"),
        help_text=_("Whether heat production corrections were applied..."),
        null=True,
        blank=True,
        default=None,
    )
    
    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("Curator comments on parent heat flow determination..."),
        blank=True,
        null=True,
    )
    
    is_ghfdb = models.BooleanField(
        verbose_name=_("GHFDB flag"),
        help_text=_("Whether this entry is part of official GHFDB release..."),
        default=True,
    )
    
    children = models.ManyToManyField(
        "heat_flow.HeatFlow",
        through="ghfdb.ParentChildRelation",
        related_name="ghfdb_parents",  # Note: plural to indicate M2M semantics
        verbose_name=_("child heat flows"),
        help_text=_("Child measurements for this site..."),
    )
```

**Constraints enforced in `save()` method:**
```python
def save(self, *args, **kwargs):
    # Enforce one parent per site
    if self.sample:
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

**Quality calculation method:**
```python
def get_quality(self):
    """
    Calculate parent quality score from relevant children.
    
    From Fuchs et al 2023 Section 3.4:
    - If one child: inherit its score
    - If multiple children: inherit poorest score of relevant children
    """
    relevant_children = self.children.filter(
        parentchildrelation__is_relevant=True
    )
    
    count = relevant_children.count()
    
    if count == 0:
        return None
    elif count == 1:
        return relevant_children.first().get_quality()
    else:
        return relevant_children.order_by("quality").first().get_quality()
```

#### ghfdb.ParentChildRelation

**Through model for ParentHeatFlow.children M2M:**

```python
class ParentChildRelation(models.Model):
    parent = models.ForeignKey(
        "ghfdb.ParentHeatFlow",
        on_delete=models.CASCADE,
        verbose_name=_("parent heat flow"),
    )
    
    child = models.ForeignKey(
        "heat_flow.HeatFlow",
        on_delete=models.CASCADE,
        verbose_name=_("child heat flow"),
        unique=True,  # CRITICAL: enforces one parent per child at DB level
    )
    
    is_relevant = models.BooleanField(
        verbose_name=_("is relevant"),
        help_text=_(
            "Whether this child was used in calculating the parent value. "
            "Curators mark children as relevant after reviewing quality and "
            "corrections. Irrelevant children are kept for historical record."
        ),
        default=False,
    )
    
    class Meta:
        verbose_name = _("Parent-Child Heat Flow Relation")
        verbose_name_plural = _("Parent-Child Heat Flow Relations")
        unique_together = ("parent", "child")  # Belt-and-suspenders with unique=True
```

**Why M2M instead of FK on child?**
- Maintains decoupling — heat_flow app has no knowledge of ghfdb
- The `unique=True` on child enforces one-parent-per-child at DB level
- Through model provides GHFDB-specific relationship metadata (`is_relevant`)
- Future-proof for potential multi-parent scenarios (unlikely but possible)

### Data Flow & Relationships

#### Creating a new parent heat flow:

```python
# 1. Create or get the site
site = HeatFlowSite.objects.create(
    location=point,
    environment="continental",
    # ... other site fields
)

# 2. Create parent heat flow
parent = ParentHeatFlow.objects.create(
    sample=site,  # FairDM's sample FK
    value=65.5,   # mW/m²
    uncertainty=5.2,
    comment="Mean of 3 corrected children, depths 500-1500m",
)

# 3. Link children and mark relevance
child1 = HeatFlow.objects.get(...)
child2 = HeatFlow.objects.get(...)
child3 = HeatFlow.objects.get(...)

ParentChildRelation.objects.create(parent=parent, child=child1, is_relevant=True)
ParentChildRelation.objects.create(parent=parent, child=child2, is_relevant=True)
ParentChildRelation.objects.create(parent=parent, child=child3, is_relevant=False)  # historical
```

#### Querying GHFDB data product:

```python
# Efficient query with all related data
parents = ParentHeatFlow.objects.filter(
    is_ghfdb=True
).select_related(
    'sample',  # HeatFlowSite with coordinates
    'sample__location',  # GIS point data
).prefetch_related(
    'children',  # All children via M2M
    'children__thermal_gradient',
    'children__thermal_conductivity',
)

# Access pattern
for parent in parents:
    site = parent.sample
    coords = site.location.coords
    
    # Get only relevant children
    relevant = parent.children.filter(
        parentchildrelation__is_relevant=True
    )
    
    # Or check via through model
    for relation in parent.parentchildrelation_set.all():
        if relation.is_relevant:
            child = relation.child
            # ... process child
```

### Database Performance Considerations

**Schema impact:**
- ParentHeatFlow: ~100k–200k rows (one per site)
- ParentChildRelation: ~250k–1M rows (2–5 children per parent average)
- HeatFlow: ~250k–1M rows (unchanged)

**Query performance:**
- `select_related('sample')` — single JOIN, fast
- `prefetch_related('children')` — one extra query for all children, then Python joins
- `unique=True` on ParentChildRelation.child — automatic DB index, fast constraint checks
- No polymorphic inheritance on ParentHeatFlow — direct table access

**Expected query times (on indexed PostgreSQL):**
- Fetch single parent with all children: <10ms
- Fetch all GHFDB parents for export: <1s with proper prefetching
- Filter parents by site country/region: <50ms with indexes

**Indexes to add:**
```python
class ParentHeatFlow(Measurement):
    class Meta:
        indexes = [
            models.Index(fields=['is_ghfdb']),
            models.Index(fields=['value']),  # for range queries
        ]

class ParentChildRelation(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['is_relevant']),
            models.Index(fields=['parent', 'is_relevant']),  # composite
        ]
```

## Migration Strategy

Since there's no production data to preserve and no backward compatibility requirements, we can do a clean-break migration.

### Step 1: Model changes

1. **Remove from heat_flow.HeatFlow:**
   - `parent` FK
   - `relevant_child` field

2. **Remove entirely:**
   - `heat_flow.SurfaceHeatFlow` model

3. **Update ghfdb.ParentHeatFlow:**
   - Ensure it inherits from `Measurement`
   - Add `save()` validation
   - Update relationships

4. **Update ghfdb.ParentChildRelation:**
   - Add `unique=True` to `child` FK
   - Rename `is_relevant` if needed (currently both exist)

### Step 2: Code updates

- Admin classes: Move `SurfaceHeatFlowAdmin` logic to `ParentHeatFlowAdmin` in ghfdb
- Views: Update any references to `SurfaceHeatFlow`
- Serializers: Update DRF serializers if used
- Tables: Update django-tables2 classes
- Filters: Update django-filter filtersets
- Forms: Update ModelForms
- Tests: Update all test cases

### Step 3: Migration file structure

```
migrations/
├── heat_flow/
│   └── 00XX_remove_parent_structure.py
│       - RemoveField(model='heatflow', name='parent')
│       - RemoveField(model='heatflow', name='relevant_child')
│       - DeleteModel(name='SurfaceHeatFlow')
│
└── ghfdb/
    └── 00YY_update_parent_structure.py
        - AddField(model='parentchildrelation', name='unique', unique=True)
        - Add indexes to ParentHeatFlow
        - Add indexes to ParentChildRelation
```

Order: Run heat_flow migration first, then ghfdb migration.

### Step 4: Documentation updates

- Update field mapping documentation (`docs/ghfdb_fields.md`)
- Update data model documentation
- Update developer guides
- Update any API documentation

## Testing Strategy

### Unit Tests

1. **ParentHeatFlow.save() validation:**
   - Test that creating two parents for same site raises ValidationError
   - Test that updating existing parent works
   - Test that creating parents for different sites works

2. **ParentChildRelation uniqueness:**
   - Test that assigning child to two parents raises IntegrityError
   - Test that updating is_relevant works
   - Test that deleting relation works

3. **Quality score calculation:**
   - Test single relevant child: parent inherits child score
   - Test multiple relevant children: parent inherits worst score
   - Test no relevant children: parent quality is None

### Integration Tests

1. **GHFDB data product generation:**
   - Create sites, parents, and children
   - Query all GHFDB parents with prefetch
   - Verify correct data structure
   - Verify query count (should be ~3 queries with prefetch)

2. **Admin interface:**
   - Test creating parent via admin
   - Test inline child relation management
   - Test validation errors display correctly

3. **heat_flow app independence:**
   - Verify HeatFlow can be created without any GHFDB models
   - Verify queries on HeatFlow don't reference ghfdb tables
   - Verify heat_flow models have no imports from ghfdb

## Rollout Plan

1. **Create feature branch** from main
2. **Implement model changes** (heat_flow first, then ghfdb)
3. **Generate and test migrations** on clean database
4. **Update all code references** (admin, views, serializers, etc.)
5. **Update tests** (unit and integration)
6. **Update documentation**
7. **Code review** with focus on:
   - Decoupling verification
   - Performance of queries
   - Admin usability
8. **Merge to main** once approved

## Future Considerations

### Automatic geographic tagging

When FairDM implements automatic geo-tagging on Location/Point models:
- Remove `country`, `region`, `continent`, `domain` from HeatFlowSite
- Access these via `site.location.country` etc.
- Update queries to use related fields

### Release versioning

If GHFDB needs to track parent values across multiple releases:
- Add `release = FK(GHFDBRelease)` to ParentHeatFlow
- Remove one-parent-per-site constraint
- Add constraint: unique_together on (site, release)
- Update queries to filter by current release

### Audit logging

To track changes to parent values over time:
- Add django-simple-history or similar
- Track changes to ParentHeatFlow value/uncertainty
- Track changes to ParentChildRelation.is_relevant
- Provide admin view of change history

## Questions & Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| FK or M2M for parent-child? | M2M with unique constraint | Maintains decoupling, allows through model metadata |
| Inherit from Measurement or standalone? | Inherit from Measurement | Gets sample FK for free, participates in FairDM ecosystem |
| Where to enforce one-parent-per-site? | Application level (save method) | Allows flexibility for future multi-release scenarios |
| Where to enforce one-parent-per-child? | Database level (unique=True) | Critical integrity constraint, should be in DB |
| Move country/region to ParentHeatFlow? | No, keep on HeatFlowSite temporarily | Will be removed when FairDM auto-tagging implemented |
| Preserve SurfaceHeatFlow? | No, remove entirely | Single source of truth in ghfdb.ParentHeatFlow |

## References

- Team discussion transcript: `questions.md`
- Fuchs et al. (2021): "A new database structure for the IHFC Global Heat Flow Database"
- Fuchs et al. (2023): "Quality-assurance of heat-flow data: The new structure and evaluation scheme"
- FairDM Core Data Model: Framework documentation
- Project constitution: `.specify/memory/constitution.md`
