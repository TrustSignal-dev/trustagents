# Phased Implementation Plan

## Phase 1: Observable and Verifiable (Current)

Make the existing pipeline observable and complete the receipt lifecycle.

### Deliverables

- [x] Structured logging module (`observability/logging.py`)
- [x] Logging instrumentation throughout the oracle pipeline
- [x] Receipt verification endpoint (`POST /api/v1/oracle/receipts/verify`)
- [x] Receipt revocation endpoint (`POST /api/v1/oracle/receipts/revoke`)
- [x] Receipt status lookup endpoint (`GET /api/v1/oracle/receipts/{receipt_id}`)
- [x] In-memory receipt store (`receipts/store.py`)
- [x] Structured error response model (`api/errors.py`)
- [x] Retry wrapper for HTTP connector (`connectors/retry.py`)
- [x] Compliance-gap risk flag in the pipeline
- [x] Tests for all new code
- [x] Updated API contract and architecture documentation

### Acceptance Criteria

- All 24 existing tests continue to pass
- New endpoints return structured responses
- Receipt verification detects valid, invalid, and revoked receipts
- Structured logs emitted at each pipeline stage boundary
- HTTP connector retries transient failures with exponential backoff

## Phase 2: Durable and Configurable (Proposed)

Replace in-memory stores with pluggable persistence abstractions.

### Deliverables (Proposed)

- [ ] Storage interface protocol for receipt store, review queue, case memory, job store
- [ ] File-backed implementations for local simulation
- [ ] Configuration for multi-source registry selection
- [ ] HMAC-based receipt signatures (replacing plain SHA-256)
- [ ] Request payload size limits
- [ ] Rate limiting middleware
- [ ] Metrics collection hooks (counters for evaluations, receipts, revocations)

### Acceptance Criteria (Proposed)

- Stores survive process restarts when file-backed
- Receipt signatures verified with HMAC
- Metrics exposed at `/metrics` (Prometheus-compatible)

## Phase 3: Integrated and Hardened (Proposed)

Connect trustagents to the TrustSignal core workflow.

### Deliverables (Proposed)

- [ ] TrustSignal handoff export (feature-flagged, `trustsignal_handoff_export_enabled`)
- [ ] Webhook notifications for receipt status changes
- [ ] External anchor network integration interface
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Container image (Dockerfile)
- [ ] API versioning strategy for v2 evolution
- [ ] Load testing and latency benchmarks
- [ ] Security review and penetration testing scope

### Acceptance Criteria (Proposed)

- End-to-end flow from TrustSignal collect through verify/review
- Webhook delivery for receipt lifecycle events
- CI pipeline runs tests on every PR
- Container image builds and starts successfully

## Phase 4: Learning-Assisted (Proposed)

Enable optional model-assisted scoring with explicit approval gates.

### Deliverables (Proposed)

- [ ] Offline retraining workflow with approval gates
- [ ] A/B scoring comparison (deterministic vs. hybrid)
- [ ] Model version promotion workflow
- [ ] Drift detection and alerting
- [ ] Formal evaluation against CEID benchmark suite

### Acceptance Criteria (Proposed)

- No autonomous threshold changes
- All model updates require explicit version bumps
- Drift detection alerts when scoring distributions shift

## Current Status

Phase 1 is implemented in this increment. Phases 2–4 are proposed and documented
for future planning. No claims of production readiness are made for capabilities
that are not yet implemented.
