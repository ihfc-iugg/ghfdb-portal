
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
