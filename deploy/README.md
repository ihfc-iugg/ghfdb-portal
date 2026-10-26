# Deployment

The production image is built from the `Dockerfile` at the repository root. This directory holds
the rest of what runs the portal in production.

| File | Purpose |
|---|---|
| `docker-compose.yml` | The production stack: the Django service, PostgreSQL and Redis. |
| `start/` | Start steps the image runs after collecting static files and before serving. |

The image is built on the FairDM base images: dependencies are installed on the development image,
then copied with the code onto the runtime image, which has GDAL, GEOS and PROJ. The base image
version is the one the pinned FairDM declares under `[tool.fairdm.platform]` in its
`pyproject.toml`, passed in as the `FAIRDM_IMAGE_VERSION` build argument, so moving the FairDM pin
moves the image with it. To build it locally:

```bash
docker build --build-arg FAIRDM_IMAGE_VERSION=1.0.0 -t ghcr.io/ihfc-iugg/ghfdb-portal .
```

## How a change reaches the server

1. A release is prepared and tagged, and the Image workflow builds the image
   from the root `Dockerfile` and pushes it to
   `ghcr.io/ihfc-iugg/ghfdb-portal`, tagged with the version and with `latest`.
2. The stack runs on infrastructure operated by GFZ, from
   `deploy/docker-compose.yml`, in Portainer. The Django service runs the exact
   release `PORTAL_VERSION` names, so publishing a release changes nothing on
   the server. Setting `PORTAL_VERSION` to the new version (without the `v`) and
   updating the stack deploys it.
3. The container runs migrations, collects static files, scores any records the current quality
   scheme has not scored, then serves the application with Gunicorn on port 8000 (see *What the
   container runs on start*).

A rollback is setting `PORTAL_VERSION` back, provided the release in between added no
migrations. One that did needs the database backup taken before it.

## What the container runs on start

The base image's entrypoint runs these in order, and each only runs if the one before it succeeded:

1. `python manage.py migrate --noinput`
2. `python manage.py collectstatic --noinput`
3. `python manage.py refresh_quality`, from `start/10-refresh-quality`
4. `gunicorn`, which serves the application on port 8000 with four workers.

`refresh_quality` recalculates the [quality scores](../docs/guides/quality-scores.md) of every
gradient, conductivity, child and parent whose stored scheme revision is not the current one.
On the first start after this feature is released that is every record the database holds. Each
record is read and written on its own, in chunks of 500, and the tests measure about 18 queries
for each determination (its gradient, conductivity, child and parent), so a release of about
90,000 determinations makes on the order of 1.6 million queries. Nobody has timed it against the
production database, so expect the first start to take a while before the site answers, and
watch the container's log for the counts it reports. Later starts find every record already
scored and finish at once, unless a release changes the scheme revision.

An error in `refresh_quality` stops the container from starting. The command exits with an error,
the entrypoint stops before Gunicorn, and the container restarts (`restart: always`) and tries
again, so the site stays down until the error is fixed or the service is pinned to the previous
version (see *How a change reaches the server*). Each record is stored on its own, so the next run
carries on with the ones still unscored.

To repair scores by hand, after a write that skipped the portal's code, run
`python manage.py refresh_quality --all` in the running container.

## Configuration

The stack reads its environment from `stack.env`, which is held on the server
and is deliberately not in this repository. `DJANGO_SITE_DOMAIN` sets the host
Traefik routes, and the same value appears in the certificate request.
`PORTAL_VERSION` names the release the Django service runs.

The compose file sets `POSTGRES_HOST` and `REDIS_URL` itself, to the `postgis` and `redis`
services. Without `REDIS_URL` there is no shared cache, and sign-in rate limiting refuses every
attempt. Leave `DJANGO_SETTINGS_MODULE` out of `stack.env`: the image sets it.

Traefik itself and the `traefik` network are not defined here. They belong to a
separate stack maintained by the GFZ IT team, and this stack joins that network
as an external one.

## Upgrading a database from 2025.21

The `heat_flow` and `ghfdb` migrations start from the schema 2025.21 left, but the heat flow
model they build is a different one. The heat flow records, samples and measurements a 2025.21
database holds are not carried across: they are removed before migrating and uploaded again with
the current import. Accounts, projects, datasets, reviews and literature are kept. The
database also moves from PostgreSQL 16 to PostgreSQL 17 with PostGIS 3.5, which FairDM requires.

1. Stop the Django service and take a backup of the 2025.21 database:
   `pg_dump -Fc -f /tmp/before-upgrade.dump` in the database container, copied off the server.
2. Add the `postgis` service from `deploy/docker-compose.yml`, with its new volume, next to the
   old `postgres` service, and copy the data across from the `postgis` console:

   ```bash
   PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h postgres -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" \
     | pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges
   ```

3. Remove the heat flow records, samples and measurements in the new database, with
   `psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"`:

   ```sql
   DO $$
   DECLARE t text;
   BEGIN
     FOR t IN
       SELECT quote_ident(table_name) FROM information_schema.tables
       WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
         AND (table_name LIKE 'heat\_flow\_%' OR table_name LIKE 'measurement\_%'
              OR table_name LIKE 'sample\_%')
     LOOP
       EXECUTE 'TRUNCATE ' || t || ' RESTART IDENTITY CASCADE';
     END LOOP;
   END $$;
   ```

4. Update the stack to `deploy/docker-compose.yml`, with `PORTAL_VERSION` set to the new release.
   The Django service starts on the new database, and its start runs the migrations and the
   quality scores before it serves, as described above.

The old database and its volume are not written to, so going back means starting the 2025.21
image against them again.

## Local development

Don't use this stack to work on the portal. Run `uv sync` and then
`uv run python manage.py runserver`. The development environment comes from
`stack.development.env` in the repository root.
