from __future__ import annotations

from trustagents.adjudication.core import adjudicate
from trustagents.comparators.core import compare_claims
from trustagents.connectors import mock_registry
from trustagents.extractors.core import extract_claims
from trustagents.ingestion.core import intake_and_fingerprint
from trustagents.normalizers.core import normalize_claims
from trustagents.oracle.models import OracleDecision, OracleRequest
from trustagents.policies.core import evaluate_policies
from trustagents.provenance.trace import build_audit_trace
from trustagents.risk.core import generate_risk_flags


class OracleService:
    def evaluate(self, request: OracleRequest) -> OracleDecision:
        steps = ["request_intake"]
        payload, fingerprint = intake_and_fingerprint(request)
        extracted = extract_claims(payload)
        claims = normalize_claims(extracted["claims"])
        steps.append("claims_extracted_and_normalized")

        source_result, source_payload = mock_registry.fetch(claims)
        source_results = [source_result]
        steps.append("source_retrieval")

        comparisons = compare_claims(claims, source_payload)
        risk_flags = generate_risk_flags(comparisons, source_results)
        policies = evaluate_policies(claims, comparisons, source_results)
        steps.append("comparison_risk_policy")

        status, confidence, score, explanations = adjudicate(policies, risk_flags)
        trace = build_audit_trace(steps + ["adjudication"])
        return OracleDecision(
            oracle_status=status,
            confidence=confidence,
            confidence_score=score,
            artifact_fingerprint=fingerprint,
            source_results=source_results,
            comparison_results=comparisons,
            policy_results=policies,
            risk_flags=risk_flags,
            explanations=explanations,
            audit_trace=trace,
        )


oracle_service = OracleService()
