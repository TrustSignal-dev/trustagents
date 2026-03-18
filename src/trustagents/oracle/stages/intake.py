from __future__ import annotations

from trustagents.ingestion.core import intake_and_fingerprint
from trustagents.oracle.models import OracleRequest


def run_intake(request: OracleRequest) -> tuple[dict, str]:
    return intake_and_fingerprint(request)
