
# ====================== BUILD STAGE ============================
FROM geoluminate as build-stage
ARG PROJ_DIR=/world-heat-flow-database

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY .${PROJ_DIR}/requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r local.txt

# ====================== RUN STAGE ============================
FROM geoluminate as run-stage
ARG PROJ_DIR=/world-heat-flow-database

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_DIR}

# copy python dependency wheels from python-build-stage
COPY --from=build-stage /usr/src/app/wheels /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
	&& rm -rf /wheels/

COPY .${PROJ_DIR}/compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
