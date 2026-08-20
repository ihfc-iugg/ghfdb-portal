# Research — 001 heat flow data model

What had to be established before the open tasks could be planned. Every claim below was checked
against the installed framework source or verified at runtime, and cites where.

Framework paths are relative to the installed `fairdm`, `research_vocabs` and `fairdm_geo` packages.

## R1 — How to enforce one site per coordinate pair

**Question**: the specification requires the rule to hold on every write path. Where does it go?

**Findings**

`Point` already constrains its coordinates: `unique_together = ("x", "y")`
(`fairdm/contrib/location/models.py:40`). A coordinate pair therefore resolves to exactly one point
record, and the framework's own `PointFactory` uses `django_get_or_create = ("x", "y")`
(`fairdm/factories/core.py:730`). The import already calls `get_or_create` on the pair
(`project/ghfdb/resources/parent.py:212`).

So the rule reduces to `location` being unique among sites, and does **not** require reasoning about
coordinate values.

`location` is declared once, on `Sample`, nullable, `on_delete=PROTECT`
(`fairdm/core/sample/models.py:111`). Because it lives on the polymorphic base table, a
`UniqueConstraint` in `HeatFlowSite.Meta` is not declarable — the same obstacle as the published
value's one-per-site rule, recorded as D2 in `decisions.md`.

`HeatFlowSite.objects.filter(...)` is correctly scoped to `HeatFlowSite` rows. `Sample` declares
`objects = PolymorphicManager.from_queryset(SampleQuerySet)()`
(`fairdm/core/sample/models.py:134`), and a polymorphic manager on a child model queries that
child's own table. So the uniqueness lookup does not need a type filter.

**The decisive finding**: neither base class calls `full_clean()` from `save()`, and Django never
does automatically. A rule implemented only in `clean()` is bypassed by `Model.objects.create()`,
by a bare `save()`, and by every factory. The framework treats this as a known hazard and works
around it in two places — `VocabularyGuardedSave` overrides `save()`
(`fairdm/core/measurement/models.py:189`), and `Sample` carries a `pre_save` signal
(`fairdm/core/sample/models.py:305`) — precisely because a manager's `create()` reaches the database
without calling `clean()`.

**Decision**: enforce in `save()`, and also in `clean()`.

`save()` is the guarantee. It is the pattern already used one file away for the parent's
one-per-site rule (`project/heat_flow/models/parent.py:217`), so the two rules read alike, and it
covers `objects.create()` and the factories.

`clean()` is what makes the failure legible. Forms and the admin call `full_clean()` before saving,
so without it a curator entering a duplicate site through the admin gets a server error rather than
a field error.

Neither fires on `bulk_create` or a queryset `update()`. Neither does a `pre_save` signal, so that
alternative buys nothing here, and the project contains no bulk write path — checked, and recorded
as D2.

**Also to resolve**: the import has two notions of site identity. `_get_or_create_site`
(`project/ghfdb/resources/parent.py:171`) looks a site up by borrowed identifier when the row
carries one and by coordinates when it does not, so the two paths can disagree and the first
contradicts the rule. Issue #143 raised this alongside the constraint, and the story carries it.

## R2 — Controlled vocabulary fields in factories

**Question**: every vocabulary declaration in `factories.py` is commented out. What does it take to
populate them?

**Findings**

Two field types, and they behave differently.

`ConceptField` stores a plain string — it subclasses `CharField`
(`research_vocabs/fields.py:151`). `FuzzyChoice(Model.<field>_vocab.values)` is correct and is
already in use (`project/heat_flow/factories.py:21`).

`ConceptManyToManyField` is a real many-to-many to `research_vocabs.Concept`
(`research_vocabs/fields.py:169`), so it needs database rows. `Concept` has a non-nullable foreign
key to `Vocabulary` and `unique_together = ("vocabulary", "name")`
(`research_vocabs/models.py:126`), so the concepts must exist before a factory can attach them.

`<field>_vocab` is set on the model class by the field's `contribute_to_class`
(`research_vocabs/fields.py:87` for the scalar field, `:200` for the related ones) and is the
instantiated vocabulary, whose `.values` is the list of concept names (`research_vocabs/core.py:182`
with `:259`).

`Concept.preload()` creates the vocabulary and its concepts from the registry
(`research_vocabs/models.py:139`), and `Concept.get_for_vocabulary()` scopes a queryset to one
vocabulary, accepting the vocabulary class (`research_vocabs/models.py:166`).

**The reason the declarations are commented out** is visible in the test layout rather than the
factories. `tests/test_ghfdb/conftest.py:17` carries an autouse fixture calling `Concept.preload()`.
`tests/test_heat_flow/conftest.py` carries no equivalent, so no concept row exists in any
`heat_flow` test, and any factory attaching one would fail. The one test that does exercise a
vocabulary many-to-many builds its vocabulary and concept by hand
(`tests/test_heat_flow/test_models.py:48`).

**Decision**: preload concepts for the `heat_flow` tests the same way the extraction tests already
do, then set many-to-many fields through `post_generation` hooks — a many-to-many cannot be
assigned before the row exists. Note `RelatedConceptMixin` forces `related_name="+"`
(`research_vocabs/fields.py:190`), so there is no reverse accessor from a concept.

