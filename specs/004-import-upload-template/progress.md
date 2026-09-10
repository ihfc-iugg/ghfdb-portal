# Progress — 004 Import a completed upload template into a dataset

## 2026-09-11 — Spec gate: approved

Sam approved the specification, with one amendment: fold #190 into this run. The all-or-nothing
refusal in US-4 rests on `rollback_on_validation_errors` being honoured, and today it is declared in
a place the library never reads. Fixing it inside US-4 rather than leaving the guarantee resting on
a declaration that does nothing.

Approved surface: epic #199, stories #200 through #205, draft PR #206, `spec.md` and `decisions.md`
on branch `004-import-upload-template`.
