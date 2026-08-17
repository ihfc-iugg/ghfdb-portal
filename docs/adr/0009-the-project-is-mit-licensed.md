# ADR 0009 — The project is MIT licensed

**Status:** accepted

## Decision

The portal's own source is released under the MIT licence. `LICENSE` at the repository root is the
single statement of that, and `pyproject.toml` declares the same.

The project was licensed under GPL-3.0 until 2 January 2026, when commit `f9dbf8e` relicensed it to
MIT. That change replaced the licence text and updated the packaging metadata, but left a second
GPL-3.0 notice behind in a file named `COPYING`. That file is removed; it never described the
project's terms after January 2026.

## Why

The relicensing commit gives its own reasoning: as the sole code contributor, a permissive licence
serves community adoption and lets other projects integrate the work. That reasoning stands. This
record exists because the decision itself was never written anywhere durable.

The consequence of that gap is what prompted this record. A residual GPL-3.0 file sat in the
repository root for seven months alongside an MIT `LICENSE`, and nothing in the repository said
which was correct. Reconstructing the answer meant reading commit history. The declaration a reader
finds first should not depend on which file they open.

Two things worth noting for anyone reading this later:

- Copies obtained before January 2026 were received under GPL-3.0, and those grants stand. This
  record concerns the terms the project offers now, not a claim about the past.
- The removed file named the Helmholtz Centre Potsdam GFZ as a joint copyright holder, where
  `LICENSE` names only the author. Deleting the file does not settle that question either way. It
  is a matter between the author and the institution, not something the repository decides.

## Revisit if

Contributors other than the copyright holder acquire a material stake in the codebase, or an
institutional policy is adopted that specifies licensing terms for work of this kind. Either would
make the licence a decision with more than one party to it.

Separately, note that the published container image bundles third-party dependencies under
copyleft terms. That is a question about the distributed artefact rather than about this source,
and it is tracked on its own.
