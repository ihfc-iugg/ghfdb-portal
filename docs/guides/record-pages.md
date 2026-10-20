# Record pages

Every heat flow record has a page: a site, a depth interval, a child heat flow value, a thermal
gradient, an interval conductivity and a parent heat flow value. Each page keeps everything the
portal shows on any record (the header and its Manage menu, the people credited, the identifiers,
how to cite it and who may open it) and adds what that kind of record holds. This page describes
what a visitor sees on each, and, for developers, how the content reaches the page.

A visitor is anyone reading the portal, signed in or not. A record is shown to them when the portal
would let them open its page: its dataset is public and published, or they hold a level on the
record, its dataset or its project.

## What every page does

- **Quantities carry their unit.** A value is written with its unit, and a value with an
  uncertainty is written `value ± uncertainty unit`.
- **Vocabulary fields are written as terms**, in the visitor's language where the vocabulary has
  one, never as stored identifiers.
- **An empty field says it is not recorded.** It is never shown as zero. An empty score says it is
  not determined.
- **A record the visitor may not open is never named or linked.** The page says that a record
  exists in a dataset that has not been published, and nothing else about it: no value, no
  score, no link.
- **Scores are shown as stored.** A page never calculates one.

## A child heat flow value's page

The child is the heat flow determination itself, and its page answers how the value was reached.
It shows:

- **The value and its method.** The value with its uncertainty and unit, and the method as its
  vocabulary terms. A child with no method says the method is not recorded.
- **What it was calculated from.** The thermal gradient and the interval conductivity, each with
  its value and a link to its own page. A child with no gradient, or no conductivity, says which
  one is not recorded and still shows everything else.
- **Corrections.** Every correction recorded for the child, each with its correction type and
  status. A correction recorded as not recognised is shown as recorded: that is a different fact
  from no correction being recorded, which the page says on its own.
- **Quality.** The quality code, the U-score and M-score, the gradient's and conductivity's own
  scores beside the scores corrected for this child, the missing-information marks, the seven
  perturbation flags and the scheme revision. [Quality scores](quality-scores.md) explains how
  each is reached. A gradient or conductivity the visitor may not open shows no score in this
  card.
- **A stale score.** A score stored under a scheme revision other than the current one is said to
  be stale. It is still shown as stored.
- **The parent.** A link to the parent heat flow value the child belongs to and whether the child
  is marked relevant to it, or a statement that the child belongs to no parent.
