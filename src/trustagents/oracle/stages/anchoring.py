from __future__ import annotations

import hashlib

from trustagents.oracle.models import AnchorRecord, SignedReceipt


def anchor_receipt(receipt: SignedReceipt) -> AnchorRecord:
    anchor_id = hashlib.sha256(f"anchor|{receipt.receipt_id}|{receipt.signature}".encode("utf-8")).hexdigest()[:20]
    return AnchorRecord(anchor_id=anchor_id, status="ANCHORED")
