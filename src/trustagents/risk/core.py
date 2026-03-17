from __future__ import annotations

from trustagents.oracle.models import ComparisonResult, SourceResult


def generate_risk_flags(comparisons: list[ComparisonResult], sources: list[SourceResult]) -> list[str]:
    flags: list[str] = []
    if any(c.result in {"NEAR_MATCH", "AMBIGUOUS"} for c in comparisons):
        flags.append("identity_ambiguity")
    if any(c.field == "artifactHash" and c.result == "MISMATCH" for c in comparisons):
        flags.append("hash_mismatch")
    if any(s.retrieval_status in {"TIMEOUT", "UNAVAILABLE", "ERROR"} for s in sources):
        flags.append("source_outage")
    if any(s.source_freshness == "stale" for s in sources):
        flags.append("stale_source_data")
    return flags
