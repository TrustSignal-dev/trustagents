# AGENTS.md

## Purpose

This repository supports a defensive-security research proposal for simulated fraud detection in compliance evidence pipelines. Future changes should keep the repository minimal, auditable, and suitable for grant reviewers, technical evaluators, and open-source collaborators.

## Required Guardrails

- Do not invent research results, benchmark scores, or deployment evidence.
- Do not claim production readiness unless the repository actually contains the required controls and validation.
- Keep the project defensive only. Do not add offensive-security content or adversarial instructions.
- Do not add real customer data, audit artifacts, internal logs, or any personally identifiable information.
- Do not add secrets, tokens, credentials, or environment-specific operational details.
- Keep examples synthetic or explicitly anonymized.
- Prefer Markdown, JSON, JSON Schema, and small reference artifacts over unnecessary application code.
- Keep changes small and easy to review.
- Preserve wording consistency across `README.md`, `proposal/`, `docs/`, `datasets/`, and `eval/`.

## Writing Standards

- Use plain English and avoid hype.
- State assumptions clearly.
- Distinguish between current repository contents and future research plans.
- Qualify any capability that is proposed but not yet implemented.
- Use precise language around trust boundaries, simulated environments, and evaluation limits.

## Data Handling

- Synthetic data only.
- `contains_pii` must remain `false` for all published samples.
- Do not add direct copies of real compliance evidence, screenshots, logs, or policy documents.

## Code And Structure

- Prefer documentation-first changes.
- Do not add databases, hosted services, CI secrets, or deployment configuration unless explicitly requested.
- If code is added later, keep it local, offline, and simulation-oriented by default.
