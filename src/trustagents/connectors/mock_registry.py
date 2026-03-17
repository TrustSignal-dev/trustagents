from __future__ import annotations

import re

from trustagents.oracle.models import RetrievalStatus, SourceResult


MOCK_REGISTRY = {
    "id12345": {
        "fullName": "Alex Carter",
        "dateOfBirth": "1990-01-05",
        "identifier": "ID-12345",
        "artifactHash": "abc123",
        "revoked": False,
        "expired": False,
    },
    "revoked001": {
        "fullName": "Jordan Lee",
        "dateOfBirth": "1988-04-01",
        "identifier": "REV-0001",
        "artifactHash": "revhash",
        "revoked": True,
        "expired": False,
    },
}


def fetch(query: dict) -> tuple[SourceResult, dict]:
    identifier = re.sub(r"[^a-zA-Z0-9]", "", str(query.get("identifier", "")).lower())
    record = MOCK_REGISTRY.get(identifier)
    if not record:
        return (
            SourceResult(
                source_id="mock-registry",
                source_type="mock_registry",
                query_performed=query,
                retrieval_status=RetrievalStatus.NO_MATCH,
            ),
            {},
        )

    return (
        SourceResult(
            source_id="mock-registry",
            source_type="mock_registry",
            query_performed=query,
            retrieval_status=RetrievalStatus.SUCCESS,
            matched_fields={"identifier": query.get("identifier")},
            source_freshness="fresh",
        ),
        record,
    )
