"""Integration tests for GitHub App webhook ingress.

Covers:
- valid webhook accepted
- invalid / missing signature rejected
- replayed delivery rejected
- malformed payload rejected
- missing delivery header rejected
- body too large rejected
- feature flag gate
- downstream check-run dispatch logging (observability)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os

import pytest
from fastapi.testclient import TestClient

from trustagents.api.app import create_app
from trustagents.config.settings import settings
from trustagents.github_app.replay_store import InMemoryReplayStore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WEBHOOK_SECRET = "test-webhook-secret-for-integration"

_MINIMAL_PAYLOAD: dict = {
    "action": "created",
    "installation": {"id": 12345, "account": {"login": "test-org", "type": "Organization"}},
    "sender": {"id": 99, "login": "octocat", "type": "User"},
    "repository": {"id": 1, "full_name": "test-org/test-repo", "private": False},
    "check_suite": {"id": 1, "head_sha": "a" * 40, "head_branch": "main"},
}


def _sign(body: bytes, secret: str = _WEBHOOK_SECRET) -> str:
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def _make_headers(
    body: bytes,
    delivery_id: str = "abc-001",
    event: str = "check_suite",
    secret: str = _WEBHOOK_SECRET,
) -> dict[str, str]:
    return {
        "x-hub-signature-256": _sign(body, secret),
        "x-github-delivery": delivery_id,
        "x-github-event": event,
        "content-type": "application/json",
    }


@pytest.fixture(autouse=True)
def _enable_webhook_flag(monkeypatch):
    """Enable the feature flag and inject the test secret for every test."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", _WEBHOOK_SECRET)
    settings.feature_flags.github_app_webhook_enabled = True
    yield
    settings.feature_flags.github_app_webhook_enabled = False


@pytest.fixture()
def client():
    return TestClient(create_app(), raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_webhook_accepted(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    resp = client.post(
        "/api/v1/github/webhook",
        content=body,
        headers=_make_headers(body, delivery_id="unique-delivery-001"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["accepted"] is True
    assert data["event"] == "check_suite"
    assert data["delivery_id"] == "unique-delivery-001"


# ---------------------------------------------------------------------------
# Signature validation
# ---------------------------------------------------------------------------


def test_missing_signature_rejected(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    headers = {
        "x-github-delivery": "delivery-no-sig",
        "x-github-event": "check_suite",
        "content-type": "application/json",
    }
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 401
    detail = resp.json()["detail"]
    assert detail["code"] == "SIGNATURE_INVALID"


def test_invalid_signature_rejected(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    headers = _make_headers(body, delivery_id="delivery-bad-sig", secret="wrong-secret")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "SIGNATURE_INVALID"


def test_malformed_signature_format_rejected(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    headers = _make_headers(body, delivery_id="delivery-bad-format")
    # Replace the correct signature with a malformed one
    headers["x-hub-signature-256"] = "notsha256=abc"
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "SIGNATURE_INVALID"


# ---------------------------------------------------------------------------
# Replay protection
# ---------------------------------------------------------------------------


def test_replayed_delivery_rejected(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    delivery_id = "replay-test-delivery-001"
    headers = _make_headers(body, delivery_id=delivery_id)

    first = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert first.status_code == 200, first.text

    second = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "DELIVERY_REPLAYED"


def test_missing_delivery_id_rejected(client):
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    sig = _sign(body)
    headers = {
        "x-hub-signature-256": sig,
        "x-github-event": "check_suite",
        "content-type": "application/json",
    }
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "DELIVERY_REPLAYED"


# ---------------------------------------------------------------------------
# Payload validation
# ---------------------------------------------------------------------------


def test_malformed_json_rejected(client):
    body = b"not valid json {"
    headers = _make_headers(body, delivery_id="malformed-json-001")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "PAYLOAD_INVALID"


def test_schema_validation_failure_rejected(client):
    # Payload missing both 'sender' and 'installation'
    payload = {"action": "created", "repository": {"id": 1, "full_name": "a/b", "private": False}}
    body = json.dumps(payload).encode()
    headers = _make_headers(body, delivery_id="schema-fail-001")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "PAYLOAD_INVALID"


def test_body_too_large_rejected(client):
    oversized_payload = {"action": "ping", "sender": {"id": 1, "login": "x"}, "data": "x" * (10 * 1024 + 1)}
    body = json.dumps(oversized_payload).encode()
    headers = _make_headers(body, delivery_id="too-large-001")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "PAYLOAD_TOO_LARGE"


# ---------------------------------------------------------------------------
# Feature flag gate
# ---------------------------------------------------------------------------


def test_feature_flag_disabled_returns_404(client):
    settings.feature_flags.github_app_webhook_enabled = False
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    headers = _make_headers(body, delivery_id="disabled-001")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Duplicate event handling (idempotency)
# ---------------------------------------------------------------------------


def test_different_delivery_ids_both_accepted(client):
    """Two deliveries with different IDs for the same event should both succeed."""
    body = json.dumps(_MINIMAL_PAYLOAD).encode()

    r1 = client.post(
        "/api/v1/github/webhook",
        content=body,
        headers=_make_headers(body, delivery_id="dup-event-001"),
    )
    r2 = client.post(
        "/api/v1/github/webhook",
        content=body,
        headers=_make_headers(body, delivery_id="dup-event-002"),
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["delivery_id"] != r2.json()["delivery_id"]


# ---------------------------------------------------------------------------
# Secret not configured
# ---------------------------------------------------------------------------


def test_missing_secret_returns_500(client, monkeypatch):
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    body = json.dumps(_MINIMAL_PAYLOAD).encode()
    headers = _make_headers(body, delivery_id="no-secret-001")
    resp = client.post("/api/v1/github/webhook", content=body, headers=headers)
    assert resp.status_code == 500
    assert resp.json()["detail"]["code"] == "WEBHOOK_SECRET_NOT_CONFIGURED"


# ---------------------------------------------------------------------------
# Replay store unit tests
# ---------------------------------------------------------------------------


def test_replay_store_marks_and_detects():
    store = InMemoryReplayStore()
    assert not store.is_seen("d1")
    store.mark_seen("d1")
    assert store.is_seen("d1")


def test_replay_store_ttl_expiry():
    store = InMemoryReplayStore(ttl_seconds=0)  # Expires immediately
    store.mark_seen("d2")
    # After a TTL of 0 seconds the entry expires on the next is_seen check
    import time
    time.sleep(0.01)
    assert not store.is_seen("d2")


def test_replay_store_independent_entries():
    store = InMemoryReplayStore()
    store.mark_seen("d3")
    assert not store.is_seen("d4")
    assert store.is_seen("d3")
