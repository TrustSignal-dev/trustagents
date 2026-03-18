from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response

from trustagents.auth.helpers import idempotency_store, tenant_guard
from trustagents.config.settings import settings
from trustagents.jobs.store import job_store
from trustagents.learning.case_memory import case_memory_store
from trustagents.oracle.models import (
    JobCreateResponse,
    JobResponse,
    OracleRequest,
    ReviewedCaseInput,
    ReviewerFeedbackInput,
)
from trustagents.oracle.service import oracle_service
from trustagents.review.store import review_queue_store

router = APIRouter()


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
        raise HTTPException(status_code=404, detail="Oracle API disabled")
    if tenant_header != request.tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

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
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    if not settings.feature_flags.async_jobs_enabled:
        raise HTTPException(status_code=400, detail="Async jobs disabled")

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
        raise HTTPException(status_code=404, detail="Job not found")
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
        raise HTTPException(status_code=404, detail="Case not found")
    return case.model_dump(by_alias=True, mode="json")
