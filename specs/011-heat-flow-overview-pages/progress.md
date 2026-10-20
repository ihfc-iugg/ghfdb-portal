# FS-011 progress

- 2026-10-20 13:02 Build claimed; sketch built on the feature branch (95005d0), served on the development server.
- 2026-10-20 13:18 Sketch passed by delegated review; both taste calls kept.
- 2026-10-20 13:40 Research, plan and tasks written. Plan gate open.
- 2026-10-20 Design review dispatch refused by sessions_spawn (anthropic account/runtime unavailable for opus, sonnet, fable). Ledger at PLAN; next step S3R design review, brief at /home/sam/projects/worktrees/scratch-011/briefs/design-review-task.md (receipts in design-review.json).
- 2026-10-20 15:32 Build taken over by a second session. Design review spawn still refused, for every anthropic model and the forge agent default. Orchestrator told; spawn retried every 20 minutes until 17:32.

## 2026-10-20T13:55:14Z · Forge · S3R

Design review approved; findings folded into plan.md and tasks.md (D14, D15). Plan comment posted. US1 dispatched on sonnet in the feature worktree; stories build sequentially.

## 2026-10-20T14:02:38Z · Implementer US1 · T001

Did: Rebuilt `project/heat_flow/overview.py` as `HeatFlowPage` (`__init__`, `context`, `opens`, `split`, `listing`, `site_location`, `is_stale`, `for_child`). The sketch's other pages are ported onto the class unchanged as `for_site`, `for_interval`, `for_gradient_or_conductivity` and `for_parent` so their templates keep rendering; their stories rewrite them test-first.
Verified: `uv run pytest tests/test_heat_flow/test_overview.py -q -n0`: red first (ImportError, no `HeatFlowPage`), then 32 passed. Probe: removing `.visible_to(...)` from `split` fails 8 tests.
Next: T002, the tag library.
Watch: the tag still reads `?intervals=all`; plan says `?show=all`, which the site story (US2) switches together with its template.

## 2026-10-20T14:09:05Z · Implementer US1 · T002

Did: Rebuilt the tag library: `heat_flow_page` gathers once per record and keeps the result in the render context, `plus_minus` is a filter, `labels` writes a graph concept in the active language. Dropped `quantity` and changed every template that used it to the quantity's own text with `default_if_none`; the `plus_minus` tag calls became the filter. The `field` component's `data-field` and `not-recorded` hooks move to T003, where a page test drives them.
Verified: `uv run pytest tests/test_heat_flow/test_templatetags -q -n0`: red first (filter missing, two blocks cost double the queries, every page failing with the old templates), then 18 passed.
Next: T003, the child page tests and hooks.
Watch: the interval page raised `IconNotFoundError` in tests (`arrow-up`/`arrow-down` are `arrow_up`/`arrow_down` in the icon registry); fixed in `heatflowinterval_overview.html` so the page renders.

## 2026-10-20T14:19:14Z · Implementer US1 · T003

Did: Added the child page's data hooks (`data-heat-flow` on gradient, conductivity, corrections, parent, interval and site; `data-state` on empty, hidden, not-recorded and stale; `data-field` and the not-recorded state on `<c-heat_flow.field>`) and made the quality card read the gradient's and conductivity's own scores from the visitor-filtered props. Wrote TestChildPage and moved FS-007's TestChildCard into the same module, unskipped.
Verified: `uv run pytest tests/test_templates/test_heatflow_overview.py -q -n0`: red first (28 failed, 7 passed, hooks absent), then 35 passed. Probe: reading the own scores through `child.thermal_gradient` again fails the hidden-gradient test.
Next: T004, the docs.
Watch: the moved card tests could not run as written. Their reader needed to be a superuser (the fixtures' datasets are not published), and the `conductivity` fixture passed `location=[]`, a field since renamed `conductivity_location`; both are fixture-only repairs in `tests/test_templates/conftest.py`.

## 2026-10-20T14:23:59Z · Implementer US1 · T004

Did: Wrote `docs/guides/record-pages.md` (the child page section and the developer section: `HeatFlowPage` and its members, the three tags, the template names, the hooks, one example of a type template filling a block) and added it to the guides toctree. `quality-scores.md` now says the card is on the child page and that a hidden gradient or conductivity contributes no score. FS-007's US-5 and FR-018 point at FS-011.
Verified: Sphinx build succeeded (32 warnings, none in a page this story wrote or edited; the sphinx environment was built offline outside the worktree). `forge verify --steps docs --base origin/main` passed.
Next: full verify, then the completion report.
Watch: the sketch's twelve undocumented names are gone; the ported `for_site`, `for_interval`, `for_gradient_or_conductivity` and `for_parent` are documented in the developer section, to be rewritten by their stories.
