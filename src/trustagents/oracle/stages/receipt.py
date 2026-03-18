from __future__ import annotations

import hashlib

from trustagents.oracle.models import SignedReceipt


def build_signed_receipt(fingerprint: str, decision: str, versions: dict[str, str]) -> SignedReceipt:
    material = f"{fingerprint}|{decision}|{versions['risk_model_version']}|{versions['policy_version']}"
    signature = hashlib.sha256(material.encode("utf-8")).hexdigest()
    receipt_id = hashlib.sha256(f"receipt|{material}".encode("utf-8")).hexdigest()[:16]
    return SignedReceipt(receipt_id=receipt_id, signature=signature, fingerprint=fingerprint)
