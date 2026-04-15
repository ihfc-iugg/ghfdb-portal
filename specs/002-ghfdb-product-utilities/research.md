# Research: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-13
**Status**: Complete

## Architecture Notes

The proxy model design required no significant architecture decisions beyond standard Django patterns:

- **`GHFDB` proxy over `HeatFlow`**: No new table; manager assigned via `objects = GHFDBManager()`. Excludes FairDM registry (admin-only; no auto-generated views required).
- **`GHFDBQuerySet.as_ghfdb_flat()`**: Uses `select_related` + `F()` annotations to fold all scalar GHFDB columns into a single queryset. Correction flags use correlated `Subquery` expressions (one per correction type). Constant =2 queries regardless of row count.
- **`GHFDBQuerySet.for_export()`**: Extends `as_ghfdb_flat()` with `prefetch_related` for all 14 M2M relations. Constant ~16 queries regardless of row count. Consumed downstream by ``003-ghfdb-import-export``.
- **`explo_purpose` list filter (BUG-001)**: Implemented as a `SimpleListFilter` whose choices are scoped to values accepted by `HeatFlowSite.explo_purpose`, preventing generic `Concept` values from appearing.

## Import/Export Architecture

All R01–R07 architecture decisions concern the import/export pipeline and have been moved to `003-ghfdb-import-export/research.md`.
