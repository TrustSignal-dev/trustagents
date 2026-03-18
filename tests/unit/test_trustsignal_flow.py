from fastapi.testclient import TestClient

from trustagents.api.app import create_app


client = TestClient(create_app())


def _eval(claims):
    response = client.post(
        "/api/v1/oracle/evaluate",
        headers={"x-tenant-id": "tenant-sim-001"},
        json={"tenantId": "tenant-sim-001", "claimPackage": claims},
    )
    assert response.status_code == 200
    return response.json()


def test_deterministic_replay_with_same_versions():
    claims = {"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"}
    one = _eval(claims)
    two = _eval(claims)
    assert one["fraudRisk"]["score"] == two["fraudRisk"]["score"]
    assert one["versions"] == two["versions"]


def test_manual_review_routing_for_medium_or_high_band():
    claims = {"fullName": "A Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "nomatch"}
    body = _eval(claims)
    assert body["manualReviewRequired"] is True
    assert body["decision"] == "MANUAL_REVIEW"


def test_hard_block_precedence_over_learned_suggestions():
    claims = {"fullName": "Jordan Lee", "dateOfBirth": "1988-04-01", "identifier": "REV-0001", "artifactHash": "revhash", "revoked": True}
    body = _eval(claims)
    assert body["oracleStatus"] == "REVOKED"
    assert body["decision"] == "BLOCK"


def test_reviewed_case_retrieval_and_feedback_capture():
    case = client.post(
        "/api/v1/oracle/review-cases",
        headers={"x-tenant-id": "tenant-sim-001"},
        json={
            "artifactFingerprint": "fp-1",
            "featureDigest": "id12345|1990-01-05|alex carter",
            "fraudSignals": ["identity_ambiguity"],
            "outcome": "MANUAL_REVIEW",
            "reviewerDisposition": "confirmed",
            "falsePositive": False,
            "falseNegative": False,
            "versions": {
                "riskModelVersion": "risk-model-v1",
                "policyVersion": "policy-v1",
                "signalSetVersion": "signals-v1",
                "reviewPolicyVersion": "review-policy-v1",
            },
        },
    )
    assert case.status_code == 200
    case_id = case.json()["caseId"]

    update = client.post(
        "/api/v1/oracle/review-feedback",
        headers={"x-tenant-id": "tenant-sim-001"},
        json={
            "caseId": case_id,
            "reviewerDisposition": "false_positive",
            "falsePositive": True,
            "falseNegative": False,
        },
    )
    assert update.status_code == 200
    assert update.json()["reviewerDisposition"] == "false_positive"

    body = _eval({"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"})
    assert body["fraudRisk"]["similarReviewedCases"]


def test_no_score_drift_without_version_bump():
    claims = {"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "ID-12345", "artifactHash": "abc123"}
    scores = {_eval(claims)["fraudRisk"]["score"] for _ in range(3)}
    assert len(scores) == 1
