from __future__ import annotations

from typing import Any


def extract_claims(payload: dict[str, Any]) -> dict[str, Any]:
    claims = payload.get("claims", payload)
    metadata = payload.get("metadata", {})
    return {"claims": claims, "metadata": metadata}
