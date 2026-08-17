# ADR 0003 — Misspelled published column names are corrected internally and rejected on input

**Status:** accepted

## Decision

Two names in the published structure are misspelled: `tc_pT_fuction`, which should be
`tc_pT_function`, and `Ref_ISGN`, which should be `Ref_IGSN` (an IGSN being an International Geo
Sample Number).

The portal uses the correct spellings internally. A file whose header carries either misspelled
form is rejected with an error identifying it as an outdated template, rather than being silently
accepted and mapped.

## Why

Both misspellings are present in the currently distributed upload template and in the 2024 release
file, so in practice most incoming files carry them. Silently accepting them would work, and it
would also make the errors permanent: every downstream consumer, every future template revision and
every piece of documentation would inherit them, and the cost of correcting them would grow with
each release.

Rejecting loudly puts the correction in front of the only people who can make it, and does so at
the moment the problem is concrete rather than abstract.

This is deliberately stricter than the alternative of quietly translating both spellings. That
alternative removes the immediate friction and removes the pressure to fix anything.

## Revisit if

The published template is corrected upstream. At that point the rejection rule can narrow to a
migration aid for files produced against older templates.
