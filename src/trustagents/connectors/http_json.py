from __future__ import annotations

import httpx

from trustagents.oracle.models import RetrievalStatus, SourceResult


def fetch(query: dict, url: str, timeout_s: float = 2.0) -> tuple[SourceResult, dict]:
    try:
        response = httpx.get(url, params=query, timeout=timeout_s)
        response.raise_for_status()
        data = response.json()
        return (
            SourceResult(
                source_id="http-json",
                source_type="http_json",
                query_performed=query,
                retrieval_status=RetrievalStatus.SUCCESS,
                source_freshness=data.get("sourceFreshness", "unknown"),
            ),
            data,
        )
    except httpx.TimeoutException:
        return (
            SourceResult(
                source_id="http-json",
                source_type="http_json",
                query_performed=query,
                retrieval_status=RetrievalStatus.TIMEOUT,
                source_errors=["timeout"],
            ),
            {},
        )
    except httpx.HTTPError as exc:
        return (
            SourceResult(
                source_id="http-json",
                source_type="http_json",
                query_performed=query,
                retrieval_status=RetrievalStatus.UNAVAILABLE,
                source_errors=[str(exc)],
            ),
            {},
        )
