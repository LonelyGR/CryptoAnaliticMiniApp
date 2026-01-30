from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Optional


def _hmac_hex(algorithm: str, *, secret: str, message: bytes) -> str:
    algo = (algorithm or "").lower().strip()
    if algo in {"sha512", "hmac-sha512", "hmac_sha512"}:
        digestmod = hashlib.sha512
    elif algo in {"sha256", "hmac-sha256", "hmac_sha256"}:
        digestmod = hashlib.sha256
    else:
        # Default for NOWPayments IPN (per docs) is SHA-512
        digestmod = hashlib.sha512
    return hmac.new(secret.encode("utf-8"), message, digestmod).hexdigest()


def build_nowpayments_signature_from_raw(raw_body: bytes, secret: str, *, algorithm: str = "sha512") -> str:
    """
    Preferred: sign EXACT raw request body bytes (no JSON re-encoding).
    """
    return _hmac_hex(algorithm, secret=secret, message=raw_body or b"")


def build_nowpayments_signature_from_payload(payload: dict[str, Any], secret: str, *, algorithm: str = "sha512") -> str:
    """
    Compatibility: some implementations/documentation canonicalize JSON (sorted keys) before signing.
    """
    canonical = json.dumps(payload or {}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _hmac_hex(algorithm, secret=secret, message=canonical)


def verify_nowpayments_signature(
    *,
    raw_body: bytes,
    signature: str,
    secret: str,
    payload: Optional[dict[str, Any]] = None,
    algorithm: str = "sha512",
) -> tuple[bool, dict[str, str]]:
    """
    Verify NOWPayments IPN signature.

    Returns: (ok, debug_info)
    debug_info contains safe metadata (digests prefixes etc.), not the secret/payload.
    """
    sig = (signature or "").strip().lower()
    sec = (secret or "").strip()
    if not sec:
        return False, {"reason": "empty_secret"}
    if not sig:
        return False, {"reason": "missing_signature_header"}

    computed_raw = build_nowpayments_signature_from_raw(raw_body or b"", sec, algorithm=algorithm).lower()
    ok_raw = hmac.compare_digest(computed_raw, sig)

    ok_canon = False
    computed_canon = ""
    if payload is not None:
        computed_canon = build_nowpayments_signature_from_payload(payload, sec, algorithm=algorithm).lower()
        ok_canon = hmac.compare_digest(computed_canon, sig)

    ok = bool(ok_raw or ok_canon)
    return ok, {
        "reason": "ok" if ok else "mismatch",
        "algo": (algorithm or "sha512").lower(),
        "raw_len": str(len(raw_body or b"")),
        "secret_len": str(len(sec)),
        "received_prefix": sig[:10],
        "computed_raw_prefix": computed_raw[:10],
        "computed_canon_prefix": computed_canon[:10] if computed_canon else "",
        "matched_mode": "raw" if ok_raw else ("canonical" if ok_canon else ""),
    }
