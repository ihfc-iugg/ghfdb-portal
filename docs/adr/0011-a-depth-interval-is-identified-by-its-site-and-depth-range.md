# ADR 0011 — A depth interval is identified by its site and depth range

**Status:** accepted

## Decision

A depth interval is identified by the site it belongs to together with the depth range reported for
it. Every determination measured over that range attaches to the same interval record.

A row that reports no depth range attaches to a single indeterminate interval for its site, which
stays distinct from any interval carrying a real range.

Probe metadata belongs to the interval and is created once for it. Where two rows share an interval
and disagree about the interval's own values, the file is refused and the disagreement is named.

## Why

An interval is a sample in its own right, and a sample can be measured more than once. A heat flow
derived from a fresh conductivity or a fresh gradient over a range another team already measured is
measuring the same piece of ground. It has to attach to the same interval.

In the 2024 release, 8,145 intervals carry more than one determination, covering 21,722 rows — a
quarter of the file. Of those groups, 68 per cent disagree on the determination's own heat flow
value and 49 per cent were reported by different publications. This is not a rare shape.

The alternative considered was giving each determination its own interval. It is tempting because
it would make every dependent record reachable from the determination's identifier, which is
otherwise the hard part of reading a release. It was rejected because it is wrong about what an
interval is: it would record two samples where the science has one, and it would do so silently, at
a quarter of the file.

The release offers no interval identifier of its own, so the identity has to be built from what the
row states. Site and depth range are the only values that describe the interval rather than the
measurement made over it.

## Revisit if

A release edition begins publishing an interval or sample identifier, which would replace this
derived identity with a stated one.
