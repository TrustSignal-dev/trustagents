from __future__ import annotations

from trustagents.adjudication.core import adjudicate
from trustagents.comparators.core import compare_claims
from trustagents.extractors.core import extract_claims
from trustagents.learning.case_memory import case_memory_store
from trustagents.normalizers.core import normalize_claims
from trustagents.observability import get_logger, log_stage
from trustagents.oracle.models import OracleDecision, OracleRequest, PipelineVersions
from trustagents.oracle.stages.anchoring import anchor_receipt
from trustagents.oracle.stages.intake import run_intake
from trustagents.oracle.stages.receipt import build_signed_receipt
from trustagents.oracle.stages.retrieval import run_screening
from trustagents.oracle.stages.review import route_review
from trustagents.policies.core import evaluate_policies
from trustagents.provenance.trace import build_audit_trace
from trustagents.receipts.store import receipt_store
from trustagents.review.store import review_queue_store
from trustagents.risk.core import generate_risk_flags
from trustagents.risk.scoring import compute_fraud_risk

logger = get_logger("oracle.service")


class OracleService:
    def evaluate(self, request: OracleRequest) -> OracleDecision:
        versions = PipelineVersions()
        steps = ["fingerprinting_intake"]
        ctx = {"tenant_id": request.tenant_id}

        with log_stage(logger, "intake", extra=ctx):
            payload, fingerprint = run_intake(request)
        ctx["fingerprint"] = fingerprint

        with log_stage(logger, "extraction_normalization", extra=ctx):
            extracted = extract_claims(payload)
            claims = normalize_claims(extracted["claims"])
            extraction_confidence = _estimate_extraction_confidence(claims)
        steps.append("extraction_normalization")

        with log_stage(logger, "retrieval_screening", extra=ctx):
            source_results, source_payload = run_screening(claims)
        steps.append("retrieval_screening")

        with log_stage(logger, "comparison_risk_flags", extra=ctx):
            comparisons = compare_claims(claims, source_payload)
            risk_flags = generate_risk_flags(comparisons, source_results)
            if extraction_confidence < 0.7:
                risk_flags.append("low_extraction_confidence")
            if any(c.result == "NEAR_MATCH" for c in comparisons):
                risk_flags.append("near_match_signal")

        with log_stage(logger, "policy_evaluation", extra=ctx):
            policies = evaluate_policies(claims, comparisons, source_results)
        steps.append("fraud_signals_policy_checks")

        with log_stage(logger, "fraud_risk_scoring", extra=ctx):
            feature_digest = _feature_digest(claims)
            similar_cases = case_memory_store.similar_cases(feature_digest)
            fraud_risk = compute_fraud_risk(risk_flags, policies, similar_cases)

        with log_stage(logger, "adjudication_review_routing", extra=ctx):
            status, confidence, score, explanations = adjudicate(policies, risk_flags)
            decision, review_recommendation, manual_review_required, review_reasons = route_review(
                band=fraud_risk.band,
                risk_flags=risk_flags,
                policy_results=policies,
                extraction_confidence=extraction_confidence,
                source_results_complete=all(s.retrieval_status == "SUCCESS" for s in source_results),
                conflicting_sources=any(s.conflicting_fields for s in source_results),
            )
            fraud_risk.review_recommendation = review_recommendation
        steps.append("adjudication_review_routing")

        with log_stage(logger, "receipt_construction", extra=ctx):
            receipt = build_signed_receipt(fingerprint, decision.value, versions.model_dump())
            receipt_store.store(receipt, request.tenant_id, decision.value)
        steps.append("receipt_construction")

        with log_stage(logger, "anchoring", extra=ctx):
            anchor_record = anchor_receipt(receipt)
        steps.append("anchoring")

        if manual_review_required:
            review_queue_store.enqueue(
                {
                    "artifactFingerprint": fingerprint,
                    "tenantId": request.tenant_id,
                    "fraudRiskBand": fraud_risk.band.value,
                    "reasons": review_reasons,
                    "versions": versions.model_dump(by_alias=True),
                }
            )

        trace = build_audit_trace(steps)
        reasons = review_reasons + explanations

        logger.info(
            "evaluation_complete",
            extra={
                **ctx,
                "oracle_status": status.value,
                "decision": decision.value,
                "manual_review": manual_review_required,
                "risk_band": fraud_risk.band.value,
            },
        )

        return OracleDecision(
            oracle_status=status,
            decision=decision,
            confidence=confidence,
            confidence_score=score,
            artifact_fingerprint=fingerprint,
            source_results=source_results,
            comparison_results=comparisons,
            policy_results=policies,
            risk_flags=sorted(set(risk_flags)),
            reasons=reasons,
            explanations=explanations,
            fraud_risk=fraud_risk,
            versions=versions,
            signed_receipt=receipt,
            anchor_record=anchor_record,
            manual_review_required=manual_review_required,
            audit_trace=trace,
        )


def _estimate_extraction_confidence(claims: dict) -> float:
    required = ["fullName", "dateOfBirth", "identifier", "artifactHash"]
    present = sum(1 for item in required if claims.get(item))
    return round(present / len(required), 4)


def _feature_digest(claims: dict) -> str:
    parts = [
        str(claims.get("identifierNormalized") or ""),
        str(claims.get("dateOfBirthNormalized") or ""),
        str(claims.get("fullNameNormalized") or ""),
    ]
    return "|".join(parts)


oracle_service = OracleService()
