import hashlib

import pytest

from trustagents.ingestion.core import intake_and_fingerprint
from trustagents.oracle.models import OracleRequest


def test_request_validation_requires_one_payload():
    with pytest.raises(ValueError):
        OracleRequest(tenantId="t1")


def test_fingerprint_deterministic_for_claim_package():
    req1 = OracleRequest(tenantId="t1", claimPackage={"b": 1, "a": 2})
    req2 = OracleRequest(tenantId="t1", claimPackage={"a": 2, "b": 1})
    _, fp1 = intake_and_fingerprint(req1)
    _, fp2 = intake_and_fingerprint(req2)
    assert fp1 == fp2
    assert fp1 == hashlib.sha256(b'{"a":2,"b":1}').hexdigest()
