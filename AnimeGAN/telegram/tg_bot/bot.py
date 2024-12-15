import asyncio
import dotenv
import aiogram
import os

dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
db = aiogram.Dispatcher()

async def main():
    await db.start_polling(bot)


@db.message(aiogram.filters.Command(("start")))
async def send_welcome(message: aiogram.types.Message):
    await message.reply("Welcome!")


@db.message()
async def echo(message: aiogram.types.Message):
    await message.answer(message.text)

def start_bot():
    asyncio.run(main())