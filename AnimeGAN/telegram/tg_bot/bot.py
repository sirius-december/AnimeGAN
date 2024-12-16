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

@db.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message):
    await message.reply_photo(message.photo[-1].file_id)

@db.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    await message.reply_video_note(message.video_note.file_id)

@db.message(aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message):
    await message.reply_video(message.video_note.file_id)

@db.message()
async def echo(message: aiogram.types.Message):
    await message.answer(message.text)

def start_bot():
    asyncio.run(main())