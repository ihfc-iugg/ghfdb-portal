# Tasks: API representations of heat flow sites and measurements

**Input**: `specs/010-heat-flow-api/` — spec.md, research.md, plan.md, decisions.md

**Tests**: required, written first and seen red for the right reason. Every test requests a route
through `client` (anonymous) or a signed-in client, so it exercises the generated viewset, the
registered serializer, FairDM's visibility filter and pagination together. Records come from
`tests/factories.py`, vocabulary values are set explicitly, and shared setup goes in
`tests/test_heat_flow/conftest.py`. Query counts compare a page of one record with a page of
several under `django_assert_num_queries`, and never pin a count that grows with rows. No test
asserts help text, descriptions or wording.

**Order**: US4, then US1, US2, US3, one after another on the branch. Every story edits
`project/heat_flow/serializers.py`, `tests/test_heat_flow/test_serializers.py` and
`docs/guides/heat-flow-records-api.md`.

**Docs**: each story documents the shapes it introduces in the guide, in its own task.

## Format: `[ID] [Story] Description`

---

## Phase 1: User Story 4 — terms and units without looking anything up (P2, built first)

**Goal**: all six lists answer 200, every vocabulary term is an object with its label and
identifier, every quantity is a number in its stored unit with the unit stated, and the schema
describes both.

**Independent test**: read one record of each type with every vocabulary field and every quantity
filled; each term carries a label and an identifier, each quantity a unit equal to the field's
declared unit.

- [ ] T001 [US4] Create `project/heat_flow/serializers.py` with the fields and base of plan.md
      (*The fields*, *The base*) and a summary serializer for each of the six types holding the
      common fields, the registration's own fields and `units`; name each in its registration with
      `serializer_class` in `project/heat_flow/config.py`. Tests first in
      `tests/test_heat_flow/test_serializers.py`: each list route answers 200 with a record of its
      type (today five answer 500); a single and a many-valued term each give `name`, `label`, `uri`
      and `vocabulary`, a many-valued field one entry per term; each quantity is a number equal to
      the stored magnitude in its declared unit, and `units` names that unit for every quantity
      field; an empty quantity is `null` with its unit still in `units`; a site created through the
      API today with a term's name for `environment` is still created and stores that term
      (FR-017); FairDM's system checks report no `fairdm.E600`.
- [ ] T002 [US4] Create `project/heat_flow/schema.py` with `TermFieldSchema` and `UnitsFieldSchema`
      of plan.md › *Schema*, imported from `HeatFlowSchemaConfig.ready()`. Tests first in
      `tests/test_heat_flow/test_schema.py`, from the generated schema: a single and a
      many-valued term property each describe an object whose `vocabulary` is that field's
      vocabulary; a record's `units` property lists each quantity field with its unit (FR-018).
- [ ] T003 [US4] Write `docs/guides/heat-flow-records-api.md`: the six addresses, how a term, a
      quantity and its unit, an empty value, a reference and a hidden record appear; list it in
      `docs/index.md` beside `guides/published-structure-api`. Docs build clean with `-W`.

## Phase 2: User Story 1 — a site with what belongs to it (P1)

**Goal**: a site's list gives its position, its parent's value, uncertainty and quality code; its
single record gives its parent whole and every interval with the children made over each; a
parent's record gives its scores, identifier, site and children with their relevance.

**Independent test**: a public site with a parent, two intervals and several children, read
anonymously in one request; the site list's query count does not grow with sites.

- [ ] T004 [US1] Site and parent shapes per plan.md › *The shapes*: the site summary's `parent`
      from the page priming in `HeatFlowListSerializer`; the full site and parent serializers;
      `summary_serializer` and `many_init`; `visible`, `reference` and `can_see`. Tests first:
      spec US1 scenarios 1–7 — the single site carries its parent, every interval and each
      interval's children (all of them, when one interval carries several); the list carries
      position, parent value, uncertainty and quality code and no `intervals`; a site with no
      parent carries `parent: null` in both shapes and is listed; the parent's record carries its
      value, uncertainty, scores, `ghfdb_id`, its site and each child with `is_relevant`, a child
      not marked relevant included; an interval or a child in a dataset the requester may not see
      is absent from the site's record and is never a `null` entry; a parent the requester may not
      see is `null` on the site in both shapes; an anonymous request is served; query count of the
      site list and of the parent list is the same for one record as for several; the single
      site's count does not grow with its intervals and children.
- [ ] T005 [US1] Add `HeatFlowRecordSchema` to `project/heat_flow/schema.py`. Tests first in
      `tests/test_heat_flow/test_schema.py`: the site list operation's item component is the
      summary's (it has `parent` and no `intervals`) and the single-site operation's is the full
      record's (it has `intervals`).
- [ ] T006 [US1] Guide: the site and parent sections, each with its list and single-record shape
      and one example request and response.

## Phase 3: User Story 2 — a child with how it was reached (P1)

**Goal**: a child carries its scores, references to its interval, parent and site and its site's
coordinates; its single record nests its gradient and conductivity and lists its corrections.

**Independent test**: a child with a gradient, a conductivity and several corrections, read
anonymously; all of them and its scores in one response; the child list's query count does not
grow with children.

- [ ] T007 [US2] Child shapes per plan.md › *The shapes*, and `SiteLocationField` with `site_of`.
      Tests first: spec US2 scenarios 1–7 — the single child nests its gradient and conductivity
      and lists every correction with its type and status as `{name, label}`; a scored child's
      eight score fields equal the stored values; an unscored child's numeric scores are `null`;
      the child carries its site's coordinates and references to its interval, parent and site, in
      the list and on its own; a child whose site the requester may not see carries
      `location: null` and `site: null`; a child with no gradient, no conductivity or no
      corrections carries `null`, `null` and `[]` and is listed; a correction recorded as not
      corrected is listed and a correction type never recorded is absent; a negative value is
      served as stored; a request creating or changing a child that supplies scores, a quality
      code, a scheme revision or a `ghfdb_id` stores none of them; query count of the child list
      is the same for one record as for several, and the single child's does not grow with its
      corrections.
- [ ] T008 [US2] Guide: the child section with its list and single-record shape and one example
      request and response.

## Phase 4: User Story 3 — a gradient, a conductivity or an interval on its own (P2)

**Goal**: each carries its own measurements, its scores where scored and its site's coordinates;
its single record refers to the records that use it or are made over it.

**Independent test**: a gradient used by two children and an interval with probe metadata, each
read on its own.

- [ ] T009 [US3] Interval, gradient and conductivity shapes per plan.md › *The shapes*, and
      `location` from the site on the parent. Tests first: spec US3 scenarios 1–5 — a scored
      gradient's and conductivity's `score`, `score_missing` and `quality_scheme` equal the stored
      values; a gradient's single record refers to each child calculated from it; an interval's
      single record carries its probe metadata with its terms and units, and refers to each child,
      gradient and conductivity made over it; an interval without probe metadata carries
      `probe_metadata: null`; each carries its site's coordinates, and so does a parent; a related
      record the requester may not see is absent from those lists; query counts of the interval,
      gradient and conductivity lists are the same for one record as for several, and their single
      records' do not grow with what they refer to.
- [ ] T010 [US3] Guide: the interval, gradient and conductivity sections with their list and
      single-record shapes and one example request and response.
