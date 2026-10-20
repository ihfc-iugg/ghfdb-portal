# How to fill a development database with demo data

This guide adds demo datasets to a development database, so the dataset list, the map, the
assessment pages and the published-structure API have something to show. The data is generated,
not sampled from the published release.

## Before you start

- The database is running and migrated. See [](getting-started.md) for starting it.
- The command refuses to run outside development. In production it stops with an error and writes nothing.

## Add demo data

1. Run the command on your own machine:

   ```shell
   uv run python manage.py migrate
   uv run python manage.py seed_demo_data
   ```

   Or run it inside the Docker development stack:

   ```shell
   docker compose exec django uv run python manage.py seed_demo_data
   ```

2. Wait for the totals line, which reports the datasets, sites and children created.

   Add `--verbosity 2` to print one line per dataset as it is written.

## Choose how much data you get

Pass `--size` to set the number of datasets, from 4 to 200. The default is 20.

```shell
uv run python manage.py seed_demo_data --size 8
```

Four is the least that holds every assessment state. The largest size, 200 datasets, holds 10,000
children. A size outside the range stops the command before it writes anything.

## What a run creates

Each run adds the number of datasets you ask for. Every dataset holds:

- a literature item with a test DOI (prefix `10.5072`, which no real publication can have) and a
  citation key that starts with `demo-`
- a few contributors, with addresses at `demo.example`
- an assessment that links the dataset to its literature item
- 20 heat flow sites, each with one parent heat flow and between one and four children, which
  makes 50 children per dataset

Datasets are grouped into projects, one for every four datasets. Three datasets of each four
belong to the project and the fourth belongs to none, so both kinds appear. Every demo project is
public and owned by one of three demo organizations. The demo Data Assessor is credited as its
leader.

About 40 % of the sites are marine and measured with a probe. The rest are on land and measured in
boreholes. Gradients, conductivities, corrections, probe metadata and controlled vocabulary values
are all filled in, and the quality scores are computed by the portal when each dataset is written.

The heat flow records come from `DemoGraph` in `heat_flow/demo.py`, which builds the records
beneath one dataset. A test that needs a realistic graph rather than a single record can use it
directly:

```python
import random

from heat_flow.demo import DemoGraph
from heat_flow.signals import Recalculation

with Recalculation.deferred():
    DemoGraph(dataset, random.Random(1)).build(sites=4)
```

Wrap the build in `Recalculation.deferred()` so the quality scores are computed once, when the block
ends. `DemoGraph` reads its concepts from the database, so the controlled vocabularies must be loaded
first (`manage.py preload`, which the test suite runs for you).

The command loads the controlled vocabularies and the recommended licences first, so it works on a
freshly migrated database.

The first four datasets of every run take the four assessment states in turn: described, awaiting
a decision, changes requested and complete. After that, four datasets in five are complete.

- A complete dataset is public and published, and its parents and children carry published
  identifiers, so the dataset list and the published-structure API serve them.
- Every other dataset is private and unpublished, and its records carry no identifier.
- The demo Data Assessor uploads every assessment and is credited on every dataset. The demo Data
  Curator decides the assessments that are complete or have changes requested.

## Page states for the record pages

With `--page-states`, the first complete dataset of the run is varied so each state a heat flow
record's page answers for can be opened:

```bash
uv run python manage.py seed_demo_data --page-states
```

Without it, every record is scored under the current scheme revision and every site has a
location, as the sections above describe. Sign in as the demo Data Assessor to open its private neighbours, and read the
pages as a visitor who is not signed in to see what an unpublished dataset hides. Its first six
sites, in the order of their primary keys, hold:

| Site | Children | State |
| --- | --- | --- |
| 1 | 1 | A parent with no children, and a child with no gradient, conductivity, corrections or parent. |
| 2 | 2 | No parent designated. |
| 3 | 3 | A parent whose children are all marked not relevant. |
| 4 | 4 | More intervals than the page lists, an interval and its child, and another interval's child, in the unpublished dataset. |
| 5 | 1 | Scores stored under another scheme revision, and no location. |
| 6 | 2 | A child not yet scored, a gradient and the parent in the unpublished dataset. |

The unpublished dataset is the first dataset of the run, the one whose assessment is only
described. A record moved into it loses its published identifier, as every record of an
unpublished dataset does. Site 5 has no location, so a test that reads every site's coordinates
must skip it.

The step is `DemoGraph.vary_page_states(unpublished)`. It raises `ValueError` for a dataset of
fewer than six sites, and running it again varies the same sites further without failing:

```python
import random

from heat_flow.demo import DemoGraph

DemoGraph(dataset, random.Random(1)).vary_page_states(unpublished_dataset)
```

## Sign in

The command creates an account for each role and confirms its email address. Every account uses
the password `password`.

| Account | What it sees |
| --- | --- |
| `data-assessor.user@example.com` | The Data Assessor. Starts and uploads assessments, and opens its private demo datasets. |
| `data-curator.user@example.com` | The Data Curator. Decides assessments, and has some waiting for a decision. |
| `regular.user@example.com` | A signed-in user with no role, who sees public datasets only. |
| `staff.user@example.com` | A staff user. |
| `super.user@example.com` | A superuser. |

The command also creates the five accounts FairDM ships for development, at `fairdm.org`. They
are described in FairDM's documentation. A rerun reuses every account and adds no second one.

The dataset list page leaves private datasets out for every visitor, so reach a private dataset
from the assessments list, or through its own page.

```{warning}
These accounts share a published password. They are for development only. Remove them before a
copy of the development database leaves your machine.
```

## Run it again

Each run adds more datasets beside the ones already there. It never changes or removes a record
that is not demo data. Coordinates stay distinct across runs, because a site is its coordinates.

To find the demo datasets in the Django shell:

```python
from fairdm.core.dataset.models import Dataset

Dataset.all_objects.filter(options__demo_data=True)
```

Use `Dataset.all_objects`, because `Dataset.objects` hides private datasets.
