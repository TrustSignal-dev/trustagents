from __future__ import annotations

from trustagents.oracle.models import ComparisonResult, SourceResult


def evaluate_policies(claims: dict, comparisons: list[ComparisonResult], sources: list[SourceResult]) -> list[str]:
    outcomes: list[str] = []
    if claims.get("revoked") or any(s.conflicting_fields.get("revoked") for s in sources):
        outcomes.append("revoked")
    if claims.get("sanctionsMatch") or any(s.matched_fields.get("sanctionsMatch") for s in sources):
        outcomes.append("sanctions_match")
    if claims.get("integrityFailure"):
        outcomes.append("integrity_failure")
    if claims.get("expired"):
        outcomes.append("expired")
    if claims.get("policyContradiction"):
        outcomes.append("impossible_policy_contradiction")
    if any(s.retrieval_status in {"UNAVAILABLE", "TIMEOUT", "ERROR"} for s in sources):
        outcomes.append("source_unavailable")
    if any(c.result == "AMBIGUOUS" for c in comparisons):
        outcomes.append("ambiguous_identity")
    if any(c.result == "NEAR_MATCH" for c in comparisons):
        outcomes.append("near_match_escalation")
    if any(c.result == "MISMATCH" and c.severity == "high" for c in comparisons):
        outcomes.append("high_mismatch")
    if not any(s.retrieval_status == "SUCCESS" for s in sources):
        outcomes.append("insufficient_evidence")
    return outcomes
