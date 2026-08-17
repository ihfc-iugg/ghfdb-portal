# ADR 0004 — Quality scores are computed by the portal and are authoritative

**Status:** accepted

## Decision

The portal calculates the U-score, the M-score, the perturbation flags and the composite quality
code from the data it holds. The value it calculates is the authoritative one.

Quality codes present in an imported file are rejected. They are not stored, not stored alongside
the computed value, and not used as a fallback when computation is not possible.

## Why

A quality code is derived, not observed. Every input to it is already imported and held here: the
uncertainty, the measurement method, the conductivity determination and the corrections applied. So
the portal can compute the score itself, and recompute it whenever the underlying data is corrected.
A code supplied by someone else cannot be recomputed, cannot be explained from the record it sits
on, and goes stale silently the moment any input to it changes.

Holding both a supplied and a computed code was considered and rejected. Two quality values on one
record invites the question of which is shown, and any answer to that question is wrong somewhere.

## Revisit if

The portal's scoring falls behind the published scheme far enough that its output would mislead. As
of this decision the implementation follows Fuchs et al. (2023) while the community's current
toolbox is Dergunova et al. (2026); closing that gap is open work, and it is a reason to update the
computation, not to import someone else's result.
