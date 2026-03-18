"""Tests for the receipt lifecycle: store, verify, revoke, and API endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient

from trustagents.api.app import create_app
from trustagents.receipts.store import ReceiptState, ReceiptStore, receipt_store

HEADERS = {"x-tenant-id": "tenant-sim-001"}
CLAIMS = {
    "fullName": "Alex Carter",
    "dateOfBirth": "1990-01-05",
    "identifier": "ID-12345",
    "artifactHash": "abc123",
}


def _make_client() -> TestClient:
    return TestClient(create_app())


# --- Unit tests for ReceiptStore ---


def test_receipt_store_verify_valid():
    store = ReceiptStore()
    from trustagents.oracle.stages.receipt import build_signed_receipt

    receipt = build_signed_receipt("fp1", "PROCEED", {"risk_model_version": "v1", "policy_version": "v1"})
    store.store(receipt, "tenant-1", "PROCEED")

    result = store.verify(receipt.receipt_id, receipt.fingerprint, receipt.signature)
    assert result["valid"] is True
    assert result["state"] == "ACTIVE"


def test_receipt_store_verify_not_found():
    store = ReceiptStore()
    result = store.verify("nonexistent", "fp", "sig")
    assert result["valid"] is False
    assert result["reason"] == "Receipt not found"


def test_receipt_store_verify_revoked():
    store = ReceiptStore()
    from trustagents.oracle.stages.receipt import build_signed_receipt

    receipt = build_signed_receipt("fp2", "PROCEED", {"risk_model_version": "v1", "policy_version": "v1"})
    store.store(receipt, "tenant-1", "PROCEED")
    store.revoke(receipt.receipt_id, "test revocation")

    result = store.verify(receipt.receipt_id, receipt.fingerprint, receipt.signature)
    assert result["valid"] is False
    assert result["state"] == "REVOKED"


def test_receipt_store_verify_fingerprint_mismatch():
    store = ReceiptStore()
    from trustagents.oracle.stages.receipt import build_signed_receipt

    receipt = build_signed_receipt("fp3", "PROCEED", {"risk_model_version": "v1", "policy_version": "v1"})
    store.store(receipt, "tenant-1", "PROCEED")

    result = store.verify(receipt.receipt_id, "wrong-fingerprint", receipt.signature)
    assert result["valid"] is False
    assert result["reason"] == "Fingerprint mismatch"


def test_receipt_store_verify_signature_mismatch():
    store = ReceiptStore()
    from trustagents.oracle.stages.receipt import build_signed_receipt

    receipt = build_signed_receipt("fp4", "PROCEED", {"risk_model_version": "v1", "policy_version": "v1"})
    store.store(receipt, "tenant-1", "PROCEED")

    result = store.verify(receipt.receipt_id, receipt.fingerprint, "wrong-signature")
    assert result["valid"] is False
    assert result["reason"] == "Signature mismatch"


def test_receipt_store_revoke_returns_none_for_missing():
    store = ReceiptStore()
    assert store.revoke("nonexistent", "reason") is None


def test_receipt_store_revoke_sets_state():
    store = ReceiptStore()
    from trustagents.oracle.stages.receipt import build_signed_receipt

    receipt = build_signed_receipt("fp5", "PROCEED", {"risk_model_version": "v1", "policy_version": "v1"})
    store.store(receipt, "tenant-1", "PROCEED")

    record = store.revoke(receipt.receipt_id, "compliance issue")
    assert record.state == ReceiptState.REVOKED
    assert record.revocation_reason == "compliance issue"
    assert record.revoked_at is not None


# --- API integration tests ---


def test_evaluate_populates_receipt_store():
    """Evaluating a claim should store the receipt for later lookup."""
    client = _make_client()
    resp = client.post(
        "/api/v1/oracle/evaluate",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": CLAIMS},
    )
    assert resp.status_code == 200
    body = resp.json()
    receipt_id = body["signedReceipt"]["receiptId"]

    # Receipt should now be retrievable
    status_resp = client.get(f"/api/v1/oracle/receipts/{receipt_id}", headers=HEADERS)
    assert status_resp.status_code == 200
    status_body = status_resp.json()
    assert status_body["state"] == "ACTIVE"
    assert status_body["tenantId"] == "tenant-sim-001"


def test_verify_receipt_endpoint():
    """Verify endpoint should confirm a valid receipt."""
    client = _make_client()
    eval_resp = client.post(
        "/api/v1/oracle/evaluate",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": CLAIMS},
    )
    body = eval_resp.json()
    receipt = body["signedReceipt"]

    verify_resp = client.post(
        "/api/v1/oracle/receipts/verify",
        headers=HEADERS,
        json={
            "receiptId": receipt["receiptId"],
            "fingerprint": receipt["fingerprint"],
            "signature": receipt["signature"],
        },
    )
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()
    assert verify_body["valid"] is True
    assert verify_body["state"] == "ACTIVE"


def test_revoke_receipt_endpoint():
    """Revoke endpoint should transition receipt to REVOKED state."""
    client = _make_client()
    eval_resp = client.post(
        "/api/v1/oracle/evaluate",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": CLAIMS},
    )
    receipt_id = eval_resp.json()["signedReceipt"]["receiptId"]

    revoke_resp = client.post(
        "/api/v1/oracle/receipts/revoke",
        headers=HEADERS,
        json={"receiptId": receipt_id, "reason": "Audit finding"},
    )
    assert revoke_resp.status_code == 200
    revoke_body = revoke_resp.json()
    assert revoke_body["state"] == "REVOKED"
    assert revoke_body["reason"] == "Audit finding"


def test_revoke_already_revoked_returns_409():
    """Revoking an already-revoked receipt should return a 409 Conflict."""
    client = _make_client()
    eval_resp = client.post(
        "/api/v1/oracle/evaluate",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": CLAIMS},
    )
    receipt_id = eval_resp.json()["signedReceipt"]["receiptId"]

    client.post(
        "/api/v1/oracle/receipts/revoke",
        headers=HEADERS,
        json={"receiptId": receipt_id, "reason": "First revocation"},
    )
    second_resp = client.post(
        "/api/v1/oracle/receipts/revoke",
        headers=HEADERS,
        json={"receiptId": receipt_id, "reason": "Second attempt"},
    )
    assert second_resp.status_code == 409


def test_verify_revoked_receipt():
    """Verifying a revoked receipt should report it as invalid."""
    client = _make_client()
    eval_resp = client.post(
        "/api/v1/oracle/evaluate",
        headers=HEADERS,
        json={"tenantId": "tenant-sim-001", "claimPackage": CLAIMS},
    )
    body = eval_resp.json()
    receipt = body["signedReceipt"]

    client.post(
        "/api/v1/oracle/receipts/revoke",
        headers=HEADERS,
        json={"receiptId": receipt["receiptId"], "reason": "Revoked for test"},
    )

    verify_resp = client.post(
        "/api/v1/oracle/receipts/verify",
        headers=HEADERS,
        json={
            "receiptId": receipt["receiptId"],
            "fingerprint": receipt["fingerprint"],
            "signature": receipt["signature"],
        },
    )
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()
    assert verify_body["valid"] is False
    assert verify_body["state"] == "REVOKED"


def test_get_receipt_not_found():
    """Looking up a nonexistent receipt should return 404."""
    client = _make_client()
    resp = client.get("/api/v1/oracle/receipts/nonexistent", headers=HEADERS)
    assert resp.status_code == 404


def test_revoke_nonexistent_receipt():
    """Revoking a nonexistent receipt should return 404."""
    client = _make_client()
    resp = client.post(
        "/api/v1/oracle/receipts/revoke",
        headers=HEADERS,
        json={"receiptId": "nonexistent", "reason": "test"},
    )
    assert resp.status_code == 404
