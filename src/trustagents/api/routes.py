from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response

from trustagents.api.errors import (
    ASYNC_JOBS_DISABLED,
    CASE_NOT_FOUND,
    GITHUB_APP_DISABLED,
    JOB_NOT_FOUND,
    ORACLE_API_DISABLED,
    RECEIPT_ALREADY_REVOKED,
    RECEIPT_NOT_FOUND,
    TENANT_MISMATCH,
)
from trustagents.auth.helpers import idempotency_store, tenant_guard
from trustagents.config.settings import settings
from trustagents.github_app.webhook import verify_webhook_request
from trustagents.jobs.store import job_store
from trustagents.learning.case_memory import case_memory_store
from trustagents.observability import get_logger, log_stage
from trustagents.oracle.models import (
    JobCreateResponse,
    JobResponse,
    OracleRequest,
    ReceiptRevokeRequest,
    ReceiptRevokeResponse,
    ReceiptStatusResponse,
    ReceiptVerifyRequest,
    ReceiptVerifyResponse,
    ReviewedCaseInput,
    ReviewerFeedbackInput,
)
from trustagents.oracle.service import oracle_service
from trustagents.receipts.store import ReceiptState, receipt_store
from trustagents.review.store import review_queue_store

router = APIRouter()

_webhook_logger = get_logger("api.webhook")


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "trustagents"}


@router.post("/api/v1/oracle/evaluate")
async def evaluate(
    request: OracleRequest,
    response: Response,
    tenant_header: str = Depends(tenant_guard),
    x_idempotency_key: str | None = Header(default=None),
):
    if not settings.feature_flags.oracle_api_enabled:
        ORACLE_API_DISABLED.raise_http()
    if tenant_header != request.tenant_id:
        TENANT_MISMATCH.raise_http()

    idempotency_key = request.idempotency_key or x_idempotency_key
    decision = oracle_service.evaluate(request)
    if idempotency_key:
        existing = idempotency_store.get(request.tenant_id, idempotency_key, decision.artifact_fingerprint)
        if existing:
            response.headers["X-Idempotent-Replay"] = "true"
            return existing

    payload = decision.model_dump(by_alias=True, mode="json")
    if idempotency_key:
        idempotency_store.set(request.tenant_id, idempotency_key, decision.artifact_fingerprint, payload)
    return payload


@router.post("/api/v1/oracle/jobs", response_model=JobCreateResponse)
async def create_job(request: OracleRequest, tenant_header: str = Depends(tenant_guard)):
    if tenant_header != request.tenant_id:
        TENANT_MISMATCH.raise_http()
    if not settings.feature_flags.async_jobs_enabled:
        ASYNC_JOBS_DISABLED.raise_http()

    job_id = job_store.create()
    try:
        job_store.set_running(job_id)
        result = oracle_service.evaluate(request)
        job_store.set_completed(job_id, result)
    except Exception as exc:  # noqa: BLE001
        job_store.set_failed(job_id, str(exc))

    return JobCreateResponse(job_id=job_id, status=job_store.get(job_id).status, location=f"/api/v1/oracle/jobs/{job_id}")


@router.get("/api/v1/oracle/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, _: str = Depends(tenant_guard)):
    job = job_store.get(job_id)
    if not job:
        JOB_NOT_FOUND.raise_http()
    return job


@router.get("/api/v1/oracle/review-queue")
async def list_review_queue(_: str = Depends(tenant_guard)):
    return {"items": review_queue_store.list_items()}


@router.post("/api/v1/oracle/review-cases")
async def record_review_case(payload: ReviewedCaseInput, _: str = Depends(tenant_guard)):
    case = case_memory_store.add_case(payload)
    return case.model_dump(by_alias=True, mode="json")


@router.post("/api/v1/oracle/review-feedback")
async def record_feedback(payload: ReviewerFeedbackInput, _: str = Depends(tenant_guard)):
    case = case_memory_store.apply_feedback(payload)
    if not case:
        CASE_NOT_FOUND.raise_http()
    return case.model_dump(by_alias=True, mode="json")


# --- Receipt lifecycle endpoints ---


@router.post("/api/v1/oracle/receipts/verify", response_model=ReceiptVerifyResponse)
async def verify_receipt(payload: ReceiptVerifyRequest, _: str = Depends(tenant_guard)):
    result = receipt_store.verify(payload.receipt_id, payload.fingerprint, payload.signature)
    return ReceiptVerifyResponse(**result)


@router.post("/api/v1/oracle/receipts/revoke", response_model=ReceiptRevokeResponse)
async def revoke_receipt(payload: ReceiptRevokeRequest, _: str = Depends(tenant_guard)):
    record = receipt_store.get(payload.receipt_id)
    if record is None:
        RECEIPT_NOT_FOUND.raise_http()
    if record.state == ReceiptState.REVOKED:
        RECEIPT_ALREADY_REVOKED.raise_http()
    record = receipt_store.revoke(payload.receipt_id, payload.reason)
    return ReceiptRevokeResponse(
        receipt_id=payload.receipt_id,
        state=record.state.value,
        revoked_at=record.revoked_at.isoformat(),
        reason=record.revocation_reason,
    )


@router.get("/api/v1/oracle/receipts/{receipt_id}", response_model=ReceiptStatusResponse)
async def get_receipt(receipt_id: str, _: str = Depends(tenant_guard)):
    record = receipt_store.get(receipt_id)
    if record is None:
        RECEIPT_NOT_FOUND.raise_http()
    return ReceiptStatusResponse(
        receipt_id=receipt_id,
        state=record.state.value,
        tenant_id=record.tenant_id,
        decision=record.decision,
        fingerprint=record.receipt.fingerprint,
        issued_at=record.receipt.issued_at.isoformat(),
        revoked_at=record.revoked_at.isoformat() if record.revoked_at else None,
        revocation_reason=record.revocation_reason,
    )


# --- GitHub App webhook ingress ---


@router.post("/api/v1/github/webhook")
async def github_webhook(request: Request) -> dict:
    """GitHub App webhook ingress endpoint.

    Security pipeline (in order):
    1. Feature-flag gate — returns 404 if disabled.
    2. Body-size enforcement (10 KB limit).
    3. HMAC-SHA256 signature verification (timing-safe).
    4. Delivery-ID replay protection.
    5. Pydantic schema validation.
    6. Business-logic dispatch.

    Returns 200 with an ``accepted`` envelope on success.
    Returns 4xx/5xx with a structured error body on any failure.
    """
    if not settings.feature_flags.github_app_webhook_enabled:
        GITHUB_APP_DISABLED.raise_http()

    with log_stage(_webhook_logger, "github_webhook_ingress"):
        event_type, delivery_id, payload, raw = await verify_webhook_request(request)

    _webhook_logger.info(
        "webhook_dispatched",
        extra={
            "event": event_type,
            "delivery_id": delivery_id,
            "action": payload.action,
            "installation_id": payload.installation.id if payload.installation else None,
        },
    )

    return {
        "accepted": True,
        "delivery_id": delivery_id,
        "event": event_type,
        "action": payload.action,
    }
