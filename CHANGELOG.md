# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
From 2026.8.1 onward this project uses calendar versioning, `<year>.<month>.<release>`.
Releases before that used `<year>.<release>` and are recorded in the
[GitHub releases](https://github.com/ihfc-iugg/ghfdb-portal/releases).

## [Unreleased]

### Added

- `manage.py repair_references` rewrites the stored DOI, ISSN and ISBN of every reference that
  django-literature 0.3 would refuse to convert: a DOI written as an address, an ISSN that lost
  its leading zeros, an ISSN and an ISBN in each other's field, and several of one in one field.
  Each reference keeps its first ISSN and first ISBN, and every other value is written into its
  note. It prints each change, and `--dry-run` writes nothing.
- A public table of the GHFDB parents at `ghfdb/parents/`, one row per parent in the published
  column names, sortable by every column and paged at 100 rows. It can be filtered by ranges on
  heat flow, its uncertainty, elevation, both total depths, latitude and longitude, by environment,
  exploration method and purpose, heat production correction, U-score and M-score, by site name,
  and by project and dataset, and the address holds the filters. Each row shows its children as
  "n (m)", m being those marked relevant, and selecting the count opens a window listing them.
  The sidebar's map viewer entry is now a collapsible GHFDB group holding the map viewer and the
  table.
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
- A researcher can correct a heat flow site on its edit page instead of re-uploading the
  spreadsheet. The form groups the site's fields the way the upload template orders its columns,
  takes a vocabulary term as text written the way the published file writes it, and keeps a
  stored term that is saved untouched. A site keeps the true vertical depth entered for it, and a
  location another site already holds is refused beside the coordinates
  ([editing records](docs/guides/editing-records.md)).
- A researcher can correct a child heat flow on its edit page: its value, uncertainty, method,
  comment and acquisition details, the status of each of its nine corrections, and the thermal
  gradient and interval conductivity it was calculated from. A gradient or conductivity on another
  depth interval is refused. Each correction offers only the statuses valid for it, and saving
  recalculates the child's quality score ([editing records](docs/guides/editing-records.md)).
- A researcher can correct a depth interval on its edit page, with the marine probe it was
  measured with: probe penetration, length and tilt are checked against the same limits as the
  probe record, and the probe types are chosen from the vocabulary. A thermal gradient and an
  interval conductivity each have a form of their own, with every value entered next to its
  uncertainty and one unit for both, and saving recalculates the scores that rest on them
  ([editing records](docs/guides/editing-records.md)).
- A researcher can mark which children a site's parent heat flow rests on, on the parent's edit
  page, together with its value, uncertainty, heat production correction and comment. A child at
  another site is refused, a child in a dataset the researcher may not change keeps its relevance,
  and saving recalculates the parent's quality from the children now marked
  ([editing records](docs/guides/editing-records.md)).
- Container images are published to `ghcr.io/ihfc-iugg/ghfdb-portal` on every
  release, tagged with the version and with `latest`.
- Dependabot pull requests for a given ecosystem now arrive grouped as one pull
  request and merge automatically once their checks pass.

### Changed

- The portal moves to FairDM v0.3.1 and django-literature 0.3.2, installed from PyPI, with
  fairdm-geo at the commit that moves it to the same release. FairDM no longer installs django-research-vocabs, so every vocabulary
  term the portal stores is the address of a concept in a published vocabulary, held through
  django-controlled-vocabularies. The heat flow fields use the IHFC vocabularies at their
  addresses under `https://w3id.org/ihfc-iugg/vocabularies/`, and the image reads them from
  those addresses with `sync_vocabularies` each time it starts, before it scores records. A
  start whose vocabulary server does not answer keeps the terms already loaded. FairDM's
  own vocabularies are read from their addresses under `https://w3id.org/fairdm/vocabularies/`.
  No vocabulary is kept in the repository. The temperature method vocabulary gains `DST` and `cDST`.
- A site no longer has an elevation datum, which went with the vocabulary fairdm-geo dropped. Its
  elevation is in metres above mean sea level, and the site page, its edit form and the API no
  longer show a datum.
- The API gives a vocabulary term with the same `name`, `label`, `uri` and `vocabulary` as
  before, and the `uri` is now the term's address under `w3id.org/ihfc-iugg/vocabularies/`. A site's
  `type`, `environment` and `explo_method` are written as a term's name or
  its address ([records API](docs/guides/heat-flow-records-api.md)).
- The environment, exploration method and exploration purpose filters of the GHFDB parents
  table and of the administration pages take a term's address in the page address.
- An assessment's publication is a django-literature 0.3 reference. A bibliography file the
  catalogue cannot read is refused on the assessment form instead of being stored.
- Upgrading a 2025.21 database takes two steps: it is migrated by the last release on FairDM
  0.2.1, then converted with `repair_references`, `upgrade_literature`,
  `upgrade_vocabularies` and `sync_vocabularies` before the current image starts
  ([upgrading from 2025.21](deploy/README.md#upgrading-a-database-from-202521)).
- A site's and a depth interval's vertical datum is chosen from the top of the hole or mean sea
  level, and starts at the top of the hole, as fairdm-geo now defines it.
- A production portal needs `BACKUP_PUBLIC_KEY`, the public key FairDM encrypts its backups to
  ([deploy](deploy/README.md#configuration)).
- The `heat_flow` and `ghfdb` migrations start again from the schema 2025.21 left. Each app
  keeps the migrations 2025.21 applied, and new ones take that schema to the current models
  (`heat_flow` 0004 and 0005, `ghfdb` 0003). A database upgraded from 2025.21 has its heat
  flow records, samples and measurements removed before migrating, and they are uploaded again
  with the current import. Accounts, projects, datasets, reviews and literature are kept
  ([upgrading from 2025.21](deploy/README.md#upgrading-a-database-from-202521)). A development
  database built on an earlier unreleased migration has to be recreated.
- `config/settings.py` no longer adds `makemigrations` to the commands `manage.py setup` runs.
- Saving, importing or deleting heat flow records recalculates their quality scores with the same
  number of reads for many records as for one. The interval, site, probe metadata, vocabulary
  terms and corrections each score reads are fetched with the records, where each record had
  fetched its own. `refresh_quality` shares the same reads.
- `seed_demo_data` loads the controlled vocabularies with `sync_vocabularies` on each run.
- The portal moves to Django 6.0 and FairDM v0.2.1. FairDM no longer depends on django-select2,
  django-autocomplete-light or django-addanother, and chooses records with django-tomselect, so
  the last two leave the lockfile. django-mvp moves to 0.31, and django-mvp-accounts,
  django-mvp-charts, django-mvp-compliance and django-mvp-forms move to their newer releases.
  fairdm-geo moves to the commit that declares its depth interval constraint as Django 6.0
  requires.
  The publication and assessor fields on the assessment form use Tom Select in place of
  Select2, which FairDM no longer installs. FairDM's development accounts are now at
  `example.com`, so `seed_demo_data` shares `regular.user@example.com` with them.
- A correction with no status is stored with an empty status instead of `-`. The published
  file still reads and writes `-`, and the API gives
  `null` for the status of such a correction and still lists it
  ([importing data](docs/guides/importing-data.md),
  [records API](docs/guides/heat-flow-records-api.md)).
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
  WGS 84 point and the shared `Point` table is removed. A site is the
  only record that holds coordinates; intervals and measurements are listed at
  their site's coordinates, shown only to someone who may see that site. A
  site's form takes a latitude and a longitude, and its `elevation` stays the
  only elevation. The published `lat_NS` and `long_EW` values do not change.
- `IntervalConductivity.location` is renamed `conductivity_location`, so that it
  no longer clashes with the `location` field FairDM is adding to every
  measurement. The published `tc_location` column is unchanged.
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
