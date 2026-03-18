# Target Architecture: TrustSignal Integration

## Design Principles

1. **API-first** — All interactions go through versioned HTTP endpoints
2. **Lifecycle-aligned** — collect → receipt → verify → review
3. **Data-minimizing** — Fingerprints over raw data; bounded traces; no PII storage
4. **Observable** — Structured logging, metrics hooks, correlation IDs
5. **Deterministic** — Same input + same versions = same output
6. **Resilient** — Retry, graceful degradation, compliance-gap awareness
7. **Testable** — Every stage independently testable with synthetic data
8. **Non-blocking** — TrustSignal core flows continue if trustagents is unavailable

## Lifecycle Mapping

```
TrustSignal Core          trustagents Oracle
─────────────────         ──────────────────────────
Collect evidence    →     POST /evaluate (intake, fingerprint, screen)
                    ←     OracleDecision + SignedReceipt

Verify receipt      →     POST /receipts/verify
                    ←     ReceiptVerification (valid/invalid/revoked)

Revoke receipt      →     POST /receipts/revoke
                    ←     ReceiptRevocation (confirmed)

Lookup receipt      →     GET  /receipts/{receipt_id}
                    ←     ReceiptStatus (current state)

Operator review     →     GET  /review-queue
                    →     POST /review-cases
                    →     POST /review-feedback
                    ←     ReviewedCaseRecord
```

## Module Boundaries

```
src/trustagents/
├── api/
│   ├── app.py              FastAPI application factory
│   ├── routes.py           All endpoint definitions
│   └── errors.py           Structured error responses      [NEW]
├── oracle/
│   ├── models.py           Pydantic schemas (CamelModel)
│   ├── service.py          Pipeline orchestration
│   └── stages/
│       ├── intake.py       Canonical fingerprinting
│       ├── retrieval.py    Source screening
│       ├── receipt.py      Receipt generation + verification [EXTENDED]
│       ├── anchoring.py    Anchor construction
│       └── review.py       Review routing
├── auth/helpers.py         Tenant guards, idempotency
├── config/settings.py      Feature flags, tuning
├── connectors/
│   ├── mock_registry.py    Synthetic source
│   ├── file_source.py      JSON file source
│   ├── http_json.py        HTTP source with retry          [EXTENDED]
│   └── retry.py            Retry/backoff wrapper           [NEW]
├── adjudication/core.py    Status resolution
├── comparators/core.py     Field comparison
├── extractors/core.py      Claim extraction
├── ingestion/core.py       Canonical JSON + fingerprint
├── normalizers/core.py     Field normalization
├── observability/
│   └── logging.py          Structured logging              [NEW]
├── policies/core.py        Policy evaluation
├── provenance/trace.py     Audit trace assembly
├── receipts/
│   └── store.py            Receipt lifecycle store         [NEW]
├── review/store.py         Review queue
├── risk/
│   ├── core.py             Risk flag generation
│   └── scoring.py          Fraud risk computation
├── jobs/store.py           Async job tracking
└── learning/case_memory.py Pattern similarity
```

## API Surface (v1)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/healthz` | Health check |
| POST | `/api/v1/oracle/evaluate` | Synchronous evaluation |
| POST | `/api/v1/oracle/jobs` | Async job creation |
| GET | `/api/v1/oracle/jobs/{job_id}` | Job status/result |
| POST | `/api/v1/oracle/receipts/verify` | Verify a receipt | **NEW** |
| POST | `/api/v1/oracle/receipts/revoke` | Revoke a receipt | **NEW** |
| GET | `/api/v1/oracle/receipts/{receipt_id}` | Receipt status lookup | **NEW** |
| GET | `/api/v1/oracle/review-queue` | List review queue items |
| POST | `/api/v1/oracle/review-cases` | Record reviewed case |
| POST | `/api/v1/oracle/review-feedback` | Record reviewer feedback |

## Error Response Contract

All error responses follow a consistent schema:

```json
{
  "error": {
    "code": "RECEIPT_NOT_FOUND",
    "message": "No receipt found with the given ID",
    "detail": null,
    "retryable": false
  }
}
```

## Logging Contract

All log entries are structured JSON with at minimum:

- `timestamp` (ISO 8601)
- `level` (DEBUG, INFO, WARNING, ERROR)
- `event` (machine-readable event name)
- `tenant_id` (when available)
- `fingerprint` (when available)
- `duration_ms` (for timed operations)

No raw claim data, PII, or secrets are logged. Only fingerprints, status values,
and structural metadata appear in log output.

## Receipt Lifecycle States

```
ACTIVE  →  REVOKED     (via explicit revocation)
ACTIVE  →  SUPERSEDED  (when a new evaluation supersedes)
```

Receipts are immutable once issued. Revocation adds a status transition, not a
mutation of the original receipt.

## Data Flow: Evaluate Request

```
Request → tenant_guard → intake → fingerprint
       → extract_claims → normalize
       → screen_sources (with retry)
       → compare_claims → risk_flags
       → evaluate_policies → compute_fraud_risk
       → adjudicate → route_review
       → build_receipt → store_receipt → anchor
       → build_audit_trace
       → return OracleDecision

Logging at each stage boundary.
Fingerprint as correlation ID throughout.
```
