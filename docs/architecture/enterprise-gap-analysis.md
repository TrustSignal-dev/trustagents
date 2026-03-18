# Enterprise-Readiness Gap Analysis

## Assessment Criteria

Each gap is rated by severity (**Critical**, **High**, **Medium**, **Low**) and
categorized by domain.

## Gaps

### 1. Observability — Partially Resolved

| Gap | Description | Status |
|---|---|---|
| No structured logging | The oracle pipeline produces no log output. There is no way to trace a request through the pipeline, diagnose failures, or audit operational behavior. | **Resolved** — `get_logger` / `log_stage` added to all pipeline stages. |
| No metrics collection | No counters, histograms, or gauges for request volume, latency, error rates, or risk band distributions. | Open |
| No distributed tracing | No correlation IDs or trace spans for cross-service observability. | Open |

**Impact:** Structured logging now covers the full pipeline lifecycle. Metrics and
distributed tracing remain open for a future instrumentation pass.

### 2. Receipt Lifecycle — Resolved

| Gap | Description | Status |
|---|---|---|
| No receipt verification | Receipts are generated but cannot be independently verified. | **Resolved** — `POST /api/v1/oracle/receipts/verify` endpoint added. |
| No receipt revocation | There is no mechanism to revoke a receipt, mark it as superseded, or look up receipt status. | **Resolved** — `POST /api/v1/oracle/receipts/revoke` and `GET /api/v1/oracle/receipts/{id}` added. |
| No receipt store | Receipts are embedded in oracle decisions but not independently addressable. | **Resolved** — in-memory `ReceiptStore` with full lifecycle support. |

**Impact:** The collect → receipt → verify → review lifecycle is now complete for
simulation scope.

### 3. Error Handling — Resolved

| Gap | Description | Status |
|---|---|---|
| Unstructured errors | API errors are raised as bare `HTTPException` with string details. No consistent error schema. | **Resolved** — `OracleError` class with machine-readable codes, messages, and retryability flags. |
| No error classification | No distinction between client errors, pipeline failures, and transient errors. | **Resolved** — pre-defined error constants (`RECEIPT_NOT_FOUND`, `TENANT_MISMATCH`, etc.). |
| Silent pipeline failures | Exceptions inside the oracle pipeline may propagate as 500s without context. | **Resolved** — `log_stage` captures and logs pipeline exceptions with full context. |

**Impact:** Structured error responses are now consistent across all API endpoints.

### 4. Resilience — Partially Resolved

| Gap | Description | Status |
|---|---|---|
| No retry logic | The HTTP connector fails immediately on timeout or error. No retry, backoff, or circuit-breaker patterns. | Open |
| No compliance-gap signaling | When source coverage is incomplete, this is handled generically rather than as a distinct compliance gap. | **Resolved** — `compliance_gap` risk flag now emits a distinct reason in review routing. |

**Impact:** Compliance-gap signals are now correctly distinguished from partial
source coverage. HTTP connector retry logic remains open.

### 5. Storage — Medium

| Gap | Description |
|---|---|
| In-memory only | Jobs, review queue, case memory, idempotency, and receipt data are lost on restart. |

**Impact:** Acceptable for simulation. Must be addressed before any durable
deployment, but pluggable interfaces make this a clean migration when ready.

### 6. Security Hardening — Medium

| Gap | Description |
|---|---|
| SHA-256 receipt signatures | Receipts use plain SHA-256 hashing rather than HMAC or asymmetric signatures. Acceptable for simulation but not for production trust assertions. |
| No rate limiting | API has no request rate controls. |
| No input size limits | Request payloads have no explicit size bounds. |

**Impact:** Adequate for simulation scope. Must be hardened before production
deployment.

### 7. CI/CD — Low (for simulation scope)

| Gap | Description |
|---|---|
| No CI workflow | No GitHub Actions configuration for automated testing. |
| No container image | No Dockerfile for deployment. |

**Impact:** Low for current simulation scope. Required before production
deployment.

## Priority Order for Enterprise Hardening

1. ~~Structured logging throughout the pipeline~~ — **Done**
2. ~~Receipt verification and revocation endpoints~~ — **Done**
3. ~~Structured error response model~~ — **Done**
4. Retry wrapper for connectors
5. ~~Compliance-gap handling in the risk pipeline~~ — **Done**
6. ~~Receipt store for independent addressability~~ — **Done**
7. Metrics hooks (counters, histograms)
8. Storage interface abstractions
9. HMAC receipt signatures
10. CI/CD pipeline
