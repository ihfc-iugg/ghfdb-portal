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
