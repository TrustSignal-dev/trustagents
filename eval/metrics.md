# Metrics

## Proposed Metrics

The project will use a small set of transparent metrics appropriate for a synthetic defensive benchmark.

- precision by anomaly category
- recall by anomaly category
- false positive rate on valid control samples
- provenance completeness judgment accuracy
- explanation quality against a reviewer rubric
- escalation accuracy for uncertain or unverifiable records

## Success Criteria

Success in this repository means:

- the schema supports the needed integrity fields
- synthetic scenarios are internally consistent
- benchmark tasks are understandable and reproducible
- evaluation can distinguish between valid, anomalous, and unverifiable cases

Success does not mean the repository has demonstrated enterprise deployment readiness or comprehensive fraud coverage.

## Reporting Rules

- do not publish metrics without describing dataset limits
- do not collapse uncertainty into forced binary decisions
- do not present synthetic benchmark performance as a real-world guarantee
