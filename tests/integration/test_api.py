from fastapi.testclient import TestClient

from trustagents.api.app import create_app
from trustagents.config.settings import settings


client = TestClient(create_app())


def _request_payload(**overrides):
    payload = {
        "tenantId": "tenant-sim-001",
        "claimPackage": {
            "fullName": "Alex Carter",
            "dateOfBirth": "1990-01-05",
            "identifier": "ID-12345",
            "artifactHash": "abc123",
        },
    }
    payload.update(overrides)
    return payload


def test_evaluate_happy_path():
    response = client.post(
        "/api/v1/oracle/evaluate",
        headers={"x-tenant-id": "tenant-sim-001"},
        json=_request_payload(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schemaVersion"] == "1.1"
    assert body["oracleStatus"] == "VALID"


def test_idempotency_replay():
    headers = {"x-tenant-id": "tenant-sim-001", "x-idempotency-key": "abc"}
    first = client.post("/api/v1/oracle/evaluate", headers=headers, json=_request_payload())
    second = client.post("/api/v1/oracle/evaluate", headers=headers, json=_request_payload())
    assert first.status_code == second.status_code == 200
    assert second.headers["X-Idempotent-Replay"] == "true"


def test_jobs_feature_flag_enforced():
    settings.feature_flags.async_jobs_enabled = False
    response = client.post(
        "/api/v1/oracle/jobs",
        headers={"x-tenant-id": "tenant-sim-001"},
        json=_request_payload(),
    )
    assert response.status_code == 400


def test_jobs_roundtrip_when_enabled():
    settings.feature_flags.async_jobs_enabled = True
    create = client.post(
        "/api/v1/oracle/jobs",
        headers={"x-tenant-id": "tenant-sim-001"},
        json=_request_payload(),
    )
    assert create.status_code == 200
    job_id = create.json()["jobId"]
    get_resp = client.get(f"/api/v1/oracle/jobs/{job_id}", headers={"x-tenant-id": "tenant-sim-001"})
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"
    settings.feature_flags.async_jobs_enabled = False
