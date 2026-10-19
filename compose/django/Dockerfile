# The development image: Python, uv, and the GDAL, GEOS and PROJ libraries GeoDjango needs.
# The source is mounted at /app by docker-compose.yml, so the image holds the dependencies only.
# The production image is the Dockerfile at the repository root.
FROM python:3.13-slim

# git because fairdm, fairdm-geo and fairdm-discussions are all VCS dependencies.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends gdal-bin git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.18 /uv /usr/local/bin/uv

# The environment lives outside /app, so the mounted source never hides it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

EXPOSE 8000
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
