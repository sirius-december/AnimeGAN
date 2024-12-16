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

@db.message(aiogram.filters.Command(("help")))
async def send_common_information(message: aiogram.types.Message):
    await message.answer("Привет!\n\nТы используешь AnimeGAN бота, он создан для стилизации нетяжелых фотографий и коротких видео.\n\n\
Всё, что тебе нужно это просто выбрать файл. Бот проверит, что он подходит по размеру и качеству, сгенерирует новое, уже стилизованное, изображение!")

def start_bot():
    asyncio.run(main())