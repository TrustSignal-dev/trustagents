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


class OracleDecision(CamelModel):
    schema_version: str = "1.0"
    oracle_status: OracleStatus
    confidence: Confidence
    confidence_score: float
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    artifact_fingerprint: str
    source_results: list[SourceResult]
    comparison_results: list[ComparisonResult]
    policy_results: list[str]
    risk_flags: list[str]
    explanations: list[str]
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
