# Oracle Decision Schema

The response contract is versioned and camelCase.

Required top-level fields:

- schemaVersion
- oracleStatus
- confidence
- confidenceScore
- checkedAt
- artifactFingerprint
- sourceResults
- comparisonResults
- policyResults
- riskFlags
- explanations
- auditTrace

`auditTrace` is bounded structured provenance. It excludes chain-of-thought and prompt internals.
