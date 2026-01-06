import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8246818201:AAEnfD4po58nQg4sEzzv4W7q4vQVRYWLsP8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! {username}, \n Следи за рынком, и получай возможность записатьcя на вебинар или получить консультацию от проффисионалов!".format(username=message.from_user.full_name)
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())