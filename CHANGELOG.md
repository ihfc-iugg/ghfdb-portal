# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
From 2026.8.1 onward this project uses calendar versioning, `<year>.<month>.<release>`.
Releases before that used `<year>.<release>` and are recorded in the
[GitHub releases](https://github.com/ihfc-iugg/ghfdb-portal/releases).

## [Unreleased]

### Added

- Container images are published to `ghcr.io/ihfc-iugg/ghfdb-portal` on every
  release, tagged with the version and with `latest`.
- Dependabot pull requests for a given ecosystem now arrive grouped as one pull
  request and merge automatically once their checks pass.

### Changed

- Continuous integration now calls the shared workflows in `django-mvp/shared`
  rather than maintaining its own copies. Tests run against the single
  Python 3.13 and Django 5.2 combination the portal is deployed on.
- Releases are prepared by opening a release pull request. Merging it cuts the
  tag, the GitHub release and the container image.
- The container image no longer builds on `ghcr.io/fair-dm/fairdm`, which is no
  longer published. Both stages now build from `python:3.13-slim`.

### Removed

- The vendored spec-driven-development toolchain, which was a copy of software
  maintained elsewhere.

## [2025.21] - 2025-08-14

Releases up to and including 2025.21 predate this changelog. See the
[GitHub releases](https://github.com/ihfc-iugg/ghfdb-portal/releases) for their
history.
