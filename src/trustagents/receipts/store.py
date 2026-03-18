from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from trustagents.oracle.models import SignedReceipt


class ReceiptState(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class ReceiptRecord:
    receipt: SignedReceipt
    tenant_id: str
    decision: str
    state: ReceiptState = ReceiptState.ACTIVE
    revoked_at: datetime | None = None
    revocation_reason: str | None = None


@dataclass
class ReceiptStore:
    """In-memory receipt lifecycle store.

    Stores issued receipts and supports verification, revocation, and lookup.
    """

    _records: dict[str, ReceiptRecord] = field(default_factory=dict)

    def store(self, receipt: SignedReceipt, tenant_id: str, decision: str) -> ReceiptRecord:
        record = ReceiptRecord(receipt=receipt, tenant_id=tenant_id, decision=decision)
        self._records[receipt.receipt_id] = record
        return record

    def get(self, receipt_id: str) -> ReceiptRecord | None:
        return self._records.get(receipt_id)

    def verify(self, receipt_id: str, fingerprint: str, signature: str) -> dict:
        """Verify a receipt by checking its existence, state, and signature."""
        record = self._records.get(receipt_id)
        if record is None:
            return {"valid": False, "reason": "Receipt not found", "state": None}
        if record.state == ReceiptState.REVOKED:
            return {
                "valid": False,
                "reason": "Receipt has been revoked",
                "state": ReceiptState.REVOKED.value,
                "revoked_at": record.revoked_at.isoformat() if record.revoked_at else None,
            }
        if record.receipt.fingerprint != fingerprint:
            return {"valid": False, "reason": "Fingerprint mismatch", "state": record.state.value}
        if record.receipt.signature != signature:
            return {"valid": False, "reason": "Signature mismatch", "state": record.state.value}
        return {"valid": True, "reason": "Receipt is valid and active", "state": ReceiptState.ACTIVE.value}

    def revoke(self, receipt_id: str, reason: str) -> ReceiptRecord | None:
        """Revoke an active receipt. Returns None if receipt not found."""
        record = self._records.get(receipt_id)
        if record is None:
            return None
        record.state = ReceiptState.REVOKED
        record.revoked_at = datetime.now(UTC)
        record.revocation_reason = reason
        return record


receipt_store = ReceiptStore()