No working example of a concept many-to-many factory exists in any of the three packages to copy
from. The nearest idiom is `fairdm/core/abstract.py:83`, which filters concepts by vocabulary name
and calls `.set()`.

## R3 — What the factory bases provide

`SampleFactory` and `MeasurementFactory` are abstract and live in `fairdm/factories/core.py:476`
and `:610`. Both supply `name` and a `dataset` via sub-factory. `SampleFactory` also supplies
`local_id`, `status` and a null `location`. **`MeasurementFactory` supplies no `sample`**, and
`Measurement.sample` is non-nullable (`fairdm/core/measurement/models.py:70`), so every measurement
factory must supply one — which the app's factories already do.

Both carry opt-in `descriptions` and `dates` hooks that do nothing unless passed a count.

## R4 — What the registry actually reads

**Question**: several configuration attributes in this app are not in the framework's vocabulary.
Which, exactly, and what is the real contract?

**Findings**

`ModelConfiguration` recognises a fixed set: `model`, `metadata`, `fields`, `exclude`, a
per-component field list and a per-component class for each of six components, `display_name` and
`description` (`fairdm/registry/config.py:195`–`:245`). The component table is at `:111`.

Anything else set on a configuration is set and never read. `ModelConfiguration` has no metaclass
and no `__init_subclass__`, and `_OVERRIDABLE` guards only keyword arguments to `__init__`.

The description, authority, keywords, repository link and citation belong on `ModelMetadata`
(`fairdm/registry/config.py:78`), assigned to `metadata` (`:203`).

Components are generated when none is supplied — `_component_class`
(`fairdm/registry/config.py:435`) falls back to a factory, resolving fields from the component's own
list, then `fields`, then the model's defaults (`:418`). Supplying both a class and a field list for
one component is refused (`:291`).

**Verified at runtime**, not only read: every one of the six registered models returns
`ModelMetadata(description='', authority=None, keywords=[], repository_url='', citation=None,
maintainer='', maintainer_email='')`.

**Consequences for the plan**

- The shared base's authority, citation and repository link reach nothing. `description` is a
  recognised attribute and is read as the configuration's own; only `ModelMetadata.description` is
  empty. Do not delete the class-level descriptions.
- Exactly three attributes are inert: `filterset_options` (on three configurations), `fieldsets`
  (on one) and `primary_data_fields` (on four). Those models get a generated filter set from
  `fields` instead. The supported spellings are `filterset_fields` or `filterset_class`.
- `admin_list_display` looks equally unfamiliar and is **not** inert — it is the admin component's
  field list (`fairdm/registry/config.py:120`). Deleting it would silently change four changelists.
- Requiring a hand-written filter set and table per model, as the approved specification did, would
  replace working generated components with code to maintain. Recorded as D8 and the specification
  amended.
- `ThermalConductivityTable` is defined at `project/heat_flow/tables.py:143` and referenced by
  nothing.

## R5 — Rendering the diagram

**Question**: what does it take for the diagram to reach a reader as a diagram?

**Findings**

No Mermaid extension is configured. The project's `docs/conf.py:39` adds `sphinx_design` and
`sphinx_exec_code` to the framework's default list (`fairdm_docs/conf.py:378`), which carries
`myst_parser` and no Mermaid renderer. MyST alone emits a highlighted code block.

**Verified by building the documentation**: the existing 458-line diagram renders as
`<div class="highlight-mermaid">` — syntax-highlighted source, not a diagram.

**The build itself is not broken.** Issue #124 reports `ModuleNotFoundError: No module named 'docs'`;
that no longer reproduces, having been fixed in `dc78c63`. A full build succeeds with 71 warnings.
What remains of #124 is the workflow condition that has never let the build run in CI, which is a
workflow file and outside this feature.

Graphviz is not installed, so the `.dot` sources beside the diagram cannot be rebuilt and the
committed images generated from them are frozen against a schema that has since changed.

**Decision**: add `sphinxcontrib-mermaid` to the documentation dependencies and the extension list.
The rendering test asserts against built output rather than source, since the failure being guarded
against is precisely a source file that is valid and never rendered.

## R6 — Checking the field map against the code

**Question**: what is the map checked against, and how?

**Findings**

`project/ghfdb/constants.py` defines `PARENT_COLUMNS`, `CHILD_COLUMNS` and `META_FIELDS`, with
`GHFDB_COLUMN_ORDER` derived as their concatenation. Tests already pin that derivation and its
casing, and they pass.

`docs/ghfdb_fields.md` is a set of pipe tables keyed by published column name, carrying the
database table, the model it is reached from, the accessor and the model that declares it. Names are
markdown-escaped, so a parser must unescape before comparing.

The map is already stale in at least one row: `ID` maps to `local_id` on the child, and that field
was replaced by `ghfdb_id` in migration `0011`.

**This is a different mapping from the one issue #122 covers.** That issue is about published
columns against import and export *resource* fields, and about a metadata file's vocabulary. This
map is published columns against *model* fields. The two do not depend on each other, and this
feature does not touch the resources.

**Decision**: parse the map's tables, assert every canonical column appears, and resolve each
mapping's model and accessor against the real model. Fourteen tests in the extraction suite are
quarantined as strict expected failures pointing at #122; nothing here touches them.
