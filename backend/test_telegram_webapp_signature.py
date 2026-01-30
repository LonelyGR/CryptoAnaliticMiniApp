"""
Unit-style test (no pytest dependency) for Telegram WebApp initData signature verification.

Run:
  python test_telegram_webapp_signature.py

This test generates a signed initData using TELEGRAM_BOT_TOKEN and validates it using
app.utils.telegram_webapp.verify_telegram_webapp_init_data.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse

from app.utils.telegram_webapp import verify_telegram_webapp_init_data


def _build_data_check_string(data: dict[str, str]) -> str:
    items = []
    for k, v in data.items():
        if k == "hash":
            continue
        items.append(f"{k}={v}")
    items.sort()
    return "\n".join(items)


def sign_webapp_init_data(fields: dict[str, str], bot_token: str) -> str:
    """
    Telegram WebApp:
      secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
      hash = HMAC_SHA256(key=secret_key, msg=data_check_string)
    """
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    dcs = _build_data_check_string(fields).encode("utf-8")
    signature = hmac.new(secret_key, dcs, hashlib.sha256).hexdigest()
    payload = dict(fields)
    payload["hash"] = signature
    return urllib.parse.urlencode(payload, quote_via=urllib.parse.quote, safe="")


def main() -> None:
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set in environment")

    user = {"id": 6989481318, "first_name": "Test", "username": "test_user"}
    now = int(time.time())

    fields = {
        "query_id": "AAH_test_query_id",
        "user": json.dumps(user, separators=(",", ":"), ensure_ascii=False),
        "auth_date": str(now),
    }

    # initData can include "signature" param in modern Telegram Mini Apps.
    # It MUST be included into data_check_string for bot-token validation.
    fields_with_signature = dict(fields)
    fields_with_signature["signature"] = "dummy_signature_value"

    init_data = sign_webapp_init_data(fields, token)
    parsed_user = verify_telegram_webapp_init_data(init_data, token)
    assert int(parsed_user["id"]) == int(user["id"])

    init_data2 = sign_webapp_init_data(fields_with_signature, token)
    parsed_user2 = verify_telegram_webapp_init_data(init_data2, token)
    assert int(parsed_user2["id"]) == int(user["id"])

    # Tamper => must fail
    bad = init_data.replace("Test", "Toast")
    try:
        verify_telegram_webapp_init_data(bad, token)
        raise AssertionError("tampered initData should not verify")
    except Exception:
        pass

    print("OK: verify_telegram_webapp_init_data works with generated initData")
    print("initData length:", len(init_data), "initData(with signature) length:", len(init_data2))


if __name__ == "__main__":
    main()

"""
Unit-style test (no pytest dependency) for Telegram WebApp initData signature verification.

Run:
  python test_telegram_webapp_signature.py

This file:
- generates a signed initData using TELEGRAM_BOT_TOKEN
- validates it via app.utils.telegram_webapp.verify_telegram_webapp_init_data
- prints a ready-to-use curl command for /api/product-payments/create (server-side)
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse

from app.utils.telegram_webapp import verify_telegram_webapp_init_data


def _build_data_check_string(data: dict[str, str]) -> str:
    items = []
    for k, v in data.items():
        if k == "hash":
            continue
        items.append(f"{k}={v}")
    items.sort()
    return "\n".join(items)


def sign_init_data(fields: dict[str, str], bot_token: str) -> str:
    import hashlib
    import hmac

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    dcs = _build_data_check_string(fields).encode("utf-8")
    signature = hmac.new(secret_key, dcs, hashlib.sha256).hexdigest()
    payload = dict(fields)
    payload["hash"] = signature
    # Telegram sends initData as querystring (urlencoded). Use quote (not plus) to avoid ambiguity.
    return urllib.parse.urlencode(payload, quote_via=urllib.parse.quote, safe="")


def main() -> None:
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set in environment")

    user = {"id": 6989481318, "first_name": "Test", "username": "test_user"}
    now = int(time.time())

    fields = {
        "query_id": "AAH_test_query_id",
        "user": json.dumps(user, separators=(",", ":"), ensure_ascii=False),
        "auth_date": str(now),
    }

    init_data = sign_init_data(fields, token)
    parsed_user = verify_telegram_webapp_init_data(init_data, token)
    assert int(parsed_user["id"]) == int(user["id"])

    # Tamper => must fail
    bad = init_data.replace("Test", "Toast")
    try:
        verify_telegram_webapp_init_data(bad, token)
        raise AssertionError("tampered initData should not verify")
    except Exception:
        pass

    print("OK: verify_telegram_webapp_init_data works with generated initData")
    print("\nExample curl (requires INTERNAL_API_KEY for server-side bypass):")
    print(
        "curl -sk \"https://cryptosensei.info/api/product-payments/create?admin_telegram_id=6989481318\" "
        "-H \"Content-Type: application/json\" "
        "-H \"X-Telegram-Init-Data: " + init_data + "\" "
        "-d '{\"amount\":590,\"price_currency\":\"usd\",\"pay_currency\":\"usdttrc20\",\"order_description\":\"Test product 590\"}'"
    )


if __name__ == "__main__":
    main()

