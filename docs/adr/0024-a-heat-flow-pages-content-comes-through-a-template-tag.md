# ADR 0024 — A heat flow page's content comes through a template tag

**Status:** accepted

## Decision

Each heat flow type adds its content to FairDM's shared sample or measurement overview page with a
type template: `heat_flow/<model>_overview.html`, which extends FairDM's template and fills its
blocks. A template cannot ask for anything that depends on the visitor, so the content a page
lists is gathered by the `heat_flow_page` template tag in `heat_flow.templatetags.heat_flow_overview`.

- The tag takes the record, reads the visitor and the `show` query parameter from the request, and
  hands both to `HeatFlowPage` in `heat_flow/overview.py`. `HeatFlowPage` returns a dict of what
  the page lists.
- The tag keeps that dict in the template's render context, so every block that asks for the same
  record reads one result and the page gathers once.
- A new heat flow type or a new block calls the tag in the same way. It does not register a
  plugin of its own, and it does not replace FairDM's.

## Why

FairDM registers one overview plugin per base model, one for samples and one for measurements. The
plugin offers no hook for a type's own context. The plugin registry appends a registration and
refuses a second plugin on the same segment, so a subclass of the overview plugin cannot take the
place of FairDM's. A type template is the only route into the page that FairDM supports.

Every list on these pages is limited to the records the visitor may open, which needs the visitor
and a database query. A template tag is the place a template can reach both. Alternatives that were
weighed and not adopted:

- **Reaching into the plugin registry's private state to swap the registered overview.** It breaks
  on any change inside FairDM.
- **A context processor.** It would have to work out which record the page is for from the URL, on
  every request, including the ones that are not record pages.
- **A newer FairDM.** None offers a hook, and the pinned version moves only by deliberate choice.

## Revisit if

FairDM adds a per-type context hook to its overview plugins, or lets a project replace a
registered plugin. Either makes the tag unnecessary, and the gathering class can move behind the
hook.
