# FS-008 decisions

Rationale too long to inline in the spec, and ambiguities resolved without asking.

## The FairDM pins move with this feature

When this feature was specified, `fairdm`, `fairdm-geo` and `fairdm-discussions` were pinned at
the head of their default branches. `fairdm-docs` was behind (`bead56e` against `847fee1`). The
build moves the `fairdm-docs` pin to the latest commit and re-checks every FairDM pin against its
default branch before it starts. It moves any pin that has fallen behind and confirms the
documentation build afterwards.

## Generated, not sampled

A sample of the published release would look more real, but it would bring the release's licence
and attribution with it. Its size would be capped at the release's size, and loading release rows
is the direction ADR-0010 closed. Generated data has none of those costs. FR-005 asks for
distributions that resemble the published database, which keeps it realistic.

## Size is counted in datasets

Sites, intervals and children vary too much per publication to make a good unit. A dataset is what
a person browses and what the assessment workflow acts on, so it is the number a developer can
reason about.
