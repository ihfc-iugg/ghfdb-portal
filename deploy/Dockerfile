# ---------------------------------------------------------------------------
# Stage 1 — build: install production dependencies into an isolated venv
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

ARG POETRY_VERSION=2.3.4
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# build-essential and libpq-dev for packages with C extensions; git because
# fairdm, fairdm-geo and fairdm-discussions are all VCS dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" && \
    poetry self add poetry-plugin-bundle

WORKDIR /build
COPY pyproject.toml poetry.lock README.md ./
COPY project/ ./project/

RUN poetry bundle venv --only=main /venv

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
