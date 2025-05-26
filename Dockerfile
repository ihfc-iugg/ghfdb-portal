
FROM python:3.11-slim-bullseye as builder
ARG POETRY_VERSION=2.1
ENV DJANGO_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install --no-install-suggests --no-install-recommends && \
    pip install poetry==${POETRY_VERSION} && \
    poetry self add poetry-plugin-bundle

COPY pyproject.toml poetry.lock LICENSE README.md ./
RUN poetry bundle venv $(test "$DJANGO_ENV" == production && echo "--only=main") /venv

# Second stage: Copy application and dependencies to final image
FROM ghcr.io/fair-dm/fairdm:latest AS run-stage
ARG DJANGO_ENV=production

ENV DJANGO_ENV=production
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

COPY --from=builder --chown=django:django /venv /venv

# copy application code to WORKDIR
COPY --chown=django:django . /app

# RUN DJANGO_ENV="development" \
    # python manage.py compilemessages
