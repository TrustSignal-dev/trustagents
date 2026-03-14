# Project Summary

## Title

Autonomous Agents for Fraud Detection in Compliance Infrastructure

## One-Sentence Description

This project proposes a defensive research framework for detecting integrity failures in automated compliance evidence pipelines using simulated datasets, narrow agent roles, and transparent evaluation criteria.

## Overview

Modern compliance programs depend on automatically collected evidence from CI/CD systems, ticketing platforms, cloud services, identity providers, and internal workflow tools. That automation improves coverage but also creates a new integrity problem: downstream reviewers may rely on artifacts whose provenance, timestamps, or generation path can no longer be trusted.

TrustAgents is a research scaffold for studying those failures in a controlled setting. The repository defines a synthetic Compliance Evidence Integrity Dataset, safe simulation scenarios, role-specific agents, and benchmark criteria for identifying evidence tampering, unauthorized evidence generation, timestamp manipulation, pipeline injection, and evidence reuse.

The project does not claim a production-ready detector. Its purpose is to create a focused, defensive-security research package that can be inspected, extended, and evaluated by external reviewers if publicly released.

## Intended Outputs

- a repository with proposal and methodology documents
- a JSON schema for synthetic integrity-focused evidence records
- synthetic anomaly samples and scenario definitions
- a benchmark plan with non-fabricated metrics
- a staged public release plan for code, docs, and datasets

## Public Benefit

All public artifacts are intended to improve understanding of integrity risks in compliance automation without exposing confidential audit material or personal data. Published samples remain synthetic, and release materials are scoped to defensive research and open evaluation.
