# ADR 0017 — A role carries the trust that decides publication, not a per-person setting

**Status:** accepted

## Decision

Two roles govern the assessment upload workflow. A Data Curator's upload becomes public the moment
they confirm it. A Data Assessor's stays private and waits for a curator to approve it or send it
back. Nothing else about the two paths differs, and there is no per-person trust setting.

## Why

The assessment team is not one kind of person. A few experienced assessors carry the database, and
alongside them are PhD students and student helpers who arrive for a semester and leave. The reason a
publication gate was wanted at all is that the second group's work needs a second pair of eyes before
it reaches anyone.

The roadmap had previously called for data from team members to publish without waiting. Taken
literally that exempts exactly the people the gate exists for, so it is superseded here.

The alternative is a flag on each person. That brings an administrative surface for granting and
revoking it, a decision about who may grant it, a second path through the workflow for the trusted
case, and a new way for the two paths to drift apart. A role already expresses the same distinction
and is already how the portal decides who may reach which page.

## Revisit if

The team grows to the point where "experienced enough to publish unreviewed" stops tracking role
membership — for instance if curators take on duties that have nothing to do with data quality, or if
some assessors become permanent staff whose work nobody checks in practice.
