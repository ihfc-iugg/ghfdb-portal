
## 2026-10-20T19:17:48Z · orchestrator · S3

Research, plan and tasks written against origin/main 54509ad. No sketch (spec D12). Branch rebased onto FS-011. Stories run US4, US1, US2, US3.

## 2026-10-20T19:41:39Z · Implementer US4 · T001

Did: Built project/heat_flow/serializers.py (term(), TermChoiceField, TermRelatedField, three quantity number fields, UnitsField, the shared base and one summary serializer for each of the six types) and named each in its registration with serializer_class. Tests in tests/test_heat_flow/test_serializers.py first: 31 of 32 failed on the first run (five lists answered 500, terms were bare strings, units absent), then 32 passed.
Verified: uv run pytest tests/test_heat_flow/test_serializers.py tests/test_heat_flow/test_config.py -q -n0 -> 44 passed; ruff check, ruff format and mypy clean on the new module. The system-check test passes before and after by design, as a guard.
Next: T002 the schema extensions for terms and units.
Watch: a many-valued term reads its vocabulary per row, which is one query per term until US1 adds the prefetch; D21-D23 in decisions.md.

## 2026-10-20T19:44:44Z · Implementer US4 · T002

Did: Added project/heat_flow/schema.py with TermFieldSchema (a single term and, through TermRelatedFieldSchema, each entry of a many-valued term, as an object with name, label, uri and a vocabulary limited to the field's own) and UnitsFieldSchema (one property per quantity, limited to its unit). ready() in apps.py imports the module. Tests first in tests/test_heat_flow/test_schema.py: 5 of 6 failed (KeyError and string-not-object), then all 6 passed.
Verified: uv run pytest tests/test_heat_flow/test_schema.py -q -n0 -> 6 passed; serializers and schema together 38 passed; ruff and mypy clean. The nullable test passed before the change and guards it.
Next: T003 the guide.
Watch: D24 in decisions.md.

## 2026-10-20T19:47:53Z · Implementer US4 · T003

Did: Wrote docs/guides/heat-flow-records-api.md (the six addresses, terms, quantities and units, empty values, references, hidden records, a child heat flow example, and a short section on how the serializers are built) and listed it in docs/index.md after the published structure guide.
Verified: sphinx-build -b html docs built the page and its toctree entry with no warning about it, using a separate docs environment; the 36 warnings the build gives come from pages this branch does not touch, so a -W build fails on the base as well. forge verify --steps docs passed (it needs each new public name quoted in a page).
Next: full verify, then the report.
Watch: the guide's example values come from a response read in the tests, not typed in.

## 2026-10-20T20:14:39Z · Implementer US1 · T004

Did: Added the list/single split and the site and parent shapes in project/heat_flow/serializers.py: reference(), RequesterVisibility (records, narrow, mark_visible, can_see), HeatFlowListSerializer, summary_serializer and many_init on the base, load_related prefetching many-valued terms with their vocabulary (the US4 watch item), SiteParentSerializer, SiteIntervalSerializer, HeatFlowSiteSerializer and ParentHeatFlowSerializer; the parent summary gained its scores, quality and site reference. The site and parent registrations name the full serializers. Tests first: 12 of 15 failed on the first run (missing parent, intervals, children, scores, and a list whose query count grew), then 47 passed.
Verified: uv run pytest tests/test_heat_flow/test_serializers.py -q -n0 -> 47 passed; ruff, ruff format and mypy clean on the changed files.
Next: T005 the schema extension; three US4 schema tests are red until it lands, since the site list now serializes the full record in the generated document.
Watch: D25-D27 in decisions.md.

## 2026-10-20T20:15:26Z · Implementer US1 · T005

Did: Added HeatFlowRecordSchema to project/heat_flow/schema.py. For a list operation on a serializer with a summary it names, maps and identifies the summary; every other operation maps the serializer itself. Tests first in tests/test_heat_flow/test_schema.py: the site list item has parent and no intervals, the single site has intervals, the parent list item has no children and the single parent has them. The three US4 schema tests that read HeatFlowSiteSummary went red when T004 landed and are green again.
Verified: uv run pytest tests/test_heat_flow/test_schema.py -q -n0 -> 10 passed, after 5 failed first. Removing get_identity makes the no-component-warnings test fail with the identical-names warning, so it guards the extension.
Next: T006 the guide.
Watch: T004's commit alone leaves those three US4 schema tests red; T005 closes it.

## 2026-10-20T20:16:49Z · Implementer US1 · T006

Did: Added the site and parent sections to docs/guides/heat-flow-records-api.md, each with the list and single-record shape and one example request and response taken from a response read in a throwaway test (then deleted), with the host and the empty metadata lists changed or noted. Added the hidden-list rule to the Hidden records section and the new serializers and schema extension to the developer section.
Verified: forge verify --repo . --base origin/main --steps docs -> passed (it failed first, because the table no longer named the two summary serializers; the paragraph names them now).
Next: full verify, then the report.
Watch: the examples use real factory output, so the numbers are made up but consistent with each other.

## 2026-10-20T20:57:27Z · Implementer US2 · T007

Did: Gave the child its surface temperature, acquisition date, eight scores, ghfdb_id, relevance, references to parent, gradient, conductivity and site, and the location of its site (SiteLocationField, site_of, prime_sites). Added HeatFlowSerializer (registered for the child) nesting the gradient and conductivity whole or null and listing corrections through ChoiceLabelField, and ChoiceLabelFieldSchema. Tests first: 18 of 22 new serializer tests failed (missing fields, a 500 on update), then 94 passed with the schema and config tests.
Verified: uv run pytest tests/test_heat_flow/test_serializers.py tests/test_heat_flow/test_schema.py tests/test_heat_flow/test_config.py -q -n0 -> 94 passed; ruff and mypy clean. Removing the page priming or the site select_related makes the child list's query-count test fail; removing the schema extension fails its test.
Next: T008 the guide.
Watch: D28-D30 in decisions.md; the corrections prefetch cannot be told from lazy loading by a count, since a lazy read is one query either way.

## 2026-10-20T20:58:50Z · Implementer US2 · T008

Did: Replaced the child section of docs/guides/heat-flow-records-api.md with the list and single-record shapes, the scores, the references and the site location, the hidden cases, one example request and response from a response read in a throwaway test (deleted), and a shortened single-record example with the corrections. Added surface temperature to the units table and the new serializers and schema extension to the developer section.
Verified: forge verify --repo . --base origin/main --steps docs -> passed.
Next: full verify, then the report.
Watch: the single-record example shortens the gradient to a few fields, and says so.

## 2026-10-20T21:31:19Z · Implementer US3 · T009

Did: site and location on interval, gradient, conductivity and parent summaries via SitePlacedSerializer; scores, temperatures, conductivity location and number on the summaries; full interval (probe metadata, children, gradients, conductivities), gradient and conductivity records with children, registered in config.py.
Verified: uv run pytest tests/test_heat_flow/test_serializers.py tests/test_heat_flow/test_schema.py tests/test_heat_flow/test_config.py -n0: 143 passed. pre-commit run --all-files: all passed. Red run before code: 31 failed.
Next: T010 guide sections.
Watch: FairDM load_relations resets select_related when a serializer has no foreign key of its own (D31).

## 2026-10-20T21:41:43Z · Implementer US3 · T010

Did: guide sections for the depth interval, thermal gradient and interval conductivity (list and single-record shapes, one request and response each), the parent section shows location and site, units table and developer notes updated.
Verified: kit/forge verify --repo . --base origin/main: conformance, docs, lint, typecheck, test (389s), build all passed, exit 0.
Next: completion report.
Watch: none.
