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
   `deploy/docker-compose.yml`. The Django service carries the Watchtower
   label, so a new `latest` is pulled and the container replaced without anyone
   logging in.
3. The container runs migrations, collects static files, scores any records the current quality
   scheme has not scored, then serves the application with Gunicorn on port 8000 (see *What the
   container runs on start*).

Both the version tag and `latest` are published for every release, so a
rollback is a matter of pinning the service to an exact version.

## What the container runs on start

The base image's entrypoint runs these in order, and each only runs if the one before it succeeded:

1. `python manage.py migrate --noinput`
2. `python manage.py collectstatic --noinput`
3. `python manage.py sync_vocabularies`, from `start/05-sync-vocabularies`
4. `python manage.py refresh_quality`, from `start/10-refresh-quality`
5. `gunicorn`, which serves the application on port 8000 with four workers.

`sync_vocabularies` loads every controlled vocabulary the portal uses. The IHFC heat flow
vocabularies are read from their addresses under `https://w3id.org/ihfc-iugg/vocabularies/`, so
the server must be able to reach `w3id.org` and `ihfc-iugg.github.io`. A new release of them
reaches the portal on its next start, with no portal release. FairDM's own vocabularies, in
`vocabularies/`, ODM2's elevation datum and fairdm-geo's vocabularies ship in the image. If a
vocabulary server does not answer, the step reports it and the portal starts with the terms it
already holds.

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

FairDM encrypts every backup to an OpenPGP public key, and the image refuses to start in
production without one (`fairdm.E700`). Set `BACKUP_PUBLIC_KEY` in `stack.env` to the armoured
public key on one line, with `\n` in place of each line break, as FairDM's
[How to back up a portal](https://github.com/FAIR-DM/fairdm/blob/main/docs/developers/how-to/back-up-a-portal.md)
describes. Keep the private key off the server: without it no backup can be read.

Traefik itself and the `traefik` network are not defined here. They belong to a
separate stack maintained by the GFZ IT team, and this stack joins that network
as an external one.

## Upgrading a database from 2025.21

The `heat_flow` and `ghfdb` migrations start from the schema 2025.21 left, but the heat flow
model they build is a different one. The heat flow records, samples and measurements a 2025.21
database holds are not carried across: they are removed before migrating and uploaded again with
the current import. Accounts, projects, datasets, reviews and literature are kept. The
database also moves from PostgreSQL 16 to PostgreSQL 17 with PostGIS 3.5, which FairDM requires.

FairDM 0.3 stores references with django-literature 0.3 and every vocabulary term by its
address, and its commands that move a database across work only on one that FairDM 0.2.1 has
fully migrated. So the database is first migrated by the last release of the portal on FairDM
0.2.1, and then converted and migrated by the current one. Both run in one-off containers, with
`stack.env` and the `POSTGRES_HOST` of the new database, while the Django service is stopped.
`BACKUP_PUBLIC_KEY` must be set before step 5 (see *Configuration*), because the current image
refuses every command in production without it.

1. Stop the Django service and take a backup of the 2025.21 database:
   `pg_dump -Fc -f /tmp/before-upgrade.dump` in the database container, copied off the server.
2. Start a `postgis/postgis:17-3.5` service with its own new volume, next to the old database,
   and copy the data across from its console:

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

4. Migrate the new database with the last release of the portal on FairDM 0.2.1:

   ```bash
   python manage.py migrate --noinput
   ```

5. Convert it with the current image, running each command in its own one-off container, in this
   order:

   ```bash
   python manage.py repair_references
   python manage.py upgrade_literature
   python manage.py upgrade_vocabularies
   python manage.py sync_vocabularies
   python manage.py upgrade_vocabularies
   ```

   - `repair_references` rewrites the stored identifiers django-literature 0.3 would refuse:
     an ISSN whose leading zeros were lost, an ISBN filed as an ISSN or the other way round, and
     several ISSNs or ISBNs in one field. Each reference keeps its first ISSN and its first ISBN.
     Every other value, and a number or address too long to store, is written into the
     reference's note. It prints each change, and `--dry-run` prints them without writing.
   - `upgrade_literature` moves every reference to django-literature 0.3 and keeps its primary
     key, so assessments and datasets keep their publications. If it names a reference it
     cannot convert, it has changed nothing: correct that reference and run it again.
   - The first `upgrade_vocabularies` creates the vocabulary tables and stops,
     `sync_vocabularies` loads every vocabulary, the IHFC ones from `w3id.org`, which must
     answer for the step to succeed, and the second
     `upgrade_vocabularies` stores every description type, contributor role and keyword by its
     concept's address.

6. Point the Django service at the new database (`POSTGRES_HOST`) and start the current image.
   Its start runs the migrations, loads the vocabularies and scores the records before it serves,
   as described above.
7. Remove the content types of the models the portal no longer has, in the running container.
   It asks before it deletes:

   ```bash
   python manage.py remove_stale_contenttypes
   ```

The database keeps the tables of apps the portal no longer installs (`actstream_*`,
`authtoken_token`, `invitations_invitation`, `laboratory_*`, `orbit_orbitentry` and
`stratigraphy_stratigraphicunit`). Nothing reads them.

The old database and its volume are not written to, so going back means starting the 2025.21
image against them again.

## Local development

Don't use this stack to work on the portal. Run `uv sync` and then
`uv run python manage.py runserver`. The development environment comes from
`stack.development.env` in the repository root.
