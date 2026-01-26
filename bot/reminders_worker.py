import os
import time
import requests


def main():
    backend_url = (os.getenv("BACKEND_URL") or "http://backend:8000").rstrip("/")
    admin_telegram_id = os.getenv("ADMIN_TELEGRAM_ID")
    interval_seconds = int(os.getenv("REMINDER_INTERVAL_SECONDS") or "300")

    if not admin_telegram_id:
        raise RuntimeError("ADMIN_TELEGRAM_ID is not set")

    while True:
        try:
            url = f"{backend_url}/reminders/check-and-send"
            r = requests.post(url, params={"admin_telegram_id": admin_telegram_id}, timeout=20)
            print("[reminders-worker]", r.status_code, r.text[:500])
        except Exception as e:
            print("[reminders-worker] error:", e)

        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()

