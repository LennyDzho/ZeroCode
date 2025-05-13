from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

from genai.items import settings



bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message()
async def send_webapp_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть WebApp", web_app=WebAppInfo(url=settings.WEBAPP_URL))],
    ])
    await message.answer("Нажми кнопку ниже, чтобы открыть приложение", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
