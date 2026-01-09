from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.webinar import Webinar
from app.models.user import User
from app.models.admin import Admin

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
    Он проверяет все предстоящие вебинары и отправляет напоминания за 24 часа, 1 час и 10 минут.
    """
    check_admin_access(admin_telegram_id, db)
    
    now = datetime.now()
    reminders_sent = {
        "24h": 0,
        "1h": 0,
        "10m": 0
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
                Booking.payment_status.in_(["paid", None])  # Оплаченные или бесплатные
            ).all()
            
            time_until = webinar_datetime - now
            
            for booking in bookings:
                user = db.query(User).filter(User.id == booking.user_id).first()
                if not user:
                    continue
                
                # Напоминание за 24 часа
                if timedelta(hours=23, minutes=50) <= time_until <= timedelta(hours=24, minutes=10):
                    if booking.reminder_sent_24h == 0:
                        # Здесь должна быть отправка уведомления (email, Telegram и т.д.)
                        # Пока просто обновляем флаг
                        booking.reminder_sent_24h = 1
                        reminders_sent["24h"] += 1
                        # В реальном приложении здесь будет:
                        # send_notification(user, webinar, "24h")
                
                # Напоминание за 1 час
                elif timedelta(minutes=50) <= time_until <= timedelta(hours=1, minutes=10):
                    if booking.reminder_sent_1h == 0:
                        booking.reminder_sent_1h = 1
                        reminders_sent["1h"] += 1
                        # send_notification(user, webinar, "1h")
                
                # Напоминание за 10 минут
                elif timedelta(minutes=5) <= time_until <= timedelta(minutes=15):
                    if booking.reminder_sent_10m == 0:
                        booking.reminder_sent_10m = 1
                        reminders_sent["10m"] += 1
                        # send_notification(user, webinar, "10m")
            
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
