# Decisions — 010 heat flow API representations

Decisions taken while specifying this feature, and why. Rationale too long for
[spec.md](spec.md) lives here. The maintainer handed this specification over without an intake
conversation, so every point below is a reading taken from the issue and the repository and
recorded for veto, not one he confirmed.

## D0 — Who can newly do what

A researcher scripting against the portal, or the map viewer, can read a heat flow site or
measurement through the API in one request, with the records it depends on, readable vocabulary
terms, stated units and the portal's quality scores. Today the same reader needs a request per
related record, cannot read a term or a unit from the response, and cannot get the scores at all.
That is a new way to work with the site, so this is a feature and not a change to an existing one.
No existing spec covers the relational model's own API shape: FS-006 covers the published
structure only.

## D1 — The interpretation the spec is built on

Issue #287 is read as: serve the six relational record types (sites, intervals, children, gradients,
conductivities, parents) in shapes designed for heat flow, for a consumer reading them. Four
properties come straight from the issue: related records arrive with the record, vocabulary terms
are readable, units are clear, and quality scores are present. Everything else in the spec is a
consequence of those four or one of the decisions below.

## D2 — Nesting goes one level, and lists stay lean

**Ambiguous:** "the related records they need without a request per record" sets no limit. A site
leads to a parent, intervals, children, and through each child to a gradient and a conductivity.

**Chosen:** a single record nests its directly related records whole and refers to anything further
away. A list carries what a page of that type is read for, and references for the rest. The one
deliberate exception is the site's single record, which carries the children made over each
interval. A site's children are what a reader of a site wants, and leaving them out would cost one
request per interval.

**Why defensible:** it is the rule FS-006 already applies (a determination links to its parent in a
list and nests it on its own route, FS-006 D3). A consumer meets one rule across the API, and a list
page does not grow by an order of magnitude.

## D3 — Writing is not part of this feature

**Ambiguous:** the framework's endpoints for these types accept writes, and the issue speaks only of
reading ("get each record in a shape").

**Chosen:** writing stays as it is today. What this feature adds is for reading. The values the
portal calculates (quality scores, quality codes, scheme revisions) and GHFDB identifiers are never
taken from a request.

**Why defensible:** the issue is about reading. Changing the write contract would be a second
feature. The rule against taking calculated values from outside is a standing constraint
(CONTEXT.md, "Quality is computed here"), not a new decision.

## D4 — A unit is stated in the record, in the canonical unit

**Ambiguous:** "units that are clear" could mean a unit in the schema only, a unit beside each
value, or conversion on request.

**Chosen:** each value is served in the canonical unit the portal stores it in, and the record
states that unit. The schema describes it too. Conversion is out of scope.

**Why defensible:** a record that states its own units can be read without the schema, which is the
FAIR reading of constitution article XI and the labelling rule of article XII. Conversion adds
nothing the canonical unit cannot already give.

## D5 — A vocabulary term carries a label and its identifier

**Chosen:** a term is given with its label and the identifier that defines it, and a many-valued
field gives each term as its own entry.

**Why defensible:** a label alone is readable but not resolvable, and an identifier alone is
resolvable but not readable. The framework already gives a record's keywords this way, so it is the
API's existing pattern. FS-006 gives labels only because the published structure fixes that shape.
These endpoints are not bound by it.

## D6 — Records placed at a site carry the site's coordinates

**Ambiguous:** the framework gives every sample and measurement a location, but in this portal only
a site holds one (ADR 0023). Left alone, every interval and measurement would arrive with an empty
location.

**Chosen:** an interval, child, gradient, conductivity or parent carries the coordinates of the site
it is placed at. They are read from the site, not stored again.

**Why defensible:** an unplaced record cannot be plotted or joined, which is the argument FS-006 D2
made for a determination carrying its site's coordinates. ADR 0023 is unchanged, since the site
stays the one record holding them.

## D7 — Nested records follow their own visibility

**Chosen:** a related record is served inside another only where the requester may read it on its
own route, and otherwise it is left out entirely.

**Why defensible:** a site and its intervals can sit in different datasets, as a parent and its
determination can. ADR 0021 settled this for the published structure, and a nested record must not
become a side door around it.

## D8 — Addresses and identifiers do not change

**Chosen:** each type keeps its current route and its current record identifier.

**Why defensible:** the framework derives a type's route from its plural name, and changing it
breaks every existing consumer. Nothing in the issue asks for new addresses.

## D9 — Corrections and probe metadata are not types of their own

