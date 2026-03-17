from __future__ import annotations

from trustagents.oracle.models import Confidence, OracleStatus


def adjudicate(policy_results: list[str], risk_flags: list[str]) -> tuple[OracleStatus, Confidence, float, list[str]]:
    explanations: list[str] = []
    if "revoked" in policy_results:
        return OracleStatus.REVOKED, Confidence.LOW, 0.1, ["Revocation evidence overrides matches"]
    if "ambiguous_identity" in policy_results and "high_mismatch" in policy_results:
        return OracleStatus.CONFLICTED, Confidence.LOW, 0.2, ["Conflicting identity evidence across checks"]
    if "source_unavailable" in policy_results:
        return OracleStatus.SOURCE_UNAVAILABLE, Confidence.LOW, 0.2, ["Required source unavailable"]
    if "ambiguous_identity" in policy_results:
        return OracleStatus.UNVERIFIABLE, Confidence.LOW, 0.3, ["Identity evidence is ambiguous"]
    if "insufficient_evidence" in policy_results:
        return OracleStatus.INSUFFICIENT_EVIDENCE, Confidence.LOW, 0.25, ["No successful source retrieval"]
    if "near_match_escalation" in policy_results:
        return OracleStatus.UNVERIFIABLE, Confidence.LOW, 0.35, ["Near-match-only evidence requires escalation"]
    if "expired" in policy_results:
        return OracleStatus.EXPIRED, Confidence.MEDIUM, 0.5, ["Evidence expired"]
    if "high_mismatch" in policy_results:
        return OracleStatus.INVALID, Confidence.LOW, 0.3, ["High severity mismatches found"]

    score = 0.9
    confidence = Confidence.HIGH
    if "stale_source_data" in risk_flags:
        score = 0.6
        confidence = Confidence.MEDIUM
        explanations.append("Stale data reduced confidence")
    explanations.append("All required checks passed conservatively")
    return OracleStatus.VALID, confidence, score, explanations
