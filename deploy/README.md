# Deployment

Everything needed to run the portal in production lives in this directory.

| File | Purpose |
|---|---|
| `Dockerfile` | The production image. Two stages: dependencies are bundled into an isolated virtualenv, then copied into a slim runtime layer. |
| `docker-compose.yml` | The production stack: the Django service, PostgreSQL and Redis. |

## How a change reaches the server

1. A release is prepared and tagged, and the Publish workflow builds the image
   from `deploy/Dockerfile` and pushes it to
   `ghcr.io/ihfc-iugg/ghfdb-portal`, tagged with the version and with `latest`.
2. The stack runs on infrastructure operated by GFZ, from
   `deploy/docker-compose.yml`. The Django service carries the Watchtower
   label, so a new `latest` is pulled and the container replaced without anyone
   logging in.
3. The container runs migrations, scores any records the current quality scheme has not
   scored, collects static files and compresses assets on start, then serves the application
   with Gunicorn on port 5000 (see *What the container runs on start*).

Both the version tag and `latest` are published for every release, so a
rollback is a matter of pinning the service to an exact version.

## What the container runs on start

The image's `CMD` runs these in order, and each only runs if the one before it succeeded:

1. `python manage.py migrate --noinput`
2. `python manage.py refresh_quality`
3. `python manage.py collectstatic --noinput`
4. `python manage.py compress`
5. `gunicorn`, which serves the application on port 5000.

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
the shell chain stops before Gunicorn, and the container restarts (`restart: always`) and tries
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
