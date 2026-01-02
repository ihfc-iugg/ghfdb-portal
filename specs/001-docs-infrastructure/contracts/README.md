# Contracts (Phase 1)

This feature introduces no runtime service/API contracts.

- See [openapi.yaml](openapi.yaml) for an explicit “no endpoints” contract artifact.
- The effective contract is CI behavior:
  - docs build warnings are treated as failures
  - linkcheck failures block merge
