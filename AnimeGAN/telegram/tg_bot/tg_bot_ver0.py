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
    await message.reply("Welcome bebrik")


if __name__ == "__main__":
    asyncio.run(main())