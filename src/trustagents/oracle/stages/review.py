from __future__ import annotations

from trustagents.oracle.models import DecisionAction, FraudRiskBand, ReviewRecommendation


def route_review(
    *,
    band: FraudRiskBand,
    risk_flags: list[str],
    policy_results: list[str],
    extraction_confidence: float,
    source_results_complete: bool,
    conflicting_sources: bool,
) -> tuple[DecisionAction, ReviewRecommendation, bool, list[str]]:
    reasons: list[str] = []

    hard_block = {"revoked", "sanctions_match", "integrity_failure", "impossible_policy_contradiction"}
    if any(policy in hard_block for policy in policy_results):
        reasons.append("Hard policy block triggered")
        return DecisionAction.BLOCK, ReviewRecommendation.NONE, False, reasons

    needs_manual = False
    if band in {FraudRiskBand.MEDIUM, FraudRiskBand.HIGH}:
        reasons.append("Fraud risk band requires manual review")
        needs_manual = True
    if "identity_ambiguity" in risk_flags or "near_match_signal" in risk_flags:
        reasons.append("Ambiguity or near-match evidence present")
        needs_manual = True
    if not source_results_complete or "compliance_gap" in risk_flags:
        reasons.append("Registry coverage incomplete")
        needs_manual = True
    if extraction_confidence < 0.7:
        reasons.append("Extraction confidence below threshold")
        needs_manual = True
    if conflicting_sources:
        reasons.append("Conflicting sources detected")
        needs_manual = True

    if needs_manual:
        return DecisionAction.MANUAL_REVIEW, ReviewRecommendation.REQUIRED, True, reasons
    return DecisionAction.PROCEED, ReviewRecommendation.NONE, False, ["Low risk and satisfactory checks"]
