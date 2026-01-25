import os
import time
import requests
from typing import Iterable
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8246818201:AAEnfD4po58nQg4sEzzv4W7q4vQVRYWLsP8"  # ОБЯЗАТЕЛЬНО через env
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ================== TELEGRAM ==================

def send_message(chat_id: int, text: str) -> bool:
    """
    Отправка одного сообщения.
    Без async, без aiohttp, без aiogram.
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        r = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=5,
        )
        r.raise_for_status()
        return True

    except requests.exceptions.HTTPError as e:
        # 403 — пользователь заблокировал бота
        if r.status_code == 403:
            print(f"[TG] User {chat_id} blocked bot")
            return False
        print("[TG] HTTP error:", e)

    except Exception as e:
        print("[TG] Network error:", e)

    return False


def broadcast(chat_ids: Iterable[int], text: str):
    """
    Массовая рассылка с защитой от rate limit.
    """
    for chat_id in chat_ids:
        send_message(chat_id, text)
        time.sleep(0.05)  # ~20 msg/sec — безопасно


# ================== ПЛАНИРОВЩИК ==================

scheduler = BackgroundScheduler()
scheduler.start()


def schedule_webinar_reminder(
    chat_ids: Iterable[int],
    title: str,
    start_time: datetime,
    minutes_before: int = 15,
):
    """
    Напоминание о вебинаре
    """
    run_at = start_time - timedelta(minutes=minutes_before)

    def job():
        broadcast(
            chat_ids,
            f"⏰ <b>Через {minutes_before} минут вебинар</b>\n\n"
            f"📌 {title}"
        )

    scheduler.add_job(job, "date", run_date=run_at)
    print(f"[Scheduler] Reminder set at {run_at}")


# ================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ==================

if __name__ == "__main__":
    # ❗ Эти chat_id ты хранишь в БД
    USERS = [
        123456789,
        987654321,
    ]

    # 1️⃣ Уведомление о новом вебинаре
    broadcast(
        USERS,
        "🚀 <b>Новый вебинар уже доступен!</b>\n\n"
        "Зайди в Mini App, чтобы узнать подробности."
    )

    # 2️⃣ Напоминание за 15 минут
    webinar_start = datetime.now() + timedelta(minutes=20)

    schedule_webinar_reminder(
        chat_ids=USERS,
        title="Как торговать по логике маркет-мейкеров",
        start_time=webinar_start,
        minutes_before=15,
    )

    print("Notifier is running...")
    while True:
        time.sleep(60)
