import asyncio
import os
from typing import Optional
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramNetworkError, TelegramForbiddenError, TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN", "8246818201:AAEnfD4po58nQg4sEzzv4W7q4vQVRYWLsP8")
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
BOT_USERNAME = os.getenv("BOT_USERNAME", "crypto_sensebot").replace("@", "").strip()

ASSETS_PATH = Path(__file__).resolve().parent.parent / "miniapp" / "react-app" / "src" / "assets" / "logo.jpg"

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
    if payload.startswith("share_ref_"):
        return payload.replace("share_ref_", "", 1)
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


async def send_referral_card(message: types.Message, referral_code: str) -> None:
    if not BOT_USERNAME:
        await safe_answer(message, "Юзернейм бота не настроен. Обратись к администратору.")
        return

    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{referral_code}"
    caption = (
        "🚀 <b>Crypto Sensey — трейдинг по логике маркет‑мейкеров</b>\n\n"
        "Бот зарабатывает на пампах и дампах, не завися от направления рынка.\n"
        "Вебинары и персональные консультации включены.\n\n"
        "Нажми кнопку ниже 👇"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Войти в Crypto Sensey", url=referral_link)]
        ]
    )

    if ASSETS_PATH.exists():
        photo = FSInputFile(ASSETS_PATH)
        try:
            await message.answer_photo(photo=photo, caption=caption, reply_markup=keyboard, parse_mode="HTML")
            return
        except Exception as exc:
            print(f"Failed to send referral photo: {exc}")

    await safe_answer(message, f"{caption}\n\n{referral_link}")


async def safe_answer(message: types.Message, text: str) -> None:
    try:
        await message.answer(text)
    except TelegramForbiddenError:
        # User blocked the bot or can't be reached
        return
    except TelegramNetworkError as exc:
        print(f"Telegram network error: {exc}")
    except TelegramAPIError as exc:
        print(f"Telegram API error: {exc}")
    except Exception as exc:
        print(f"Unexpected bot error: {exc}")


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    referral_code = extract_referral_code(message.text)
    if referral_code and message.text and "share_ref_" in message.text:
        await send_referral_card(message, referral_code)
        return
    if referral_code:
        await track_referral(referral_code, message)

    await safe_answer(
        message,
        "Привет, {username}!\n"
        "Следи за рынком, записывайся на вебинары и получай консультации от профессионалов 🚀".format(
            username=message.from_user.full_name
        )
    )


@dp.message()
async def handle_any_message(message: types.Message):
    await safe_answer(
        message,
        "Я на связи! Открой мини‑приложение, чтобы продолжить работу 🚀"
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())