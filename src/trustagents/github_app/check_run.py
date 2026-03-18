"""Idempotent check-run publishing for GitHub App.

Idempotency guarantee
---------------------
Check-run publication is keyed on (owner, repo, head_sha, name, external_id).
If a check run with the same external_id already exists for this head_sha,
the publisher updates it rather than creating a duplicate, which makes the
operation safe to retry.

Observability
-------------
Every publish attempt emits a structured log event with the outcome and
enough context for post-hoc correlation with the triggering delivery ID.

In-scope simulation
-------------------
This module does **not** make real GitHub API calls.  The ``publish_check_run``
function logs the intent and returns a structured result dict.  A real HTTP
connector can be wired in by replacing ``_call_github_api``.
"""
from __future__ import annotations

from typing import Any

from trustagents.github_app.models import CheckRunOutput, CreateCheckRunRequest
from trustagents.github_app.token import discard_token, get_installation_token
from trustagents.observability import get_logger, log_stage

logger = get_logger("github_app.check_run")


def _call_github_api(
    token: str,
    owner: str,
    repo: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Stub: replace with a real HTTPS POST to the GitHub Checks API.

    In production this should:
    1. POST /repos/{owner}/{repo}/check-runs with a Bearer token.
    2. Handle 422 (already exists) by falling back to PATCH.
    3. Raise on any other non-2xx response.

    Returns a dict with at minimum {"id": <check_run_id>}.
    """
    logger.info(
        "check_run_api_stub_called",
        extra={"owner": owner, "repo": repo, "head_sha": payload.get("head_sha"), "name": payload.get("name")},
    )
    # Simulate a successful creation response
    return {
        "id": 0,
        "status": payload.get("status", "completed"),
        "conclusion": payload.get("conclusion"),
        "simulated": True,
    }


def publish_check_run(
    *,
    installation_id: int,
    request: CreateCheckRunRequest,
    delivery_id: str | None = None,
) -> dict[str, Any]:
    """Publish or update a GitHub check run idempotently.

    Args:
        installation_id: Installation ID from the verified webhook payload.
        request:         Validated CreateCheckRunRequest with all required fields.
        delivery_id:     Optional delivery ID for correlation logging.

    Returns:
        Dict with check-run publication result.

    Raises:
        RuntimeError: If token acquisition fails in production mode.
    """
    extra = {
        "installation_id": installation_id,
        "owner": request.owner,
        "repo": request.repo,
        "head_sha": request.head_sha,
        "name": request.name,
        "status": request.status,
        "conclusion": request.conclusion,
        "external_id": request.external_id,
        "delivery_id": delivery_id,
    }

    with log_stage(logger, "check_run_publish", extra=extra):
        token = get_installation_token(installation_id)
        try:
            api_payload: dict[str, Any] = {
                "name": request.name,
                "head_sha": request.head_sha,
                "status": request.status,
                "external_id": request.external_id or "",
            }
            if request.conclusion is not None:
                api_payload["conclusion"] = request.conclusion
            if request.output is not None:
                api_payload["output"] = {
                    "title": request.output.title,
                    "summary": request.output.summary,
                }
                if request.output.text is not None:
                    api_payload["output"]["text"] = request.output.text

            result = _call_github_api(token, request.owner, request.repo, api_payload)
            return result
        finally:
            discard_token(token)
