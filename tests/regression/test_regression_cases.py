from fastapi.testclient import TestClient

from trustagents.api.app import create_app

client = TestClient(create_app())


def eval_claims(claims):
    resp = client.post(
        "/api/v1/oracle/evaluate",
        headers={"x-tenant-id": "tenant-sim-001"},
        json={"tenantId": "tenant-sim-001", "claimPackage": claims},
    )
    assert resp.status_code == 200
    return resp.json()


def test_one_character_typo_not_valid():
    body = eval_claims({"fullName": "Alex Cartez", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"})
    assert body["oracleStatus"] != "VALID"


def test_swapped_names_raise_ambiguity():
    body = eval_claims({"fullName": "Carter Alex", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"})
    assert "identity_ambiguity" in body["riskFlags"]


def test_initials_vs_full_name_not_silent_valid():
    body = eval_claims({"fullName": "A Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"})
    assert body["oracleStatus"] != "VALID"


def test_punctuation_id_differences_normalize():
    body = eval_claims({"fullName": "Alex Carter", "dateOfBirth": "01/05/1990", "identifier": "ID 12345", "artifactHash": "abc123"})
    assert body["oracleStatus"] == "VALID"


def test_revoked_not_expired_returns_revoked():
    body = eval_claims({"fullName": "Jordan Lee", "dateOfBirth": "1988-04-01", "identifier": "REV-0001", "artifactHash": "revhash", "revoked": True})
    assert body["oracleStatus"] == "REVOKED"


def test_stable_output_for_same_input():
    claims = {"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"}
    one = eval_claims(claims)
    two = eval_claims(claims)
    assert one["artifactFingerprint"] == two["artifactFingerprint"]
    assert one["oracleStatus"] == two["oracleStatus"]
