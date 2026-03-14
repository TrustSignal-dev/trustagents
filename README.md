# TrustAgents

TrustAgents is a defensive-security research repository for simulated fraud detection in compliance evidence pipelines. It is designed to support a grant application and early research review with concrete artifacts instead of product infrastructure. The repository focuses on integrity failures such as evidence tampering, unauthorized evidence generation, timestamp manipulation, pipeline injection, and evidence reuse. All examples in this repository are synthetic or simulated and do not contain customer data or personally identifiable information.

## Project Scope

This repository documents a proposed research project: Autonomous Agents for Fraud Detection in Compliance Infrastructure.

The project is framed as:

- a research scaffold for defensive integrity monitoring
- a synthetic dataset and schema effort
- a simulation and evaluation plan
- a public-benefit release package intended for external review

It is not:

- a production detection system
- a hosted SaaS application
- a repository of real audit artifacts
- evidence that the proposed methods already outperform existing controls

## Outputs

This repository is intended to publish:

- proposal and grant application source documents
- the Compliance Evidence Integrity Dataset schema
- synthetic anomaly samples
- simulation and methodology notes
- agent role definitions
- evaluation benchmarks and metrics

## Repository Map

- `proposal/`: grant-ready summaries, application text, budget, and timeline
- `docs/`: problem framing, methodology, release plan, and threat model
- `datasets/`: schema and synthetic sample anomalies
- `simulations/`: scenario catalog and pipeline model
- `agents/`: lightweight role definitions for research agents
- `eval/`: benchmark design and metrics

## Defensive Framing

The repository is limited to defensive integrity failures in automated compliance workflows. It does not include offensive testing procedures, exploit development, or operational guidance for bypassing controls. Fraud scenarios are documented only at a level needed to define synthetic data and evaluation tasks.

## Roadmap

1. Publish the initial proposal and dataset schema.
2. Expand the synthetic anomaly corpus and scenario coverage.
3. Formalize benchmark tasks and evaluator instructions.
4. Refine labeling guidance, threat boundaries, and reviewer documentation.
5. Release benchmark materials with clear limitations and no overclaiming.
