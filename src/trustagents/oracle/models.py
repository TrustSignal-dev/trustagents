from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)


class OracleStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    CONFLICTED = "CONFLICTED"
    UNVERIFIABLE = "UNVERIFIABLE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RetrievalStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NO_MATCH = "NO_MATCH"
    TIMEOUT = "TIMEOUT"
    UNAVAILABLE = "UNAVAILABLE"
    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FraudRiskBand(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ReviewRecommendation(str, Enum):
    NONE = "NONE"
    RECOMMENDED = "RECOMMENDED"
    REQUIRED = "REQUIRED"


class ScoringMode(str, Enum):
    DETERMINISTIC_RULES = "DETERMINISTIC_RULES"
    LEARNED_MODEL_ASSISTED = "LEARNED_MODEL_ASSISTED"
    HYBRID = "HYBRID"


class DecisionAction(str, Enum):
    PROCEED = "PROCEED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BLOCK = "BLOCK"


class Artifact(CamelModel):
    payload_base64: str | None = None
    payload_text: str | None = None
    content_type: str = "application/octet-stream"
    encoding: str | None = None


class OracleRequest(CamelModel):
    tenant_id: str
    artifact: Artifact | None = None
    claim_package: dict[str, Any] | None = None
    policy_profile: str | None = "conservative"
    source_selection: list[str] | None = None
    idempotency_key: str | None = None
    prefer_async: bool = False

    @model_validator(mode="after")
    def validate_payload(self) -> "OracleRequest":
        if not self.artifact and not self.claim_package:
            raise ValueError("Either artifact or claimPackage must be provided")
        if self.artifact and self.claim_package:
            raise ValueError("Provide either artifact or claimPackage, not both")
        return self


class SourceResult(CamelModel):
    source_id: str
    source_type: str
    query_performed: dict[str, Any]
    retrieval_status: RetrievalStatus
    matched_fields: dict[str, Any] = Field(default_factory=dict)
    conflicting_fields: dict[str, Any] = Field(default_factory=dict)
    source_freshness: str = "fresh"
    source_errors: list[str] = Field(default_factory=list)


class ComparisonResult(CamelModel):
    field: str
    original_value: Any = None
    normalized_value: Any = None
    source_value: Any = None
    normalized_source_value: Any = None
    result: str
    severity: str
    explanation: str


class PipelineVersions(CamelModel):
    risk_model_version: str = "risk-model-v1"
    policy_version: str = "policy-v1"
    signal_set_version: str = "signals-v1"
    review_policy_version: str = "review-policy-v1"


class SimilarCaseReference(CamelModel):
    case_id: str
    similarity_score: float
    outcome: str
    reviewer_disposition: str


class FraudSignal(CamelModel):
    signal_id: str
    contribution: float
    reason: str


class FraudRisk(CamelModel):
    score: float
    band: FraudRiskBand
    confidence: Confidence
    scoring_mode: ScoringMode
    top_contributing_signals: list[FraudSignal]
    review_recommendation: ReviewRecommendation
    similar_reviewed_cases: list[SimilarCaseReference] = Field(default_factory=list)


class SignedReceipt(CamelModel):
    receipt_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signature: str
    fingerprint: str


class AnchorRecord(CamelModel):
    anchor_id: str
    status: str
    anchored_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OracleDecision(CamelModel):
    schema_version: str = "1.1"
    oracle_status: OracleStatus
    decision: DecisionAction
    confidence: Confidence
    confidence_score: float
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    artifact_fingerprint: str
    source_results: list[SourceResult]
    comparison_results: list[ComparisonResult]
    policy_results: list[str]
    risk_flags: list[str]
    reasons: list[str]
    explanations: list[str]
    fraud_risk: FraudRisk
    versions: PipelineVersions
    signed_receipt: SignedReceipt
    anchor_record: AnchorRecord
    manual_review_required: bool = False
    audit_trace: list[str]


class JobCreateResponse(CamelModel):
    job_id: str
    status: str
    location: str


class JobResponse(CamelModel):
    job_id: str
    status: str
    result: OracleDecision | None = None
    error: str | None = None


class ReviewedCaseInput(CamelModel):
    artifact_fingerprint: str
    feature_digest: str
    fraud_signals: list[str]
    outcome: str
    reviewer_disposition: str
    false_positive: bool = False
    false_negative: bool = False
    versions: PipelineVersions


class ReviewedCaseRecord(ReviewedCaseInput):
    case_id: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReviewerFeedbackInput(CamelModel):
    case_id: str
    reviewer_disposition: str
    false_positive: bool = False
    false_negative: bool = False


class ReceiptVerifyRequest(CamelModel):
    receipt_id: str
    fingerprint: str
    signature: str


class ReceiptVerifyResponse(CamelModel):
    valid: bool
    reason: str
    state: str | None = None
    revoked_at: str | None = None


class ReceiptRevokeRequest(CamelModel):
    receipt_id: str
    reason: str


class ReceiptRevokeResponse(CamelModel):
    receipt_id: str
    state: str
    revoked_at: str
    reason: str


class ReceiptStatusResponse(CamelModel):
    receipt_id: str
    state: str
    tenant_id: str
    decision: str
    fingerprint: str
    issued_at: str
    revoked_at: str | None = None
    revocation_reason: str | None = None
