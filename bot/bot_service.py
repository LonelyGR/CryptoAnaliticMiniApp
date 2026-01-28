import os
import time
import requests


def _api(token: str) -> str:
    return f"https://api.telegram.org/bot{token}"


def send_message(token: str, chat_id: int, text: str, webapp_url: str | None = None):
    payload: dict = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if webapp_url:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "Open Mini App", "web_app": {"url": webapp_url}}]]
        }

    requests.post(f"{_api(token)}/sendMessage", json=payload, timeout=20).raise_for_status()


def _track_referral(
    backend_url: str,
    *,
    referral_code: str,
    referred_telegram_id: int,
    referred_username: str | None,
    referred_first_name: str | None,
    referred_last_name: str | None,
):
    """
    Calls backend /referrals/track to store invite.
    Safe to call multiple times (backend deduplicates by referred_telegram_id + referrer).
    """
    backend_url = (backend_url or "").rstrip("/")
    if not backend_url:
        return

    try:
        requests.post(
            f"{backend_url}/referrals/track",
            json={
                "referral_code": referral_code,
                "referred_telegram_id": referred_telegram_id,
                "referred_username": referred_username,
                "referred_first_name": referred_first_name,
                "referred_last_name": referred_last_name,
            },
            timeout=10,
        ).raise_for_status()
        print(f"[bot] referral tracked: code={referral_code} referred={referred_telegram_id}")
    except Exception as e:
        # don't break bot flow if backend is temporarily unavailable
        print("[bot] referral track failed:", e)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # Single domain for Telegram Mini App
    domain = (os.getenv("DOMAIN") or "").strip()
    if not domain:
        raise RuntimeError("DOMAIN is not set")
    base_webapp_url = f"https://{domain}"

    # Backend base URL for internal container network
    backend_url = (os.getenv("BACKEND_URL") or "http://backend:8000").rstrip("/")

    offset = int(os.getenv("BOT_UPDATE_OFFSET") or "0")
    timeout = int(os.getenv("BOT_LONGPOLL_TIMEOUT") or "30")
    sleep_s = float(os.getenv("BOT_POLL_SLEEP") or "0.5")

    print("[bot] started, webapp_url=", base_webapp_url, "backend_url=", backend_url)

    while True:
        try:
            r = requests.get(
                f"{_api(token)}/getUpdates",
                params={"timeout": timeout, "offset": offset, "allowed_updates": ["message"]},
                timeout=timeout + 10,
            )
            r.raise_for_status()
            data = r.json()
            for upd in data.get("result", []):
                offset = max(offset, int(upd["update_id"]) + 1)
                msg = upd.get("message") or {}
                text = (msg.get("text") or "").strip()
                chat = msg.get("chat") or {}
                chat_id = chat.get("id")
                if not chat_id:
                    continue
                sender = msg.get("from") or {}

                if text.startswith("/start"):
                    # Parse optional argument: "/start ref_<code>"
                    start_arg = ""
                    parts = text.split(maxsplit=1)
                    if len(parts) == 2:
                        start_arg = parts[1].strip()

                    webapp_url = base_webapp_url
                    if start_arg.startswith("ref_") and len(start_arg) > 4:
                        code = start_arg[4:].strip()
                        # pass ref code into webapp URL for client-side tracking
                        webapp_url = f"{base_webapp_url}/?ref={code}"
                        # server-side tracking (so invites appear even if user doesn't open the webapp)
                        _track_referral(
                            backend_url,
                            referral_code=code,
                            referred_telegram_id=int(chat_id),
                            referred_username=sender.get("username"),
                            referred_first_name=sender.get("first_name"),
                            referred_last_name=sender.get("last_name"),
                        )

                    send_message(
                        token,
                        chat_id,
                        "✅ <b>Mini App готов</b>\n\nНажми кнопку ниже, чтобы открыть.",
                        webapp_url=webapp_url,
                    )
                elif text.startswith("/help"):
                    send_message(
                        token,
                        chat_id,
                        "Команды:\n/start — открыть Mini App\n/help — помощь",
                        webapp_url=base_webapp_url,
                    )
        except Exception as e:
            print("[bot] error:", e)

        time.sleep(sleep_s)


if __name__ == "__main__":
    main()

