# Datasets

## Compliance Evidence Integrity Dataset

This repository defines the Compliance Evidence Integrity Dataset, or CEID, as a synthetic dataset format for researching integrity failures in automated compliance evidence pipelines.

Current contents:

- `ceid-schema.json`: the JSON Schema for a CEID record
- `sample-anomalies.jsonl`: a small synthetic sample set for early benchmarking and review

## Synthetic-Only Policy

All dataset examples in this repository are synthetic. They are written to model research-relevant integrity failures without using real audit evidence, production logs, customer records, or personal data.

Dataset publication rules:

- `simulated` must be `true`
- `contains_pii` must be `false`
- records must avoid organization-specific secrets or identifiers
- examples must remain suitable for public release

## Intended Uses

The dataset is intended for:

- schema design and validation
- simulation-driven anomaly generation
- benchmark development
- comparative evaluation of defensive analysis methods

The dataset is not intended to support claims about real-world detection coverage or enterprise deployment readiness.
