from collections.abc import MutableMapping

from fastapi import Header, HTTPException


async def tenant_guard(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing tenant header")
    return x_tenant_id


class IdempotencyStore:
    def __init__(self) -> None:
        self._records: MutableMapping[str, dict] = {}

    @staticmethod
    def _key(tenant_id: str, idempotency_key: str, fingerprint: str) -> str:
        return f"{tenant_id}:{idempotency_key}:{fingerprint}"

    def get(self, tenant_id: str, idempotency_key: str, fingerprint: str) -> dict | None:
        return self._records.get(self._key(tenant_id, idempotency_key, fingerprint))

    def set(self, tenant_id: str, idempotency_key: str, fingerprint: str, response: dict) -> None:
        self._records[self._key(tenant_id, idempotency_key, fingerprint)] = response


idempotency_store = IdempotencyStore()
