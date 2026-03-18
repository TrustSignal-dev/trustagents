# Oracle Service Architecture (Experimental)

The service is a compact FastAPI application with deterministic pipeline stages:

1. intake and canonical fingerprinting
2. claim extraction and normalization
3. source retrieval (mock, file, optional HTTP connector with retry)
4. field comparison
5. risk flag generation (including compliance-gap detection)
6. conservative policy evaluation
7. deterministic adjudication and review routing
8. receipt construction and lifecycle storage
9. receipt anchoring
10. bounded audit trace assembly

Structured logging is emitted at each stage boundary with tenant ID, fingerprint,
and timing metadata. No raw claim data or PII appears in log output.

The receipt lifecycle supports verification, revocation, and status lookup through
dedicated API endpoints. Receipts are immutable once issued; revocation adds a
state transition rather than mutating the original record.

The API layer depends on the oracle service contract only. The oracle service
depends on local deterministic components. Error responses follow a structured
schema with machine-readable error codes and retryability indicators.
