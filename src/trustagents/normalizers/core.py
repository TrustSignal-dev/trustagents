from __future__ import annotations

import re
from datetime import datetime
from typing import Any


def normalize_name(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(value.lower().split())


def normalize_id(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"[^a-zA-Z0-9]", "", value).lower()


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def normalize_claims(claims: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(claims)
    if "fullName" in claims:
        normalized["fullNameNormalized"] = normalize_name(claims.get("fullName"))
    if "dateOfBirth" in claims:
        normalized["dateOfBirthNormalized"] = normalize_date(claims.get("dateOfBirth"))
    if "identifier" in claims:
        normalized["identifierNormalized"] = normalize_id(claims.get("identifier"))
    return normalized
