# Enterprise-Readiness Gap Analysis

## Assessment Criteria

Each gap is rated by severity (**Critical**, **High**, **Medium**, **Low**) and
categorized by domain.

## Gaps

### 1. Observability — Critical

| Gap | Description |
|---|---|
| No structured logging | The oracle pipeline produces no log output. There is no way to trace a request through the pipeline, diagnose failures, or audit operational behavior. |
| No metrics collection | No counters, histograms, or gauges for request volume, latency, error rates, or risk band distributions. |
| No distributed tracing | No correlation IDs or trace spans for cross-service observability. |

**Impact:** An enterprise deployment without logging or metrics is opaque and
unauditable. This is the single highest-priority gap.

### 2. Receipt Lifecycle — Critical

| Gap | Description |
|---|---|
| No receipt verification | Receipts are generated but cannot be independently verified. The collect → receipt → **verify** → review flow is incomplete. |
| No receipt revocation | There is no mechanism to revoke a receipt, mark it as superseded, or look up receipt status. |
| No receipt store | Receipts are embedded in oracle decisions but not independently addressable. |

**Impact:** Without verification and revocation, receipts are write-only artifacts
with no operational lifecycle.

### 3. Error Handling — High

| Gap | Description |
|---|---|
| Unstructured errors | API errors are raised as bare `HTTPException` with string details. No consistent error schema. |
| No error classification | No distinction between client errors, pipeline failures, and transient errors. |
| Silent pipeline failures | Exceptions inside the oracle pipeline may propagate as 500s without context. |

**Impact:** Operators and integrators cannot programmatically handle errors or
distinguish retriable from terminal failures.

### 4. Resilience — High

| Gap | Description |
|---|---|
| No retry logic | The HTTP connector fails immediately on timeout or error. No retry, backoff, or circuit-breaker patterns. |
| No compliance-gap signaling | When source coverage is incomplete, this is handled generically rather than as a distinct compliance gap. |

**Impact:** A single transient source failure causes degraded decisions with no
recovery path.

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

1. Structured logging throughout the pipeline
2. Receipt verification and revocation endpoints
3. Structured error response model
4. Retry wrapper for connectors
5. Compliance-gap handling in the risk pipeline
6. Receipt store for independent addressability
7. Metrics hooks (counters, histograms)
8. Storage interface abstractions
9. HMAC receipt signatures
10. CI/CD pipeline
