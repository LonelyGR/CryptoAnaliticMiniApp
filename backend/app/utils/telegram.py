import os
import requests


def send_telegram_message(telegram_id: int, text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not telegram_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.ok
    except requests.RequestException:
        return False
