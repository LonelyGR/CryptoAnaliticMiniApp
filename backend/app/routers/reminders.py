from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.webinar import Webinar
from app.models.user import User
from app.models.admin import Admin
from app.utils.telegram import send_telegram_message

router = APIRouter(prefix="/reminders", tags=["reminders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_admin_access(admin_telegram_id: int = Query(..., description="Telegram ID администратора"), db: Session = Depends(get_db)):
    """Проверка прав администратора"""
    admin = db.query(Admin).filter(Admin.telegram_id == admin_telegram_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора")
    return admin


@router.post("/check-and-send")
def check_and_send_reminders(
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Проверить и отправить напоминания о вебинарах (только для администраторов)
    
    Этот endpoint должен вызываться периодически (например, каждые 5 минут) через cron job или планировщик задач.
    Он проверяет все предстоящие вебинары и отправляет напоминания за 12 часов, 2 часа и 15 минут (только оплатившим).
    """
    check_admin_access(admin_telegram_id, db)
    
    now = datetime.now()
    reminders_sent = {
        "12h": 0,
        "2h": 0,
        "15m": 0
    }
    
    # Получаем все предстоящие вебинары
    upcoming_webinars = db.query(Webinar).filter(
        Webinar.status == "upcoming"
    ).all()
    
    for webinar in upcoming_webinars:
        try:
            # Парсим дату и время вебинара
            webinar_datetime = datetime.strptime(
                f"{webinar.date} {webinar.time}",
                "%Y-%m-%d %H:%M"
            )
            
            # Получаем все подтвержденные записи на этот вебинар
            bookings = db.query(Booking).filter(
                Booking.webinar_id == webinar.id,
                Booking.status.in_(["confirmed", "paid"]),
                Booking.payment_status == "paid"  # только оплатившие
            ).all()
            
            time_until = webinar_datetime - now
            
            for booking in bookings:
                user = db.query(User).filter(User.id == booking.user_id).first()
                if not user or not user.telegram_id or user.is_blocked:
                    continue
                
                # Напоминание за 12 часов (флаг reminder_sent_24h используется как "12h")
                if timedelta(hours=11, minutes=50) <= time_until <= timedelta(hours=12, minutes=10):
                    if booking.reminder_sent_24h == 0:
                        msg = (
                            "⏰ <b>Напоминание о вебинаре</b>\n\n"
                            f"Через <b>12 часов</b> начнётся вебинар:\n"
                            f"📌 <b>{webinar.title}</b>\n"
                            f"🗓 <b>{webinar.date}</b> ⏰ <b>{webinar.time}</b>\n\n"
                            "Откройте мини‑приложение, чтобы посмотреть детали."
                        )
                        send_telegram_message(user.telegram_id, msg)
                        booking.reminder_sent_24h = 1
                        reminders_sent["12h"] += 1
                
                # Напоминание за 2 часа (флаг reminder_sent_1h используется как "2h")
                elif timedelta(hours=1, minutes=50) <= time_until <= timedelta(hours=2, minutes=10):
                    if booking.reminder_sent_1h == 0:
                        msg = (
                            "⏰ <b>Напоминание о вебинаре</b>\n\n"
                            f"Через <b>2 часа</b> начнётся вебинар:\n"
                            f"📌 <b>{webinar.title}</b>\n"
                            f"🗓 <b>{webinar.date}</b> ⏰ <b>{webinar.time}</b>\n\n"
                            "Откройте мини‑приложение заранее, чтобы быть готовым."
                        )
                        send_telegram_message(user.telegram_id, msg)
                        booking.reminder_sent_1h = 1
                        reminders_sent["2h"] += 1
                
                # Напоминание за 15 минут (флаг reminder_sent_10m используется как "15m")
                elif timedelta(minutes=10) <= time_until <= timedelta(minutes=20):
                    if booking.reminder_sent_10m == 0:
                        msg = (
                            "🚀 <b>Вебинар скоро начнётся</b>\n\n"
                            f"Через <b>15 минут</b> старт:\n"
                            f"📌 <b>{webinar.title}</b>\n"
                            f"🗓 <b>{webinar.date}</b> ⏰ <b>{webinar.time}</b>\n\n"
                            "Откройте мини‑приложение: кнопка <b>«Подключиться»</b> уже доступна."
                        )
                        send_telegram_message(user.telegram_id, msg)
                        booking.reminder_sent_10m = 1
                        reminders_sent["15m"] += 1
            
            db.commit()
        except Exception as e:
            print(f"Error processing webinar {webinar.id}: {e}")
            continue
    
    return {
        "message": "Reminders checked and sent",
        "reminders_sent": reminders_sent,
        "timestamp": now.isoformat()
    }


@router.get("/upcoming")
def get_upcoming_reminders(
    admin_telegram_id: int = Query(..., description="Telegram ID администратора"),
    db: Session = Depends(get_db)
):
    """Получить список предстоящих вебинаров, которым нужны напоминания (только для администраторов)"""
    check_admin_access(admin_telegram_id, db)
    
    now = datetime.now()
    upcoming = []
    
    webinars = db.query(Webinar).filter(
        Webinar.status == "upcoming"
    ).all()
    
    for webinar in webinars:
        try:
            webinar_datetime = datetime.strptime(
                f"{webinar.date} {webinar.time}",
                "%Y-%m-%d %H:%M"
            )
            
            if webinar_datetime > now:
                bookings = db.query(Booking).filter(
                    Booking.webinar_id == webinar.id,
                    Booking.status.in_(["confirmed", "paid"])
                ).count()
                
                upcoming.append({
                    "webinar_id": webinar.id,
                    "title": webinar.title,
                    "datetime": webinar_datetime.isoformat(),
                    "time_until": str(webinar_datetime - now),
                    "bookings_count": bookings
                })
        except:
            continue
    
    return {"upcoming_webinars": upcoming}
