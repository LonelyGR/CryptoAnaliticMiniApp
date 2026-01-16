import asyncio
import os
from typing import Optional
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN", "8246818201:AAEnfD4po58nQg4sEzzv4W7q4vQVRYWLsP8")
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def extract_referral_code(text: str) -> Optional[str]:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1]
    if payload.startswith("ref_"):
        return payload.replace("ref_", "", 1)
    return None


async def track_referral(code: str, message: types.Message) -> None:
    payload = {
        "referral_code": code,
        "referred_telegram_id": message.from_user.id,
        "referred_username": message.from_user.username,
        "referred_first_name": message.from_user.first_name,
        "referred_last_name": message.from_user.last_name,
    }
    try:
        await asyncio.to_thread(
            requests.post,
            f"{API_BASE_URL}/referrals/track",
            json=payload,
            timeout=10,
        )
    except Exception as exc:
        print(f"Referral track failed: {exc}")


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    referral_code = extract_referral_code(message.text)
    if referral_code:
        await track_referral(referral_code, message)

    await message.answer(
        "Привет, {username}!\n"
        "Следи за рынком, записывайся на вебинары и получай консультации от профессионалов 🚀".format(
            username=message.from_user.full_name
        )
    )


@dp.message()
async def handle_any_message(message: types.Message):
    try:
        await message.answer(
            "Я на связи! Открой мини‑приложение, чтобы продолжить работу 🚀"
        )
    except Exception as exc:
        print(f"Message handler failed: {exc}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())