from trustagents.adjudication.core import adjudicate
from trustagents.oracle.models import OracleStatus


def test_revoked_precedence_over_expired():
    status, _, _, _ = adjudicate(["expired", "revoked"], [])
    assert status == OracleStatus.REVOKED


def test_expired_when_not_revoked():
    status, _, _, _ = adjudicate(["expired"], [])
    assert status == OracleStatus.EXPIRED
