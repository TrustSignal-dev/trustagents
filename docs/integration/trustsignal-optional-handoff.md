# TrustSignal Optional Handoff (Future Gated)

This repository includes documentation-only handoff guidance.

- Handoff is optional and non-blocking.
- Handoff is not part of the current production dependency chain.
- Export support is controlled by `trustsignal_handoff_export_enabled=false` by default.

Example handoff payload:

```json
{
  "schemaVersion": "1.0",
  "tenantId": "tenant-sim-001",
  "oracleStatus": "UNVERIFIABLE",
  "confidence": "LOW",
  "artifactFingerprint": "<sha256>",
  "auditTrace": ["request_intake", "source_retrieval", "adjudication"]
}
```
