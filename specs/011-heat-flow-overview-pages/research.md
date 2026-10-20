# FS-011 research

Against origin/main at aab8e99 and FairDM f69c9cb, after the sketch (95005d0) was passed.

## Planning notes

None. The spec directory has no `planning-notes.md`.

## The sketch's requirements

Each line of `sketch.md` "What the screens need from the code" and "What the sketch faked", and how
it is met.

| # | Need | How it is met |
|---|---|---|
| 1 | Content gathered once per request | The `heat_flow_page` tag keeps what it gathered in the template's render context, keyed by the record, so every block after the first reads the same result. Query-count tests hold it. |
| 2 | A way for a type to add context | R1 below: a template tag, since FairDM offers no per-type plugin. |
| 3 | Visibility per listed record | `Sample.objects.visible_to(user)` and `Measurement.objects.visible_to(user)` (FairDM, `fairdm/core/managers.py`, `RecordVisibilityMixin`), one query per list, ids compared in Python. |
| 4 | Intervals in depth order without a query per interval | One query for the intervals ordered by `top`, one for their children with `prefetch_related("method")`, grouped in Python. |
| 5 | The children a parent rests on, by the rule that scores it | A model method, `ParentHeatFlow.quality_basis()`, which `refresh_quality` and the page both call. |
| 6 | Staleness | A non-empty `quality_scheme` that differs from `heat_flow.quality.SCHEME_REVISION`. |
| 7 | The site's location on records that hold none | `HeatFlowSite.location`, `location_elevation`, `location_uncertainty`, shown only when the site's own page would open. |
| 8 | Units and vocabulary labels | A quantity's `str()` already writes its abbreviated unit (pint, through FairDM's `print_value`). A value with its uncertainty uses pint's `plus_minus`, the call `Measurement.get_value` makes. Vocabulary labels need one filter: a `ConceptField` yields `research_vocabs.core.Concept`, whose `label` is a method taking a language, and a `ConceptManyToManyField` yields `research_vocabs.models.Concept`, whose `label` is a field. Nothing installed reads both. |
| 9, 10 | Every interval, every child | A "Show all" link that reloads the page with `?show=all`, on the site (intervals) and on the gradient, conductivity and parent pages (children). Replaces the disabled placeholder the sketch used. |
| faked | Context through a tag | Kept, by R1. Made a class (Article X) and cached (need 1). |
| faked | Seeded states | R4. |
| faked | No tests; FS-007's skipped tests | Every story is rebuilt test-first. FS-007's card tests are brought back against the child, gradient and conductivity pages (decision D4). |
| faked | FS-007's spec | Edited in this pull request so its page story points at FS-011 (D4). |

## R1. How a heat flow type adds its content to FairDM's page

FairDM registers one `Overview` plugin per base model (`fairdm.core.sample.plugins.Overview`,
`fairdm.core.measurement.plugins.Overview`). Its ADR 0023 names three routes: a template that
fills blocks, a subclass that overrides a plugin method, and a type template. The second needs the
subclass to be the one registered, and the plugin registry has no way to replace a registration:
`PluginRegistry.register` appends, and `validate_against_existing`
(`fairdm/contrib/plugins/checks.py`) refuses a second plugin on the same segment. Neither plugin
offers a hook for a type's own context.

So a type template is the only route that reaches the page, and a template cannot ask for
anything that depends on the visitor (every list is filtered by `visible_to(user)`). The content
is gathered by a template tag in the heat flow app, which hands the record and the visitor to a
class in `heat_flow/overview.py`.

- **Adopted:** a `simple_tag` taking the record, returning a dict, cached per render.
- **Not adopted:** reaching into `registry._registry` to swap the plugin (private state, breaks on
  any FairDM change); a context processor (it would have to work out the record from the URL); a
  newer FairDM (none offers a hook, and the pin moves deliberately only).

This meets the bar for an ADR (it is architectural, every future heat flow page follows it, and
the reason is not visible in the code). FairDM ADR 0023's "Revisit if" names exactly this case, so
a hook upstream would retire it.

