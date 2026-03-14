# Threat Model

## Scope

This threat model covers integrity failures in automated compliance evidence pipelines. It is limited to defensive analysis of how evidence can become unreliable between generation and review.

## Assets

- evidence records and derived reports
- provenance metadata
- timestamp and sequencing information
- artifact hashes or equivalent integrity signals
- reviewer decisions that depend on pipeline output

## Trust Boundaries

The representative pipeline includes the following trust boundaries:

- evidence sources: CI/CD systems, ticketing tools, identity systems, cloud services, and internal workflow tools
- ingestion systems: collectors, webhooks, or batch import jobs that normalize incoming records
- transformation layer: scripts or services that reformat evidence and attach metadata
- artifact stores: object storage, document stores, or evidence bundles used for later review
- validation layer: logic that checks consistency, provenance, and completeness
- reviewer and auditor reliance layer: humans or downstream systems that consume final evidence packages

## Threat Events

The defensive threat events modeled in this repository are:

- evidence tampering after collection
- unauthorized evidence generation presented as trusted output
- timestamp manipulation that changes sequence or reviewability
- pipeline injection through unexpected transforms or jobs
- evidence reuse across unrelated reporting contexts
- provenance erosion caused by missing links, identifiers, or state transitions

## Assumptions

- the project uses simulated data only
- public artifacts must not enable offensive operations
- evaluation focuses on detection quality, uncertainty handling, and provenance reasoning
- the model does not assume perfect access to source-of-truth systems

## Defensive Objective

The objective is to help a reviewer determine whether a record should be trusted, questioned, or escalated based on integrity signals and provenance gaps. The objective is not to automate enforcement or replace human judgment in high-stakes assurance workflows.
