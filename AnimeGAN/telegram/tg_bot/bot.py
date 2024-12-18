import asyncio
import dotenv
import aiogram
import os
import cv2
from PIL import Image
import io

dotenv.load_dotenv()

bot = aiogram.Bot(os.environ["TOKEN"])
dp = aiogram.Dispatcher()

def imagecheck(img):
    image = Image.open(io.BytesIO(img))
    if(max(image.size())<=1024 and os.path.getsize(img) <= 10*1024*1024+1024):
        return True
    return False
async def main():
    await dp.start_polling(bot)


@dp.message(aiogram.filters.Command("start"))
async def send_welcome(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Информация"),
            aiogram.types.KeyboardButton(text="Начать!")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard = kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите как продолжить"
    )
    await message.answer("Добро пожаловать в AnimeGan!", reply_markup=keyboard)



@dp.message(aiogram.F.text.lower() == "начать!")
async def photo_or_video_choose(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Фотография"),
            aiogram.types.KeyboardButton(text="Видео")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Что будем стилизовать?"
    )
    await message.answer("Для начала выберите, что будем стилизовать", reply_markup=keyboard)



@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message):
    await message.reply_photo(message.photo[-1].file_id)
    img_data = await message.bot.get_file(message.photo[-1].file_id)
    await bot.download_file(img_data.file_path)
    imagecheck(img_data)
'''@dp.message(aiogram.F.content_type == "photo")
async def get_image(message: aiogram.types.Message):
    await message.reply_photo(message.photo[-1].file_id)
    file = await message.bot.get_file(message.photo[-1].file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/photo/" + str(message.photo[-1].file_id))'''

@dp.message(aiogram.F.content_type == "video_note")
async def get_video_note(message: aiogram.types.Message):
    await message.reply_video_note(message.video_note.file_id)
    file = await message.bot.get_file(message.video_note.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/video_note/" + str(message.video_note.file_id))

@dp.message(aiogram.F.content_type == "video")
async def get_video(message: aiogram.types.Message):
    await message.reply_video(message.video.file_id)
    file = await message.bot.get_file(message.video.file_id)
    await bot.download_file(file.file_path, r"AnimeGAN/downloads/video/" + str(message.video.file_id))

@dp.message(aiogram.F.text.lower() == "информация" or aiogram.types.Command("help"))
async def send_common_information(message: aiogram.types.Message):
    kb = [
        [
            aiogram.types.KeyboardButton(text="Как это работает?"),
            aiogram.types.KeyboardButton(text="Начать!")
        ]
    ]
    keyboard = aiogram.types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Как продолжим?"
    )
    await message.answer("Привет!\n\nТы используешь AnimeGAN бота, он создан для стилизации нетяжелых фотографий и коротких видео.\n\n\
Всё, что тебе нужно это просто выбрать файл. Бот проверит, что он подходит по размеру и качеству, сгенерирует новое, уже стилизованное, изображение!",\
        reply_markup=keyboard)



def make_dir():
    if not os.path.exists(r"AnimeGAN/downloads/"):
        os.mkdir("AnimeGAN/downloads")
    if not os.path.exists(r"AnimeGAN/downloads/photo/"):
        os.mkdir("AnimeGAN/downloads/photo/")
    if not os.path.exists(r"AnimeGAN/downloads/video/"):
        os.mkdir("AnimeGAN/downloads/video/")
    if not os.path.exists(r"AnimeGAN/downloads/video_note/"):
        os.mkdir("AnimeGAN/downloads/video_note/")


def start_bot():
    make_dir()
    asyncio.run(main())