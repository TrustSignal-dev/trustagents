# Oracle API Contract

## Endpoints

- `GET /healthz`
- `POST /api/v1/oracle/evaluate`
- `POST /api/v1/oracle/jobs`
- `GET /api/v1/oracle/jobs/{jobId}`

## Request

A request includes:

- `tenantId`
- either `artifact` or `claimPackage`
- optional `policyProfile` or `sourceSelection`
- optional `idempotencyKey`
- optional `preferAsync`

## Response safety limits

The API does not expose chain-of-thought, prompt internals, model/provider selection internals, raw stack traces, or connector secrets.

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
