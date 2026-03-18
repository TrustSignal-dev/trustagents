# Oracle API Contract

## Endpoints

- `GET /healthz`
- `POST /api/v1/oracle/evaluate`
- `POST /api/v1/oracle/jobs`
- `GET /api/v1/oracle/jobs/{jobId}`
- `POST /api/v1/oracle/receipts/verify`
- `POST /api/v1/oracle/receipts/revoke`
- `GET /api/v1/oracle/receipts/{receiptId}`
- `GET /api/v1/oracle/review-queue`
- `POST /api/v1/oracle/review-cases`
- `POST /api/v1/oracle/review-feedback`

## Request

A request includes:

- `tenantId`
- either `artifact` or `claimPackage`
- optional `policyProfile` or `sourceSelection`
- optional `idempotencyKey`
- optional `preferAsync`

## Response safety limits

The API does not expose chain-of-thought, prompt internals, model/provider selection internals, raw stack traces, or connector secrets.

## Error response contract

All error responses follow a structured schema:

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

Error codes include: `ORACLE_API_DISABLED`, `TENANT_MISMATCH`, `ASYNC_JOBS_DISABLED`,
`JOB_NOT_FOUND`, `CASE_NOT_FOUND`, `RECEIPT_NOT_FOUND`, `RECEIPT_ALREADY_REVOKED`.

## Example: synchronous evaluate

```bash
curl -sS -X POST http://localhost:8000/api/v1/oracle/evaluate \
  -H 'content-type: application/json' \
  -H 'x-tenant-id: tenant-sim-001' \
  -d @examples/oracle-request.json
```

## Example: async job (feature-flagged)

`async_jobs_enabled` is `false` by default. Enable it explicitly for local testing before calling:

```bash
curl -sS -X POST http://localhost:8000/api/v1/oracle/jobs \
  -H 'content-type: application/json' \
  -H 'x-tenant-id: tenant-sim-001' \
  -d @examples/oracle-request.json
```

## Example: receipt verification

```bash
curl -sS -X POST http://localhost:8000/api/v1/oracle/receipts/verify \
  -H 'content-type: application/json' \
  -H 'x-tenant-id: tenant-sim-001' \
  -d '{"receiptId": "<id>", "fingerprint": "<fp>", "signature": "<sig>"}'
```

## Example: receipt revocation

```bash
curl -sS -X POST http://localhost:8000/api/v1/oracle/receipts/revoke \
  -H 'content-type: application/json' \
  -H 'x-tenant-id: tenant-sim-001' \
  -d '{"receiptId": "<id>", "reason": "Audit finding"}'
```

## Example: receipt status lookup

```bash
curl -sS http://localhost:8000/api/v1/oracle/receipts/<receipt-id> \
  -H 'x-tenant-id: tenant-sim-001'
```
