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


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # Single domain for Telegram Mini App
    domain = (os.getenv("DOMAIN") or "").strip()
    if not domain:
        raise RuntimeError("DOMAIN is not set")
    webapp_url = f"https://{domain}"

    offset = int(os.getenv("BOT_UPDATE_OFFSET") or "0")
    timeout = int(os.getenv("BOT_LONGPOLL_TIMEOUT") or "30")
    sleep_s = float(os.getenv("BOT_POLL_SLEEP") or "0.5")

    print("[bot] started, webapp_url=", webapp_url)

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

                if text.startswith("/start"):
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
                        webapp_url=webapp_url,
                    )
        except Exception as e:
            print("[bot] error:", e)

        time.sleep(sleep_s)


if __name__ == "__main__":
    main()