## R2. Where each piece of logic lives

- **Which children a parent's quality rests on** is a rule about one record:
  `ParentHeatFlow.quality_basis()`, returning the basis (`single`, `relevant`, `none`, `empty`) and
  the children. `refresh_quality` calls it, so the page and the score cannot disagree.
- **What a page gathers** is one subject with shared state (the record, the visitor, whether the
  full list was asked for), so it is one class, `HeatFlowPage`, in a module of its own,
  `heat_flow/overview.py` (Article X; `docs/contributing/standards/django.md` §1, Modules).
- **Showing a value** is template work: two filters (`labels`, `plus_minus`) beside the tag.
- **Reused markup** is Cotton components under `templates/cotton/heat_flow/` and the existing
  `templates/cotton/card/quality/`, never `{% include %}`.

## R3. FS-007's quality card

The card's components call `<c-data_field>`, which was the old name of django-mvp's
`<c-mvp.data_field>` (`mvp/templates/cotton/mvp/data_field.html`), so the card fails to render.
The sketch moved them, split out the grades and the flags so the parent's card reuses them, and
added `card/quality/parent.html`. `tests/test_templates/test_measurement_detail.py` carries
FS-007's tests, skipped module-wide since #263 because the page they drove was removed. They are
re-pointed at the measurement overview pages and unskipped.

## R4. Development data for every state

The walkthrough needs a site with no parent, a parent with no children and one with none marked
relevant, a child with no gradient, conductivity, corrections or parent, a stale score, an
unscored child, a site with no location, a site with more than twenty intervals, and records in an
unpublished dataset listed beside published ones. `seed_demo_data` (FS-008) makes none of these
on purpose. The development seeding path is extended so one dataset of each run carries them,
documented in `docs/development/demo-data.md`. Development-only, never a migration or a fixture.

## R5. Out of reach of this feature

- FairDM's "Other measurements on this sample" list on a measurement page stays as FairDM draws it.
- Translations: strings are wrapped; no `.po` changes are needed for `en`.

## What already exists

| New piece | Search stopped at | Found |
|---|---|---|
| Type templates for six types | 3, installed package | FairDM's lookup finds `heat_flow/<model>_overview.html` (`TypedOverviewPlugin.get_template_names`) |
| `HeatFlowPage` (gathers a page's content) | 7, new code | No per-type context hook in FairDM (R1) |
| `heat_flow_page` tag | 7, new code | as above |
| Visibility of listed records | 3, installed package | `RecordVisibilityMixin.visible_to`, `fairdm/core/managers.py` |
| Which children a parent rests on | 2, this repo | the rule inside `ParentHeatFlow.refresh_quality`; lifted into `quality_basis()` |
| Staleness | 2, this repo | `heat_flow.quality.SCHEME_REVISION`; the comparison is new, one line |
| Quantity with unit | 3, installed package | pint `Quantity.__str__` (as `Measurement.print_value`) |
| Value ± uncertainty | 3, installed package | pint `plus_minus`, wrapped by a one-line filter for templates |
| Vocabulary labels | 7, new code | `research_vocabs` `i18n_label` reads only the graph concept; nothing reads both kinds |
| Labelled field, "Not recorded" when empty | 3, installed package | `<c-mvp.data_field missing=…>` (django-mvp), wrapped as `<c-heat_flow.field>` to fix the empty text |
| Location card | 3, installed package | FairDM `<c-card.location>` |
| Cut list wording, hidden counts | 3, installed package | FairDM's sample and measurement templates (copied wording) |
| Quality card, own-score card | 2, this repo | `templates/cotton/card/quality/` (FS-007) |
| List rows, stats strip | 3, installed package | daisyUI `list`, FairDM `<c-stats>` |
| "Show all" | 5, the browser | a plain link with `?show=all` |
| Seeded states | 2, this repo | `heat_flow.demo.DemoGraph`, extended |
| A record's site | 2, this repo | `ParentHeatFlow.site`, `HeatFlowInterval.site`, `heat_flow.quality.site()`; no helper of its own |
