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

Traefik itself and the `traefik` network are not defined here. They belong to a
separate stack maintained by the GFZ IT team, and this stack joins that network
as an external one.

## Local development

Don't use this stack to work on the portal. Run `uv sync` and then
`uv run python manage.py runserver`. The development environment comes from
`stack.development.env` in the repository root.
