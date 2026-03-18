"""GitHub App webhook HMAC verification and ingress hardening.

Security properties
-------------------
1. Signature is verified *before* any business logic runs (fail-closed).
2. Comparison uses ``hmac.compare_digest`` for constant-time equality to
   prevent timing-oracle attacks.
3. Delivery-ID replay protection is applied after signature verification.
4. Payload schema is validated with Pydantic before dispatch.
5. All failures produce structured log events and explicit HTTP error codes.

Secret configuration
--------------------
The webhook secret is read from the ``GITHUB_WEBHOOK_SECRET`` environment
variable.  If the variable is absent the route returns 500 (not 200) so that
misconfigured deployments fail loudly rather than accepting unsigned payloads.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

from fastapi import Header, HTTPException, Request
from pydantic import ValidationError

from trustagents.github_app.models import WebhookPayload
from trustagents.github_app.replay_store import ReplayStore, replay_store as _default_replay_store
from trustagents.observability import get_logger

logger = get_logger("github_app.webhook")

_SIGNATURE_HEADER = "x-hub-signature-256"
_DELIVERY_HEADER = "x-github-delivery"
_EVENT_HEADER = "x-github-event"

# Maximum accepted raw body size (10 KB). Adjust if legitimate payloads exceed this.
_MAX_BODY_BYTES = 10 * 1024


class WebhookVerificationError(Exception):
    """Raised when a webhook request fails any security check."""

    def __init__(self, reason: str, status_code: int = 401) -> None:
        super().__init__(reason)
        self.status_code = status_code


def _get_webhook_secret() -> bytes:
    """Read the webhook secret from the environment. Raise 500 if not configured."""
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if not secret:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "WEBHOOK_SECRET_NOT_CONFIGURED",
                "message": "Webhook secret is not configured",
                "retryable": False,
            },
        )
    return secret.encode()


def _verify_hmac(body: bytes, signature_header: str | None, secret: bytes) -> None:
    """Verify the SHA-256 HMAC signature.

    Raises WebhookVerificationError on any failure so callers can convert to
    the appropriate HTTP response without leaking internal details.
    """
    if not signature_header:
        raise WebhookVerificationError("Missing x-hub-signature-256 header")

    if not signature_header.startswith("sha256="):
        raise WebhookVerificationError("Signature header has unexpected format")

    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    provided = signature_header.removeprefix("sha256=")

    if not hmac.compare_digest(expected, provided):
        raise WebhookVerificationError("Signature mismatch")


def _check_replay(delivery_id: str | None, store: ReplayStore) -> None:
    """Reject requests whose delivery ID has already been processed."""
    if not delivery_id:
        raise WebhookVerificationError("Missing x-github-delivery header", status_code=400)
    if store.is_seen(delivery_id):
        raise WebhookVerificationError(
            f"Replayed delivery: {delivery_id}", status_code=409
        )


def _parse_payload(body: bytes) -> tuple[dict[str, Any], WebhookPayload]:
    """Decode and validate the webhook payload JSON."""
    try:
        raw = json.loads(body)
    except json.JSONDecodeError as exc:
        raise WebhookVerificationError(
            f"Invalid JSON body: {exc}", status_code=400
        ) from exc

    try:
        payload = WebhookPayload.model_validate(raw)
    except ValidationError as exc:
        raise WebhookVerificationError(
            f"Payload schema validation failed: {exc}", status_code=422
        ) from exc

    return raw, payload


async def verify_webhook_request(
    request: Request,
    *,
    store: ReplayStore | None = None,
) -> tuple[str, str, WebhookPayload, dict[str, Any]]:
    """Full webhook ingress verification pipeline.

    Returns:
        (event_type, delivery_id, validated_payload, raw_dict)

    Raises:
        HTTPException on any security or validation failure.
    """
    effective_store = store if store is not None else _default_replay_store

    # 1. Read and enforce body size limit
    body = await request.body()
    if len(body) > _MAX_BODY_BYTES:
        logger.warning(
            "webhook_body_too_large",
            extra={"size_bytes": len(body), "limit_bytes": _MAX_BODY_BYTES},
        )
        raise HTTPException(
            status_code=413,
            detail={"code": "PAYLOAD_TOO_LARGE", "message": "Request body exceeds size limit", "retryable": False},
        )

    # 2. Signature verification — must happen before any other processing
    secret = _get_webhook_secret()
    signature = request.headers.get(_SIGNATURE_HEADER)
    delivery_id = request.headers.get(_DELIVERY_HEADER)
    event_type = request.headers.get(_EVENT_HEADER, "unknown")

    try:
        _verify_hmac(body, signature, secret)
    except WebhookVerificationError as exc:
        logger.warning(
            "webhook_signature_rejected",
            extra={"delivery_id": delivery_id, "event": event_type, "reason": str(exc)},
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": "SIGNATURE_INVALID", "message": str(exc), "retryable": False},
        ) from exc

    # 3. Replay protection — _check_replay raises if delivery_id is None or already seen
    try:
        _check_replay(delivery_id, effective_store)
    except WebhookVerificationError as exc:
        logger.warning(
            "webhook_replay_rejected",
            extra={"delivery_id": delivery_id, "event": event_type, "reason": str(exc)},
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": "DELIVERY_REPLAYED", "message": str(exc), "retryable": False},
        ) from exc

    # delivery_id is guaranteed non-None at this point: _check_replay raises on None.
    assert delivery_id is not None

    # 4. Schema validation
    try:
        raw, payload = _parse_payload(body)
    except WebhookVerificationError as exc:
        logger.warning(
            "webhook_payload_invalid",
            extra={"delivery_id": delivery_id, "event": event_type, "reason": str(exc)},
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": "PAYLOAD_INVALID", "message": str(exc), "retryable": False},
        ) from exc

    # 5. Mark delivery as seen only after all checks pass
    effective_store.mark_seen(delivery_id)

    logger.info(
        "webhook_accepted",
        extra={
            "delivery_id": delivery_id,
            "event": event_type,
            "action": payload.action,
            "installation_id": payload.installation.id if payload.installation else None,
        },
    )

    return event_type, delivery_id, payload, raw
