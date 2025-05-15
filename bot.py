import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

from dotenv import load_dotenv

from genai.items import settings
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message()
async def send_webapp_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть WebApp", web_app=WebAppInfo(url=WEBAPP_URL))],
    ])
    await message.answer("<b>Нажми кнопку ниже, чтобы открыть приложение</b>\n\n"
                         "<b><i>Домен может обновляться, поэтому перед запуском пропишите /start для получения актуальной ссылки.</i></b>", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
