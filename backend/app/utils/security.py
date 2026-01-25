from __future__ import annotations

import hashlib
import hmac
import json


def build_nowpayments_signature(payload: dict, secret: str) -> str:
    sorted_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hmac.new(
        secret.encode(),
        sorted_json.encode(),
        hashlib.sha512
    ).hexdigest()


def verify_nowpayments_signature(payload: dict, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = build_nowpayments_signature(payload, secret)
    return hmac.compare_digest(expected, signature)
