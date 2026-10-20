# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
From 2026.8.1 onward this project uses calendar versioning, `<year>.<month>.<release>`.
Releases before that used `<year>.<release>` and are recorded in the
[GitHub releases](https://github.com/ihfc-iugg/ghfdb-portal/releases).

## [Unreleased]

### Added

- Every site, depth interval and measurement page now shows heat flow content as well as
  FairDM's shared page. A child heat flow value shows its method, the thermal gradient and
  interval conductivity it was calculated from, its corrections, its quality card and its parent.
  A thermal gradient and an interval conductivity show their own fields, score and the values that
  use them. A parent shows its heat production correction, comment and GHFDB id, and the children
  its quality rests on. A site lists its depth intervals with the heat flow values determined over
  each, and a depth interval shows its depth, rock, probe and IGSN. Every page made on an interval
  shows the site's location, or says none is recorded. Records in datasets that have not been
  published are counted and never named. Every column of the GHFDB export can be read on one of
  these pages ([record pages](docs/guides/record-pages.md)).
- Container images are published to `ghcr.io/ihfc-iugg/ghfdb-portal` on every
  release, tagged with the version and with `latest`.
- Dependabot pull requests for a given ecosystem now arrive grouped as one pull
  request and merge automatically once their checks pass.

### Changed

- CI, the image build and the release flow call the reusable workflows in
  `FAIR-DM/shared` v0.1.0. The tests, the browser tests and the code quality
  checks run in the FairDM development image against the PostGIS version the
  pinned FairDM declares. The required checks are now `call-tests / Tests`,
  `call-browser-tests / Browser tests`, `call-build / Code Quality`,
  `call-build / Security Scan` and `call-image / Build image`. The package
  build check is gone: the portal ships as an image, not a package.
- The production image is built from a `Dockerfile` at the repository root on
  the FairDM base images, which include GDAL, GEOS and PROJ, instead of
  `deploy/Dockerfile` on `python:3.13-slim`. It serves on port 8000 rather than
  5000, and `deploy/docker-compose.yml` routes to 8000. `refresh_quality` now
  runs after `collectstatic`, as a start step.
- Development and CI run on PostgreSQL 17 with PostGIS 3.5, the version FairDM
  `1c2e0819` declares. Production still runs 16 until its database is upgraded.
  A local database created on 16 has to be dumped and restored, or recreated,
  to start on 17.
- FairDM moves to commit `1c2e0819`, which declares the base image and PostGIS
  version a portal runs on. django-compressor and django-libsass are no longer
  installed, so the image no longer runs `manage.py compress` on start.

- Development and the test suite run on PostgreSQL 16 with PostGIS 3.5, as
  production does, and FairDM moves to commit `c9c12314`, which requires PostGIS
  in every environment and installs GeoDjango. `docker compose up` starts
  PostGIS, Redis, the development server and a Celery worker. Running Django
  outside Docker needs the GDAL, GEOS and PROJ libraries. The test that applies
  every migration to an empty database runs again, and the migrations now apply
  to one. The tests and the build checks run from workflows kept in this
  repository, because the shared ones start no database and install no GDAL.
- FairDM moves to commit `b89656ae`, where a sample holds its own location as a
  WGS 84 point and the shared `Point` table is removed. Upgrading copies every
  sample's coordinates aside before FairDM's migration empties the column and
  writes them back after it, so no site loses its coordinates. That migration
  does not reverse, so take a database backup before deploying. A site is the
  only record that holds coordinates; intervals and measurements are listed at
  their site's coordinates, shown only to someone who may see that site. A
  site's form takes a latitude and a longitude, and its `elevation` stays the
  only elevation. The published `lat_NS` and `long_EW` values do not change.
- `IntervalConductivity.location` is renamed `conductivity_location`, so that it
  no longer clashes with the `location` field FairDM is adding to every
  measurement. Existing values are kept, and the published `tc_location` column
  is unchanged.
- The project is built and developed with uv instead of Poetry, and the shared
  workflows are pinned at v0.6.0. The container image installs its dependencies
  with uv from `uv.lock`. The FairDM packages stay at the commits the previous
  lockfile held.
- Continuous integration now calls the shared workflows in `django-mvp/shared`
  for everything but the tests and the build checks, rather than maintaining
  its own copies. Tests run against the single
  Python 3.13 and Django 5.2 combination the portal is deployed on.
- Releases are prepared by opening a release pull request. Merging it cuts the
  tag, the GitHub release and the container image.
- The container image no longer builds on `ghcr.io/fair-dm/fairdm`, which is no
  longer published. Both stages now build from `python:3.13-slim`.
- The portal now runs on the current FairDM. Sample status values are reset by
  the framework's own migration, because the vocabulary behind that field was
  replaced and no old term maps onto a new one. The portal has never set or
  displayed it.
- FairDM is updated to its current version, which brings django-mvp 0.28.
  Upgrading converts the permissions stored on projects, datasets, samples and
  measurements into access levels and deletes the stored permissions. That
  migration does not reverse, so take a database backup before deploying.
- An anonymous API caller may now make 30 requests a minute and 2,000 a day,
  and a signed-in caller 120 a minute and 20,000 a day, in place of 100 and
  1,000 an hour. API tokens issued before this release stop working. New ones
  are created from the account pages.
- The GHFDB API serves a record only when its dataset is public and published,
  or to a signed-in person listed on the record, its dataset or its project.
  Being listed on a dataset now reaches every record in it.
- The person who starts an assessment is listed on its dataset as its Data Manager,
  and can open, edit and delete it.
- The quality score card is not shown on measurement pages for now. The
  framework replaced the page it was placed on.

### Fixed

- An imported row with a latitude outside -90 to 90 or a longitude outside -180
  to 180 is refused, naming the row and the column, instead of being stored as a
  site.
- Spreadsheet imports no longer fail when every dataset on the portal is
  private. The importer looks up the dataset it should fill, and that lookup had
  started skipping private ones.
- The map viewer no longer collapses to a sliver on narrow screens. It filled
  the page correctly on desktop only by accident, through hand-rolled CSS that
  had no floor for a viewport where the sidebar contributes no height.
- The edit page of a parent heat flow no longer fails with a server error.

### Removed

- The vendored spec-driven-development toolchain, which was a copy of software
  maintained elsewhere.
- The `/map/` address, which named a page that does not exist and always failed.
  The interactive map is at `/ghfdb/explore/`.
- Page templates nothing rendered any more, and the portal's own server error
  page, which drew nothing of its own. The framework's server error page is shown
  instead.

## [2025.21] - 2025-08-14

Releases up to and including 2025.21 predate this changelog. See the
[GitHub releases](https://github.com/ihfc-iugg/ghfdb-portal/releases) for their
history.