- **Where it was measured.** The depth interval, with its depth range, and the site, each linked,
  and the site's location on a map ([the site's location](#the-sites-location)).
- **The determination.** The surface temperature, the date acquired, the expedition or platform,
  the GHFDB child ID, the data reference and related publications of the dataset it belongs to,
  and the comment.

## A site's page

The site's page answers what the database holds for a place. It shows:

- **The parent heat flow.** The parent's value with its uncertainty and unit, its quality code and
  a link to its page. A site with no parent says that none has been designated. A parent the
  visitor may not open is said to belong to a dataset that has not been published, and nothing
  more.
- **The site.** Its geographic environment, exploration method, exploration purpose and site type
  as vocabulary terms; its access geometry (top, bottom, length, vertical depth, inclination,
  azimuth, elevation and elevation datum); and where it lies (country, region, continent and
  domain). A field with nothing recorded says so.
- **The depth intervals.** Every interval from the shallowest to the deepest, ordered by top, then
  bottom. Each interval shows its depth range, its lithology and the heat flow values determined
  over it, each with its value and quality code, linked to its own page. An interval with no heat
  flow value says so.
- **Records the visitor may not open.** An interval, or a heat flow value over an interval, in a
  dataset that has not been published is counted and never named or linked.

### Show all

A site with many intervals lists the first twenty and says how many more there are. The **Show all**
link beside that count opens the same page with `?show=all`, which lists every interval the visitor
may open. The link is absent when the page already lists them all.

## A depth interval's page

An interval is the stretch of a borehole or a probe track that heat flow values were determined
over, so its page answers where those values were measured and what rock is there. It shows:

- **The depth range.** The top and the bottom of the interval, with their unit.
- **The vertical depth and the depth datum.** A field with nothing recorded says so.
- **The rock.** Its lithology and age as vocabulary terms, and its stratigraphy.
- **The IGSN.** The interval's sample identifier, where one is recorded.
- **The probe.** Where a marine probe was used: the probe type, length, penetration and tilt,
  each with its unit. An interval with no probe metadata shows no probe card.
- **The site.** A link to the site the interval belongs to. A site the visitor may not open is not
  named: the page says that it belongs to a dataset that has not been published.
- **The site's location.** An interval holds no location of its own, so the page shows the
  site's. See [the site's location](#the-sites-location).

FairDM lists the measurements made over the interval, as it does on every sample's page.

### The site's location

Only a site holds coordinates ([ADR 0023](../adr/0023-a-site-holds-the-location-and-its-own-elevation.md)).
The pages of an interval, a child, a thermal gradient, an interval conductivity and a parent
therefore show the site's location: a map with the point marked, the latitude and longitude, and
the elevation and uncertainty where the site records them. The card is titled as the site's. A
site with no location says that none is recorded, and a site in a dataset that has not been
published is not named, located or linked: the card says its location is not shown.

## A thermal gradient's page

The gradient's page answers what was measured, and which heat flow values rest on it. It shows:

- **The values.** The measured gradient and the corrected gradient, each with its uncertainty and
  unit. A gradient with no corrected value says so.
- **The temperatures.** At the top and the bottom of the interval: the temperature, the method it
  was read by, the correction applied, the shut-in time, and the number of temperature
  recordings. A field with nothing recorded says so.
- **Quality.** The gradient's own T-score, with the missing-information mark where one applies,
  and the scheme revision. A gradient whose score was not determined says so; it is never shown as
  zero. The score here is the gradient's own, before any heat flow value applies its corrections:
  the child's page shows the corrected score beside it.
- **A stale score.** A score stored under a scheme revision other than the current one is said to
  be stale and is shown as stored.
- **Where it was measured.** The depth interval and the site, each linked, and the site's
  location on a map.
- **The heat flow values that use it.** Each value linked, with its quality code. A gradient no
  heat flow value uses says so.

## An interval conductivity's page

The conductivity's page answers how a conductivity was determined, and which heat flow values rest
on it. It shows:

- **The value.** The conductivity with its uncertainty and unit, and the number of measurements
  it comes from.
- **How it was determined.** Its source, the location of the samples, the method, the averaging
  strategy, the saturation, the pT conditions and the pT function, each as its vocabulary terms. A
  field with nothing recorded says so.
- **Quality.** The conductivity's own TC-score, with the missing-information mark where one
  applies, and the scheme revision. A score that was not determined says so and is never shown as
  zero.
- **A stale score.** Said and shown as on a gradient's page.
- **Where it was measured.** The depth interval and the site, each linked, and the site's
  location on a map.
- **The heat flow values that use it.** Each value linked, with its quality code.

On both pages a heat flow value in a dataset that has not been published is counted and never named
or linked, and the interval and the site are named only when the visitor may open them.

### Show all

A gradient or a conductivity used by many heat flow values lists the first twenty and says how many
more there are. The **Show all** link beside that count opens the same page with `?show=all`, which
lists every heat flow value the visitor may open. The link is absent when the page already lists
them all.

## A parent heat flow value's page

A parent is designated by the database's curators, not calculated, so its page answers which heat
flow values stand behind it. It shows:

- **The designation.** The parent's value with its uncertainty and unit, whether a heat production
  correction was applied, the curator's comment and the GHFDB parent ID. A field with nothing
  recorded says so. A correction that was not decided is shown as not recorded, and a correction
  recorded as not applied is shown as not applied.
- **Quality.** The quality code, the U-score and M-score, the seven perturbation flags and the
  scheme revision, as stored. [Quality scores](quality-scores.md) explains how the parent inherits
  each from its children.
- **What the quality rests on.** The card says which children the quality is inherited from. A
  parent with one child rests on that child, whether or not it is marked relevant. A parent with
  several children rests on the ones marked relevant. A parent with several children and none
  marked relevant, or with no children, says that its quality could not be determined.
- **The children.** Every child of the parent, each with its value, its quality code, its method,
  whether it is marked relevant and a link to its page. The children the quality rests on are
  marked as such. A parent with no children says so.
- **A stale score.** A score stored under a scheme revision other than the current one is said to
  be stale and is shown as stored.
- **The site.** The site the parent represents, linked, and its location on a map.
- **Records the visitor may not open.** A child in a dataset that has not been published is
  counted and never named or linked. It still counts towards what the quality rests on, because
  the quality is stored for the parent's whole set of children. The site is named only when the
  visitor may open it.

### Show all

A parent with many children lists the first twenty and says how many more there are. The **Show
all** link beside that count opens the same page with `?show=all`, which lists every child the
visitor may open. The link is absent when the page already lists them all.

## Where each release column is shown

Every column of the GHFDB release format that the export writes can be read on the page of the
child or on the page of a record it links to, so a visitor needs no download to see a row. The
table names the page each column is read on, and the field on it. A field is marked on the page by
its `data-field` attribute, and a test reads the columns from the export itself and finds each one
there. A column that several fields share, such as a value with its uncertainty, is read on the one
field.

| Column | Page | Field |
| --- | --- | --- |
| `q` | Parent | `value` |
| `q_uncertainty` | Parent | `value` |
| `name` | Depth interval | `site` |
| `lat_NS` | Child | `location` |
| `long_EW` | Child | `location` |
| `elevation` | Site | `elevation` |
| `environment` | Site | `environment` |
| `p_comment` | Parent | `comment` |
| `corr_HP_flag` | Parent | `corr_HP_flag` |
| `total_depth_MD` | Site | `length` |
| `total_depth_TVD` | Site | `vertical_depth` |
| `explo_method` | Site | `explo_method` |
| `explo_purpose` | Site | `explo_purpose` |
| `ID` | Child | `ghfdb_id` |
| `qc` | Child | `value` |
| `qc_uncertainty` | Child | `value` |
| `q_method` | Child | `method` |
| `q_top` | Depth interval | `depth_range` |
| `q_bottom` | Depth interval | `depth_range` |
| `probe_penetration` | Depth interval | `probe_penetration` |
| `publication_reference` | Child | `publication_reference` |
| `data_reference` | Child | `data_reference` |
| `relevant_child` | Child | `is_relevant` |
| `c_comment` | Child | `comment` |
| `corr_IS_flag` | Child | `corrections` |
| `corr_T_flag` | Child | `corrections` |
| `corr_S_flag` | Child | `corrections` |
| `corr_E_flag` | Child | `corrections` |
| `corr_TOPO_flag` | Child | `corrections` |
| `corr_PAL_flag` | Child | `corrections` |
| `corr_SUR_flag` | Child | `corrections` |
| `corr_CONV_flag` | Child | `corrections` |
| `corr_HR_flag` | Child | `corrections` |
| `expedition` | Child | `expedition` |
| `probe_type` | Depth interval | `probe_type` |
| `probe_length` | Depth interval | `probe_length` |
| `probe_tilt` | Depth interval | `probe_tilt` |
| `water_temperature` | Child | `surface_temperature` |
| `geo_lithology` | Depth interval | `lithology` |
| `geo_stratigraphy` | Depth interval | `stratigraphy` |
| `T_grad_mean` | Thermal gradient | `value` |
| `T_grad_uncertainty` | Thermal gradient | `value` |
| `T_grad_mean_cor` | Thermal gradient | `corrected_value` |
| `T_grad_uncertainty_cor` | Thermal gradient | `corrected_value` |
| `T_method_top` | Thermal gradient | `method_top` |
| `T_method_bottom` | Thermal gradient | `method_bottom` |
| `T_shutin_top` | Thermal gradient | `shutin_top` |
| `T_shutin_bottom` | Thermal gradient | `shutin_bottom` |
| `T_corr_top` | Thermal gradient | `correction_top` |
| `T_corr_bottom` | Thermal gradient | `correction_bottom` |
| `T_number` | Thermal gradient | `number` |
| `q_date` | Child | `date_acquired` |
| `tc_mean` | Interval conductivity | `value` |
| `tc_uncertainty` | Interval conductivity | `value` |
| `tc_source` | Interval conductivity | `source` |
| `tc_location` | Interval conductivity | `conductivity_location` |
| `tc_method` | Interval conductivity | `method` |
| `tc_saturation` | Interval conductivity | `saturation` |
| `tc_pT_conditions` | Interval conductivity | `pT_conditions` |
| `tc_pT_function` | Interval conductivity | `pT_function` |
| `tc_number` | Interval conductivity | `number` |
| `tc_strategy` | Interval conductivity | `strategy` |
| `Ref_IGSN` | Depth interval | `igsn` |

## For developers

### How the content reaches a page

FairDM draws every record's overview page from `overview/page.html` and lets a record's type
extend it. A heat flow type provides `heat_flow/<model_name>_overview.html`, which extends
`sample/sample_overview.html` or `measurement/measurement_overview.html` and fills the blocks
FairDM defines. FairDM's page is extended, never replaced, so the shared header, people,
identifiers and citation stay.

What a page lists beyond FairDM's own context is gathered by `HeatFlowPage`, and reaches the
template through the `heat_flow_page` tag. FairDM offers no per-type context hook, which is why:
[ADR 0024](../adr/0024-a-heat-flow-pages-content-comes-through-a-template-tag.md) records the
choice.

| Page | Template |
| --- | --- |
| Site | `heat_flow/heatflowsite_overview.html` |
| Depth interval | `heat_flow/heatflowinterval_overview.html` |
| Child | `heat_flow/heatflow_overview.html` |
| Thermal gradient | `heat_flow/thermalgradient_overview.html` |
| Interval conductivity | `heat_flow/intervalconductivity_overview.html` |
| Parent | `heat_flow/parentheatflow_overview.html` |

The reusable pieces are Cotton components: `<c-heat_flow.field>`, `<c-heat_flow.code>`,
`<c-heat_flow.stale>`, `<c-heat_flow.child_row>`, `<c-heat_flow.children>`,
`<c-heat_flow.measured_on>` and `<c-heat_flow.site_location>` under `templates/cotton/heat_flow/`,
and `<c-card.quality>` with its parts under `templates/cotton/card/quality/`.

### `HeatFlowPage`

`HeatFlowPage(record, user, show_all=False)` in `heat_flow.overview` gathers what a record's page
lists, for one visitor. `context()` dispatches on the record's type to the method that gathers it,
and each method returns a dictionary the template reads.

| Method | Gathers |
| --- | --- |
| `for_child()` | The gradient, conductivity and parent the visitor may open, each with a `*_hidden` flag; the corrections; the interval and site; the site's location; whether the scores are stale. |
| `for_site()` | The site's parent, or that it is hidden; its intervals from shallowest to deepest, each with its children; how many intervals and children the visitor may not open; and the children the visitor may open, counted over every interval the visitor may open. |
| `for_interval()` | The interval's site, `None` when the visitor may not open it, with `site_hidden`; its probe metadata, `None` where it has none; its `igsn`, empty where it has none; and the site's location. |
| `for_gradient_or_conductivity()` | The measurement's interval and site, each `None` when the visitor may not open it, and the site's location; the children that use the measurement, with the cut at `children_shown` lifted by `show_all`, each child's method prefetched; whether the score is stale. |
| `for_parent()` | The parent's children, the relevant ones first, with the cut at `children_shown` lifted by `show_all` and each child's method prefetched; the `basis` of the parent's quality and the keys of the children it `rests_on`, each listed child carrying its own `rests_on`; the site, `None` when the visitor may not open it, and its location; whether the score is stale. |

The members every method shares:

- `opens(record)` says whether the record's own page would open for the visitor.
- `split(records)` returns the records the visitor may open, in the order given, and how many they
  may not. It makes one `visible_to` query however many records it is given, so the records must
  all be samples or all be measurements.
- `listing(children, limit=None)` splits a list of children and cuts it to `limit`, returning
  the `rows`, the `total` the visitor may open, how many `more` the cut leaves out and how many are
  `hidden`.
- `site_location()` gives the location of the record's site as the site's. It reads `record.site`
  for a parent or an interval and `record.sample.site` for the rest. It returns the `site` and
  whether the visitor may see it (`visible`), and its `point`, `elevation` and `uncertainty`;
  nothing of the site when the visitor may not open it.
- `is_stale(record)` says whether a record's stored scheme revision is not the current one.

A list shows its first rows and says how many more there are. `intervals_shown` and
`children_shown` set the cut for a site's intervals and for the children a page lists; `show_all`
lifts the cut on the intervals and on the children a gradient's, a conductivity's or a parent's
page lists. A page asks for it with `?show=all`.

### `ParentHeatFlow.quality_basis`

`ParentHeatFlow.quality_basis()` says which children a parent's quality rests on. It is the one
place the inheritance rule is written: `refresh_quality` stores the quality it names, and the
parent's page shows the same basis. It returns the basis and the children it rests on.

| Basis | When | Children it rests on |
| --- | --- | --- |
| `single` | The parent has one child, marked relevant or not. | That child. |
| `relevant` | The parent has several children and some are marked relevant. | The children marked relevant. |
| `none` | The parent has several children and none is marked relevant. | None. |
| `empty` | The parent has no children. | None. |

```python
basis, children = parent.quality_basis()
if basis == "none":
    ...  # several children, none marked relevant: the quality is not determined
```

It reads all the parent's children, those the visitor may not open included, so the basis on the
page is the one the stored quality was calculated from.

### Template tags

Load them with `{% load heat_flow_overview %}`.

- `{% heat_flow_page record as hf %}` hands the template what `HeatFlowPage(record, request.user)`
  gathers. A render gathers a record once: a second block asking for the same record reads the
  result the first block left in the render context, with no further query.
- `{{ concepts|labels }}` writes one vocabulary concept, or a many-to-many manager of concepts,
  as its labels joined by commas. A graph concept is written in the active language.
- `{{ value|plus_minus:uncertainty }}` writes `value ± uncertainty unit`, the value alone when
  the uncertainty is empty, and nothing when the value is empty.

### Adding content to a page

To add a card to a type's page, fill a block in its template. This one adds a card to the
child's page, and reads the gradient the visitor may open:

```django
{% extends "measurement/measurement_overview.html" %}
{% load i18n heat_flow_overview %}
{% block overview.properties %}
  {% heat_flow_page measurement as hf %}
  <c-mvp.card title="{% translate 'Calculated from' %}">
    {% if hf.gradient %}
      <a href="{{ hf.gradient.get_absolute_url }}">{{ hf.gradient.print_value }}</a>
    {% elif hf.gradient_hidden %}
      {% translate "Recorded in a dataset that hasn't been published yet." %}
    {% else %}
      {% translate "No thermal gradient is recorded." %}
    {% endif %}
  </c-mvp.card>
{% endblock overview.properties %}
```

Read a related record from the dictionary, never from the model's own relation, so that a record
the visitor may not open stays out of the page.

### Hooks for tests

Tests find a page's content by `data-` attributes and by the records' URLs, never by wording.
`data-heat-flow="<what>"` marks each card or list (`gradient`, `conductivity`, `corrections`,
`parent`, `intervals`, `children`, `interval`, `site`, `probe`, `location`). The location card
carries `data-source="site"`, and `data-state` is `not-recorded` for a site with no location and
`hidden` for a site the visitor may not open; its map carries FairDM's `data-lon` and `data-lat`. A cut list carries `data-more`, the number it does not
show, and a list that hides records carries `data-hidden`, how many; a site page's interval rows
carry `data-interval` with the interval's key, and each child in a list `data-child` with the
child's key; a child row on a parent's page also carries `data-relevant` and `data-rests-on`
(`true` or `false`). The parent's quality card carries `data-quality="basis"`, whose `data-value`
is the basis. `data-state` marks an empty (`empty`, `none`, `not-recorded`),
hidden (`hidden`) or stale (`stale`) state. `<c-heat_flow.field>` carries `data-field="<name>"`,
and `data-state="not-recorded"` when its value is empty; the gradient's table cells carry the same
two attributes. A correction row carries
`data-correction` and `data-status`. FairDM's own cards carry `data-card` (`identifiers`,
`citation`) and the Manage menu `data-menu="manage"`.
