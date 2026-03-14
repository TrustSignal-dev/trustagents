# Methodology

## Research Approach

The project uses a simulated compliance evidence pipeline rather than live enterprise systems. The purpose is to study integrity failures in a controlled environment where scenario design, labels, and evaluation criteria are transparent and safe to publish.

## Simulated Pipeline

The simulation models a representative path from evidence generation to reviewer consumption:

1. source systems emit evidence-like records
2. an ingestion layer normalizes metadata
3. a transform layer packages evidence for reporting
4. a storage layer retains artifacts and metadata
5. a validation layer checks provenance and consistency
6. a reviewer layer consumes the resulting evidence bundle

Each stage is modeled with enough detail to support integrity reasoning, but not enough detail to recreate real customer environments or operational controls.

## Agent Roles

The repository uses three narrow agent roles:

- evidence analysis: inspect record structure, provenance fields, and context quality
- anomaly detection: identify likely integrity failures and classify anomaly categories
- verification: compare claims against expected provenance rules and simulation state

These roles are intentionally separated so the evaluation can measure task quality and uncertainty handling rather than treating the system as a monolithic autonomous actor.

## Anomaly Generation

Synthetic anomalies are created by modifying otherwise plausible evidence records. Examples include hash mismatches, impossible timestamp orderings, missing provenance links, unapproved source identifiers, duplicate artifact reuse across unrelated controls, and unexpected transform steps in the pipeline.

Scenario design follows these rules:

- all examples remain synthetic
- no real customer systems or logs are copied
- anomaly descriptions stay non-operational
- labels reflect integrity failures, not exploit instructions

## Labeling Process

Each synthetic record includes:

- a scenario identifier
- an anomaly category
- integrity signals or warning indicators
- reproduction notes describing how the anomaly was synthesized
- a `simulated` flag
- a `contains_pii` flag set to `false`

Labels are intended for benchmark reproducibility, not as proof of real-world prevalence.

## Evaluation Loop

The evaluation loop is:

1. generate or sample a synthetic scenario
2. provide the record and surrounding context to the agent role under test
3. collect structured judgments about provenance, anomaly type, and confidence
4. compare outputs against scenario labels and benchmark criteria
5. review false positives, false negatives, and uncertain cases

Evaluation emphasizes defensible precision, correct uncertainty handling, and explanation quality over broad automation claims.

## Public Release Constraints

Public releases will include schema definitions, synthetic samples, methodology notes, and benchmark descriptions. If lightweight code is added later, it should remain offline and simulation-oriented by default. No release should contain confidential evidence, personal data, or unsupported claims about operational effectiveness.