**Chosen:** corrections are served inside the child they belong to, and probe metadata inside its
interval. Neither gets its own endpoint.

**Why defensible:** neither is registered with the framework as a sample or measurement type, and
neither means anything apart from its owner. The issue names six types, and these are not among
them.

## D10 — Boundary with the sibling features

The forms for these records (#286) and their overview pages (#288) are written in parallel and own
their own scope. The published-structure endpoints (FS-006) are not touched. This feature reads the
same records the overview pages show, but it shares no surface with them, and neither depends on the
other.

## D11 — FairDM version

The portal pins FairDM at `f69c9cb`. Its API at that commit already lets a project supply its own
serializer for a sample or measurement type, provided it builds on the framework's base serializer
for that kind. FairDM's main branch has moved on since (latest `2bebf29b`), but only to Django 6.0
and new development accounts, with nothing in its API or registry. This feature needs nothing from a
newer FairDM.

## D12 — No sketch

The feature changes no page a person looks at. Its output is API responses, which tests can assert
in full, so there is nothing for a sketch to settle.

## D13 — Re-read against the feature delivered since

FS-011 (the overview pages) merged after this specification was written. It changes the pages
and shares no surface with the API, as D10 expected. Nothing in this specification contradicts it.
Its `HeatFlowPage.split` rule for which related records a visitor may see is the one these
endpoints apply too.

**ADR:** none — a check of one specification against another, nothing to inherit

## D14 — A registration names a declared serializer

Each of the six registrations names its serializer with `serializer_class`, declared in
`project/heat_flow/serializers.py`, rather than one built inside `get_serializer_class()`
(research.md). Its `Meta.fields` keeps every writable field the generated serializer has today.

**ADR:** pending S5

## D15 — A list holds the summary, a single record the whole record

The full serializer's `many_init` builds a list from the type's summary serializer, and a schema
extension gives the list operation the summary's shape. The generated viewsets stay FairDM's own,
so paging, ordering, filtering and visibility are unchanged (FR-015).

**ADR:** pending S5

## D16 — Units are a `units` object beside plain numbers

A quantity is a plain number in its stored unit, and the record carries a `units` object naming
each quantity's unit in pint's compact form. An empty value is `null` and its unit is still stated
(spec US4 scenario 4). A `{magnitude, unit}` object per value would lose the unit exactly when the
value is empty.

**ADR:** pending S5

## D17 — The conductivity's declared unit is served as declared

`IntervalConductivity` declares `W/mK`, which a unit library reads as watts per millikelvin. The
stored numbers are right, because the whole portal uses the declaration consistently. Correcting
it touches the model, the import and the quality scheme, so it is an issue of its own, and the
API's unit text follows the declaration when it changes.

**ADR:** none — follows the model's own declaration, nothing new to inherit

## D18 — Undetermined grades are served as stored

`U_score` and `M_score` hold `Ux` and `Mx` when not determined, the scheme's own grades, and are
served as those codes (SC-005: every score served equals the stored one). Numeric scores not
determined are stored empty and served `null` (FR-012).

**ADR:** none — the stored value, served as it is

## D19 — Five of the six lists answered 500

The generated serializers map a quantity to a plain number field, which cannot read a pint
quantity, so every list but the site's answered 500 before this feature. Serving quantities in
their stored unit (FR-011) ends it, and US4's first test is each list answering 200.

**ADR:** none — a defect this feature's own requirement removes

## D20 — Design review applied

The design review approved the plan with six medium and three low findings, none blocking. All
nine were applied to plan.md, research.md and tasks.md, because each was a paragraph:

- Nested records and coordinates follow `FairDMVisibilityFilter`, the rule of a record's own
  route, not `visible_to`, which the overview pages use and which admits on dataset permissions
  the API does not read (FR-013).
- A child's, gradient's or conductivity's `site` reference is built from the primed site set,
  since FairDM does not prime a reference with a dotted source.
- Nested lists are built through the nested summary's `load_related`, and a site's children are
  fetched once across its intervals.
- Relations other than vocabulary fields keep the read-only fields FairDM gives them today
  (`stratigraphy` among them), so nothing becomes writable.
- A decimal quantity is served as a float, since the portal's orjson renderer would otherwise
  give a string.
- Tests added for hidden children on a parent, hidden gradients and conductivities on a child,
  a conductivity's children, a hidden site's coordinates, and a child's `ghfdb_id`.
- The schema extension sets `get_identity`, T001 is narrowed to the pieces its tests exercise,
  and the expected `units` in tests is a literal mapping from the model declarations.

**ADR:** none — corrections to this feature's plan
