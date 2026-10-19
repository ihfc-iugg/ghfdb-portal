# The portal's production image, built on the FairDM base images. Build from the repository root:
#
#   docker build --build-arg FAIRDM_IMAGE_VERSION=<image version> -t ghcr.io/ihfc-iugg/ghfdb-portal .
#
# FAIRDM_IMAGE_VERSION is the `image` version under [tool.fairdm.platform] in the pyproject.toml of
# the FairDM that uv.lock pins. It is not FairDM's own version, and it has no default. The Image
# workflow reads it and passes it in.
ARG FAIRDM_IMAGE=ghcr.io/fair-dm/fairdm
ARG FAIRDM_IMAGE_VERSION

# Install the locked dependencies on the development image, which has git and a compiler.
FROM ${FAIRDM_IMAGE}:${FAIRDM_IMAGE_VERSION}-dev AS build
COPY --chown=fairdm:fairdm pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY --chown=fairdm:fairdm . .
RUN uv sync --locked --no-dev --no-editable

# Run on the runtime image, which has neither. Its entrypoint migrates, collects static files,
# runs the start steps in /docker-entrypoint.d, then serves with gunicorn on $PORT (8000).
FROM ${FAIRDM_IMAGE}:${FAIRDM_IMAGE_VERSION}
# The base image sets the first two already. They are repeated because the site depends on them:
# config/development.py, which relaxes the host and cookie settings, must never load here.
ENV DJANGO_ENV=production \
    DJANGO_SETTINGS_MODULE=config.settings \
    GUNICORN_CMD_ARGS="--workers 4"
COPY --from=build /opt/venv /opt/venv
COPY --chmod=755 deploy/start/ /docker-entrypoint.d/
COPY --chown=fairdm:fairdm . /app
