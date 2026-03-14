# Simulation Scenarios

## Purpose

These scenarios define safe, defensive examples of integrity failures in automated compliance evidence pipelines. They are written to support synthetic dataset generation and evaluation planning, not operational abuse.

## Scenario Families

### Evidence Tampering

A previously collected artifact is altered after collection or before review. The anomaly is represented through inconsistent hashes, changed metadata, or mismatched storage references.

### Unauthorized Evidence Generation

A record appears in the evidence pipeline without the expected source, approval path, or export mechanism. The scenario focuses on provenance inconsistency rather than attack mechanics.

### Timestamp Manipulation

Related events are assigned an impossible or suspicious temporal order. Example patterns include approvals that occur after deployment or review artifacts created after a process is reported complete.

### Pipeline Injection

An unexpected transform, sidecar job, or intermediary packaging step appears in the synthetic provenance chain. The scenario tests whether analysis can flag unrecognized handling stages.

### Evidence Reuse

An evidence artifact is reused outside its original reporting period, control objective, or review context. The scenario examines how provenance and freshness rules handle stale reuse.

## Safety Constraints

- no real operational procedures
- no exploit payloads or bypass instructions
- no references to live customer environments
- no confidential evidence
- synthetic identifiers only
