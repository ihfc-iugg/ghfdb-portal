# ---------------------------------------------------------------------------
# Stage 1 — build: install production dependencies into an isolated venv
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

# build-essential and libpq-dev for packages with C extensions; git because
# fairdm, fairdm-geo and fairdm-discussions are all VCS dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.18 /uv /usr/local/bin/uv

WORKDIR /build

# Third-party dependencies first, so this layer is reused until uv.lock or the
# dependency list changes. --locked fails the build when uv.lock is out of date
# with pyproject.toml, and --no-dev leaves out the test, lint and docs tooling.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

# Then the project's own packages, installed into the same venv.
COPY project/ ./project/
RUN uv sync --locked --no-dev --no-editable

# ---------------------------------------------------------------------------
# Stage 2 — runtime: minimal image with app code and bundled venv
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYDEVD_DISABLE_FILE_VALIDATION=1 \
    DJANGO_ENV=production \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/venv/bin:$PATH"

# libpq5 for psycopg2. No geospatial libraries: FairDM has deprecated its
# geospatial functionality, and fairdm.contrib.location.Point is now a plain
# model with decimal x/y and a CRS string, so nothing loads GDAL, GEOS or PROJ.
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 django \
    && useradd --uid 1000 --gid django --shell /bin/bash --create-home django

COPY --from=builder /venv /venv

WORKDIR /app
COPY --chown=django:django . /app
RUN mkdir -p /app/static /app/media && chown -R django:django /app/static /app/media

USER django

EXPOSE 5000

# Port 5000 is what the traefik labels in docker-compose.yml route to.
# collectstatic and compress run at start because they need the runtime
# environment injected by Compose, not the values present at build time.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py compress && exec gunicorn config.wsgi:application --bind 0.0.0.0:5000 --workers 4"]
