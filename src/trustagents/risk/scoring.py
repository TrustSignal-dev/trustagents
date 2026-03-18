from __future__ import annotations

from trustagents.oracle.models import (
    Confidence,
    FraudRisk,
    FraudRiskBand,
    FraudSignal,
    ReviewRecommendation,
    ScoringMode,
    SimilarCaseReference,
)

_SIGNAL_WEIGHTS = {
    "hash_mismatch": 0.45,
    "identity_ambiguity": 0.30,
    "source_outage": 0.25,
    "stale_source_data": 0.10,
    "high_mismatch": 0.35,
    "near_match_signal": 0.2,
    "low_extraction_confidence": 0.2,
    "compliance_gap": 0.30,
}


def _to_band(score: float) -> FraudRiskBand:
    if score >= 0.7:
        return FraudRiskBand.HIGH
    if score >= 0.35:
        return FraudRiskBand.MEDIUM
    return FraudRiskBand.LOW


def compute_fraud_risk(
    risk_flags: list[str],
    policy_results: list[str],
    similar_cases: list[SimilarCaseReference],
) -> FraudRisk:
    unique_flags = sorted(set(risk_flags + [p for p in policy_results if p in _SIGNAL_WEIGHTS]))
    signals = [
        FraudSignal(signal_id=flag, contribution=_SIGNAL_WEIGHTS.get(flag, 0.05), reason=f"Detected {flag}")
        for flag in unique_flags
    ]
    score = min(1.0, round(sum(s.contribution for s in signals), 4))
    band = _to_band(score)

    confidence = Confidence.HIGH if band == FraudRiskBand.LOW else Confidence.MEDIUM
    if band == FraudRiskBand.HIGH:
        confidence = Confidence.LOW

    scoring_mode = ScoringMode.DETERMINISTIC_RULES
    if similar_cases:
        scoring_mode = ScoringMode.HYBRID

    recommendation = ReviewRecommendation.NONE if band == FraudRiskBand.LOW else ReviewRecommendation.RECOMMENDED
    top_signals = sorted(signals, key=lambda s: s.contribution, reverse=True)[:3]
    return FraudRisk(
        score=score,
        band=band,
        confidence=confidence,
        scoring_mode=scoring_mode,
        top_contributing_signals=top_signals,
        review_recommendation=recommendation,
        similar_reviewed_cases=similar_cases,
    )
