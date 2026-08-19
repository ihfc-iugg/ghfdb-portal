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
3. The container runs migrations, collects static files and compresses assets
   on start, then serves the application with Gunicorn on port 5000.

Both the version tag and `latest` are published for every release, so a
rollback is a matter of pinning the service to an exact version.

## Configuration

The stack reads its environment from `stack.env`, which is held on the server
and is deliberately not in this repository. `DJANGO_SITE_DOMAIN` sets the host
Traefik routes, and the same value appears in the certificate request.

Traefik itself and the `traefik` network are not defined here. They belong to a
separate stack maintained by the GFZ IT team, and this stack joins that network
as an external one.

## Local development

Don't use this stack to work on the portal. Run `poetry install` and then
`python manage.py runserver`. The development environment comes from
`stack.development.env` in the repository root.
