# Oracle/Registry Asset Audit

## Findings

### Existing registry setup

- No `TRUST_REGISTRY_SOURCE` environment variable was found in the repository.
- Existing adapters/connectors:
  - `mock_registry` connector (`src/trustagents/connectors/mock_registry.py`)
  - `file_source` connector (`src/trustagents/connectors/file_source.py`)
  - optional `http_json` connector (`src/trustagents/connectors/http_json.py`)
- Source requirement config is currently static:
  - `required_sources = ("mock_registry",)` in `src/trustagents/config/settings.py`.

### Oracle jobs

- Async oracle jobs exist behind `async_jobs_enabled` feature flag.
- Jobs are stored in an in-memory job store (`src/trustagents/jobs/store.py`).

### Sanctions and screening sources

- Sanctions-specific feed integration is not present.
- This increment adds sanctions policy handling if `sanctionsMatch` is supplied by claims/source.

### Anchor and receipt verification flow

- Prior to this increment, receipt and anchor steps were not represented in service outputs.
- This increment adds deterministic signed receipt construction and a simulated anchoring record in response output.
- Explicit receipt verification endpoint and revocation lifecycle endpoint are still missing.

## Conclusion

The repository had a deterministic single-source oracle with mock screening and no first-class review queue, case-memory, receipt, or anchor stage modules. This increment introduces those structures while preserving simulation-only boundaries.
