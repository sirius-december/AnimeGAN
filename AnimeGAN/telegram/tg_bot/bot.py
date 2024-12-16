import asyncio
import dotenv
import aiogram
import os

dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
db = aiogram.Dispatcher()

async def main():
    await db.start_polling(bot)


@db.message(aiogram.filters.Command("start"))
async def send_welcome(message: aiogram.types.Message):
    await message.reply("Welcome!")

@db.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message):
    await message.reply_photo(message.photo[-1].file_id)
    file = await message.bot.get_file(message.photo[-1].file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/telegram/tg_bot/photo/" + str(message.photo[-1].file_id))

@db.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    await message.reply_video_note(message.video_note.file_id)
    file = await message.bot.get_file(message.video_note.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/telegram/tg_bot/video_note/" + str(message.video_note.file_id))

@db.message(aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message):
    await message.reply_video(message.video_note.file_id)
    file = await message.bot.get_file(message.video.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/telegram/tg_bot/video/" + str(message.video.file_id))
@db.message(aiogram.filters.Command("help"))
async def send_common_information(message: aiogram.types.Message):
    await message.answer("Привет!\n\nТы используешь AnimeGAN бота, он создан для стилизации нетяжелых фотографий и коротких видео.\n\n\
Всё, что тебе нужно это просто выбрать файл. Бот проверит, что он подходит по размеру и качеству, сгенерирует новое, уже стилизованное, изображение!")

def make_dir():
    if not os.path.exists(r"AnimeGAN/telegram/tg_bot/photo/"):
        os.mkdir("AnimeGAN/telegram/tg_bot/photo/")
    if not os.path.exists(r"AnimeGAN/telegram/tg_bot/video/"):
        os.mkdir("AnimeGAN/telegram/tg_bot/video/")
    if not os.path.exists(r"AnimeGAN/telegram/tg_bot/video_note/"):
        os.mkdir("AnimeGAN/telegram/tg_bot/video_note/")

def start_bot():
    make_dir()
    asyncio.run(main())