from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse

from fastapi import HTTPException, Request


def _debug_enabled() -> bool:
    return os.getenv("DEBUG_TELEGRAM_AUTH") == "1"


def _safe_prefix(value: str, n: int = 80) -> str:
    value = value or ""
    if len(value) <= n:
        return value
    return value[:n] + "…"


def _parse_init_data(init_data: str) -> dict[str, str]:
    # initData приходит как querystring (urlencoded), напр: "query_id=...&user=...&auth_date=...&hash=..."
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=False, keep_blank_values=True)
    # берём первые значения
    return {k: (v[0] if isinstance(v, list) and v else "") for k, v in parsed.items()}


def _build_data_check_string(data: dict[str, str]) -> str:
    # Telegram: сортируем "key=value" (без hash) по key, соединяем \n
    items = []
    for key, value in data.items():
        if key == "hash":
            continue
        items.append(f"{key}={value}")
    items.sort()
    return "\n".join(items)


def verify_telegram_webapp_init_data(init_data: str, bot_token: str) -> dict:
    """
    Verifies Telegram WebApp initData signature.
    Returns parsed 'user' dict on success.
    Raises HTTPException on failure.
    """
    init_data = (init_data or "").strip()
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram initData")

    bot_token = (bot_token or "").strip()
    if not bot_token:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN is not configured")

    data = _parse_init_data(init_data)
    received_hash = (data.get("hash") or "").strip()
    if not received_hash:
        if _debug_enabled():
            keys = sorted(list(data.keys()))
            raise HTTPException(
                status_code=401,
                detail=f"Missing Telegram initData hash (keys={keys})",
            )
        raise HTTPException(status_code=401, detail="Missing Telegram initData hash")

    # Telegram WebApp signing (current):
    # secret_key = HMAC_SHA256(key=bot_token, msg="WebAppData")
    # hash = HMAC_SHA256(key=secret_key, msg=data_check_string)
    data_check_string_raw = _build_data_check_string(data)
    data_check_string = data_check_string_raw.encode("utf-8")

    secret_key = hmac.new(bot_token.encode("utf-8"), b"WebAppData", hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()

    # Backward compatibility (legacy implementations used sha256(bot_token) as secret_key)
    legacy_secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    legacy_hash = hmac.new(legacy_secret_key, data_check_string, hashlib.sha256).hexdigest()

    if not (hmac.compare_digest(calculated_hash, received_hash) or hmac.compare_digest(legacy_hash, received_hash)):
        if _debug_enabled():
            # DO NOT log full initData. Only a safe prefix & metadata.
            keys = sorted([k for k in data.keys()])
            user_raw = data.get("user") or ""
            user_id = None
            try:
                user_obj = json.loads(user_raw) if user_raw else None
                if isinstance(user_obj, dict):
                    user_id = user_obj.get("id")
            except Exception:
                user_id = None

            raise HTTPException(
                status_code=401,
                detail=(
                    "Invalid Telegram initData signature "
                    f"(init_len={len(init_data)} init_prefix={_safe_prefix(init_data)!r} "
                    f"keys={keys} has_hash={'hash' in data} "
                    f"user_id={user_id} "
                    f"received_hash={received_hash[:10]} computed_hash={calculated_hash[:10]} legacy_hash={legacy_hash[:10]} "
                    f"bot_token_sha256={hashlib.sha256(bot_token.encode('utf-8')).hexdigest()[:12]})"
                ),
            )
        raise HTTPException(status_code=401, detail="Invalid Telegram initData signature")

    # optional TTL check
    max_age = int(os.getenv("TELEGRAM_AUTH_MAX_AGE_SECONDS", "86400"))
    auth_date_raw = (data.get("auth_date") or "").strip()
    if auth_date_raw.isdigit():
        auth_date = int(auth_date_raw)
        if max_age > 0 and int(time.time()) - auth_date > max_age:
            raise HTTPException(status_code=401, detail="Telegram initData expired")

    user_raw = data.get("user") or ""
    if not user_raw:
        raise HTTPException(status_code=401, detail="Telegram initData has no user")
    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=401, detail="Invalid Telegram initData user") from exc
    if not isinstance(user, dict) or not user.get("id"):
        raise HTTPException(status_code=401, detail="Telegram initData user has no id")
    return user


def get_request_telegram_user_id(request: Request) -> int:
    init_data = (request.headers.get("X-Telegram-Init-Data") or "").strip()
    user = verify_telegram_webapp_init_data(init_data, os.getenv("TELEGRAM_BOT_TOKEN", ""))
    return int(user["id"])


def resolve_admin_telegram_id(
    request: Request,
    fallback_admin_telegram_id: int | None,
    *,
    allow_internal: bool = False,
) -> int:
    """
    Resolves requester Telegram ID:
    - If X-Telegram-Init-Data present and valid -> returns its user.id
    - Else if REQUIRE_TELEGRAM_AUTH=1 -> 401
    - Else fallback to query admin_telegram_id (legacy)
    """
    init_data = (request.headers.get("X-Telegram-Init-Data") or "").strip()
    if init_data:
        return get_request_telegram_user_id(request)

    if allow_internal:
        internal_key = (os.getenv("INTERNAL_API_KEY") or "").strip()
        provided = (request.headers.get("X-Internal-Key") or "").strip()
        if internal_key and provided and hmac.compare_digest(internal_key, provided):
            if fallback_admin_telegram_id is None:
                raise HTTPException(status_code=401, detail="Missing admin_telegram_id")
            return int(fallback_admin_telegram_id)

    if os.getenv("REQUIRE_TELEGRAM_AUTH") == "1":
        # Optional legacy fallback for admin panels outside Telegram.
        # Enable explicitly via env to avoid weakening security by default.
        if fallback_admin_telegram_id is not None and os.getenv("ALLOW_LEGACY_ADMIN_TELEGRAM_ID") == "1":
            return int(fallback_admin_telegram_id)
        raise HTTPException(status_code=401, detail="Telegram auth required")

    if fallback_admin_telegram_id is None:
        raise HTTPException(status_code=401, detail="Missing admin_telegram_id")
    return int(fallback_admin_telegram_id)
