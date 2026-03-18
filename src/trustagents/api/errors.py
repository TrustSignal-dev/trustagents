from __future__ import annotations

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class OracleError:
    """Structured error builder for consistent API error responses."""

    def __init__(self, code: str, message: str, *, status_code: int = 400, detail: str | None = None, retryable: bool = False):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.retryable = retryable

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={
                "error": {
                    "code": self.code,
                    "message": self.message,
                    "detail": self.detail,
                    "retryable": self.retryable,
                }
            },
        )

    def raise_http(self) -> None:
        raise HTTPException(
            status_code=self.status_code,
            detail={
                "code": self.code,
                "message": self.message,
                "detail": self.detail,
                "retryable": self.retryable,
            },
        )


# Pre-defined error constants
RECEIPT_NOT_FOUND = OracleError("RECEIPT_NOT_FOUND", "No receipt found with the given ID", status_code=404)
RECEIPT_ALREADY_REVOKED = OracleError("RECEIPT_ALREADY_REVOKED", "Receipt is already revoked", status_code=409)
ORACLE_API_DISABLED = OracleError("ORACLE_API_DISABLED", "Oracle API is disabled", status_code=404)
TENANT_MISMATCH = OracleError("TENANT_MISMATCH", "Tenant header does not match request", status_code=403)
ASYNC_JOBS_DISABLED = OracleError("ASYNC_JOBS_DISABLED", "Async jobs feature is disabled", status_code=400)
JOB_NOT_FOUND = OracleError("JOB_NOT_FOUND", "Job not found", status_code=404)
CASE_NOT_FOUND = OracleError("CASE_NOT_FOUND", "Case not found", status_code=404)
