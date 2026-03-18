"""Tests for the structured error responses and retry wrapper."""
from __future__ import annotations

from fastapi.testclient import TestClient

from trustagents.api.app import create_app
from trustagents.api.errors import OracleError
from trustagents.connectors.retry import with_retry

HEADERS = {"x-tenant-id": "tenant-sim-001"}


def test_oracle_error_to_response():
    err = OracleError("TEST_CODE", "Test message", status_code=422, detail="extra", retryable=True)
    resp = err.to_response()
    assert resp.status_code == 422
    import json

    body = json.loads(resp.body)
    assert body["error"]["code"] == "TEST_CODE"
    assert body["error"]["retryable"] is True


def test_structured_error_on_tenant_mismatch():
    client = TestClient(create_app())
    resp = client.post(
        "/api/v1/oracle/evaluate",
        headers={"x-tenant-id": "wrong-tenant"},
        json={"tenantId": "tenant-sim-001", "claimPackage": {"fullName": "X"}},
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["detail"]["code"] == "TENANT_MISMATCH"


def test_structured_error_on_async_jobs_disabled():
    client = TestClient(create_app())
    resp = client.post(
        "/api/v1/oracle/jobs",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": {"fullName": "X"}},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"]["code"] == "ASYNC_JOBS_DISABLED"


# --- Retry wrapper ---


def test_retry_succeeds_on_first_attempt():
    calls = []

    def fn():
        calls.append(1)
        return "ok"

    result = with_retry(fn, max_retries=2, base_delay=0.01)
    assert result == "ok"
    assert len(calls) == 1


def test_retry_recovers_after_transient_failure():
    attempts = []

    def fn():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("transient")
        return "recovered"

    result = with_retry(fn, max_retries=3, base_delay=0.01, retryable_exceptions=(ConnectionError,))
    assert result == "recovered"
    assert len(attempts) == 3


def test_retry_propagates_after_exhaustion():
    import pytest

    def fn():
        raise ValueError("permanent")

    with pytest.raises(ValueError, match="permanent"):
        with_retry(fn, max_retries=1, base_delay=0.01, retryable_exceptions=(ValueError,))


def test_retry_does_not_catch_non_retryable():
    import pytest

    def fn():
        raise TypeError("not retryable")

    with pytest.raises(TypeError, match="not retryable"):
        with_retry(fn, max_retries=3, base_delay=0.01, retryable_exceptions=(ValueError,))
