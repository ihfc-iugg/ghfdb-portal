# Architecture decisions

Each record here captures one decision that shapes the codebase, why it was made, and what would
make it worth reopening. They are written for someone who arrives later and wants to know why
something is the way it is before changing it.

A record is never rewritten once it lands. When a later decision overturns an earlier one, the old
record's status changes to point at its replacement and the text stays as it was, so the reasoning
that applied at the time is still readable.

The domain vocabulary these records use is defined in `CONTEXT.md` at the repository root.

| # | Decision |
|---|---|
| [0001](0001-heat-flow-owns-the-model-ghfdb-extracts-it.md) | The heat flow application owns the data model; the GHFDB application extracts from it |
| [0002](0002-published-column-names-are-preserved-exactly.md) | Published column names are preserved exactly inside the GHFDB application |
| [0003](0003-misspelled-published-columns-are-corrected-and-rejected.md) | Misspelled published column names are corrected internally and rejected on input |
| [0004](0004-quality-scores-are-computed-by-the-portal.md) | Quality scores are computed by the portal and are authoritative |
| [0005](0005-import-and-export-formats.md) | Exports use the release format; imports accept the upload template and a full release |
| [0006](0006-a-site-is-its-coordinates.md) | A heat flow site is identified by its coordinates |
| [0007](0007-the-portal-database-holds-current-state.md) | The portal database holds current state; releases are artefacts |
| [0008](0008-one-constitution-one-glossary.md) | One constitution, one glossary, each with a single home |
| [0009](0009-the-project-is-mit-licensed.md) | The project is MIT licensed |

:::{toctree}
:hidden:
:glob:

0*
:::
