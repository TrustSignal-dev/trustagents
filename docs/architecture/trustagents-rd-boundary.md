# TrustAgents R&D Boundary

## Current state

TrustAgents provides an experimental oracle-evaluation service for synthetic compliance evidence research. It is optional and non-blocking.

TrustSignal production remains unchanged and does not depend on this service.

## Boundary rules

- Oracle decisions are advisory outputs for research ingestion.
- No runtime coupling to TrustSignal production verification path is implemented.
- Integration is future gated and must remain explicitly optional.
- Service defaults keep local, synthetic, and mocked operation.
