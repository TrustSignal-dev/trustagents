# Benchmarks

## Benchmark Goals

The benchmark suite is intended to measure whether proposed agent roles can identify integrity failures in synthetic compliance evidence records without overstating capability.

## Initial Benchmark Tasks

- classify the anomaly category for a single synthetic record
- detect whether provenance metadata is sufficient for verification
- explain why a record should be trusted, questioned, or escalated
- distinguish valid control examples from anomalous samples
- identify when uncertainty is the correct answer

## Benchmark Design Principles

- synthetic data only
- clear labels and scenario documentation
- no fabricated scores
- reproducible task definitions
- emphasis on defensive usefulness rather than novelty claims

## Release Criteria

Benchmark results should only be published when:

- the task definitions are stable
- labels are documented
- limitations are stated clearly
- failure cases are retained for review

Until then, this repository publishes benchmark design only.
