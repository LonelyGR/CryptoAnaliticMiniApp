from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Request

from app.utils.telegram_webapp import verify_telegram_webapp_init_data


router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/telegram")
async def debug_telegram(request: Request):
    """
    Debug endpoint for Telegram initData verification.
    Enabled ONLY when DEBUG_TELEGRAM_AUTH=1.
    Returns: {ok: bool, reason?: str, user_id?: int}
    """
    if os.getenv("DEBUG_TELEGRAM_AUTH") != "1":
        raise HTTPException(status_code=404, detail="Not found")

    init_data = (request.headers.get("X-Telegram-Init-Data") or "").strip()
    try:
        user = verify_telegram_webapp_init_data(init_data, os.getenv("TELEGRAM_BOT_TOKEN", ""))
        return {"ok": True, "user_id": int(user["id"])}
    except HTTPException as exc:
        # Return safe reason; verify_telegram_webapp_init_data already censors initData.
        return {"ok": False, "reason": str(exc.detail)}

