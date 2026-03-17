from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from trustagents.oracle.models import OracleRequest


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def intake_and_fingerprint(request: OracleRequest) -> tuple[dict[str, Any], str]:
    if request.claim_package is not None:
        payload = canonical_json(request.claim_package)
        return request.claim_package, hashlib.sha256(payload).hexdigest()

    assert request.artifact is not None
    if request.artifact.payload_base64:
        payload = base64.b64decode(request.artifact.payload_base64)
        extracted: dict[str, Any] = {
            "artifactText": payload.decode("utf-8", errors="ignore"),
            "contentType": request.artifact.content_type,
        }
    else:
        text = request.artifact.payload_text or ""
        payload = text.encode("utf-8")
        extracted = {"artifactText": text, "contentType": request.artifact.content_type}

    return extracted, hashlib.sha256(payload).hexdigest()
