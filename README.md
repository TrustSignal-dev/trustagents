# TrustAgents

TrustAgents is a defensive-security research repository for simulated fraud detection in compliance evidence pipelines. It supports proposal review with synthetic artifacts and explicit limits. TrustSignal production controls remain unchanged: artifact hashing, signed receipt issuance, receipt verification, scoped auth, webhook integrity checks, and redaction or partner-gated surfaces are not replaced by this repository.

## TrustAgents R&D Boundary

The `trustagents` oracle service in `src/trustagents/` is:

- experimental
- optional
- non-blocking
- isolated from the production verification dependency chain

Oracle output is advisory and ingestion-ready only. Current repository content does **not** claim production dependency on oracle fusion, chain anchoring, ZKP attestation, or autonomous research agents. Any future integration is gated and documented as future work.

All fixtures and examples are synthetic unless explicitly documented otherwise.

## Repository Map

- `proposal/`: grant-ready summaries, application text, budget, and timeline
- `docs/`: architecture boundaries, schema contracts, methodology, and threat model
- `datasets/`: synthetic schema and sample anomalies
- `simulations/`: scenario catalog and pipeline model
- `agents/`: role definitions for research agents
- `eval/`: benchmark design and metrics
- `src/trustagents/`: isolated experimental oracle evaluation service
- `tests/`: unit, integration, and regression checks for the oracle service
