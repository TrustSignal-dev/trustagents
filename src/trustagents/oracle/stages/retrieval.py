from __future__ import annotations

from trustagents.connectors import mock_registry
from trustagents.oracle.models import SourceResult


def run_screening(claims: dict) -> tuple[list[SourceResult], dict]:
    source_result, source_payload = mock_registry.fetch(claims)
    return [source_result], source_payload
