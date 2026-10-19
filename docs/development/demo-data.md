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
   docker compose exec django python manage.py seed_demo_data
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

About 40 % of the sites are marine and measured with a probe. The rest are on land and measured in
boreholes. Gradients, conductivities, corrections, probe metadata and controlled vocabulary values
are all filled in, and the quality scores are computed by the portal when each dataset is written.

The command loads the controlled vocabularies and the recommended licences first, so it works on a
freshly migrated database.

At this stage every dataset is public and its assessment is complete. Both are decided by one demo
user.

## Run it again

Each run adds more datasets beside the ones already there. It never changes or removes a record
that is not demo data. Coordinates stay distinct across runs, because a site is its coordinates.

To find the demo datasets in the Django shell:

```python
from fairdm.core.dataset.models import Dataset

Dataset.all_objects.filter(options__demo_data=True)
```

Use `Dataset.all_objects`, because `Dataset.objects` hides private datasets.
