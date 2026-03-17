from __future__ import annotations

import json
from pathlib import Path

from trustagents.oracle.models import RetrievalStatus, SourceResult


def fetch(query: dict, path: str) -> tuple[SourceResult, dict]:
    records = json.loads(Path(path).read_text())
    identifier = query.get("identifier")
    for record in records:
        if record.get("identifier") == identifier:
            return (
                SourceResult(
                    source_id="file-source",
                    source_type="file_source",
                    query_performed=query,
                    retrieval_status=RetrievalStatus.SUCCESS,
                ),
                record,
            )
    return (
        SourceResult(
            source_id="file-source",
            source_type="file_source",
            query_performed=query,
            retrieval_status=RetrievalStatus.NO_MATCH,
        ),
        {},
    )
